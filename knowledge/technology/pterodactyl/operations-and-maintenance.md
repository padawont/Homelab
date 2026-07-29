---
sources:
  - "https://pterodactyl.io/project/introduction.html"
  - "https://github.com/pterodactyl/panel"
  - "https://github.com/pterodactyl/wings"
last_audit_date: 2026-07-29
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
status: draft
date: 2026-07-29
---

# Operations & Maintenance

## Backup Strategy

| Component | What to Back Up | Notes |
|-----------|----------------|-------|
| **Panel Database** | Dump via `mysqldump` | Regular dumps; store off-server |
| **Panel .env** | `APP_KEY` value | **Critical** — without it, all encrypted data (passwords, 2FA secrets) is permanently lost. Store in a password manager or offline vault. |
| **Panel Files** | `/var/www/pterodactyl` | Config, themes, extensions; `vendor/` is regeneratable via `composer install` |
| **Wings Server Data** | `/var/lib/pterodactyl/volumes` | All game server data (worlds, plugins, configurations) |
| **Wings Config** | `/etc/pterodactyl/config.yml` | Node configuration, TLS certs |

Use a rotation scheme (7 daily, 4 weekly, 3 monthly) and test restores periodically.

---

## Updating the Panel

```bash
cd /var/www/pterodactyl
php artisan down
curl -L https://github.com/pterodactyl/panel/releases/latest/download/panel.tar.gz | tar -xzv
chmod -R 755 storage/* bootstrap/cache
composer install --no-dev --optimize-autoloader
php artisan view:clear
php artisan config:clear
php artisan migrate --seed --force
chown -R www-data:www-data /var/www/pterodactyl/*
php artisan queue:restart
php artisan up
```

1. Put the Panel into maintenance mode (`php artisan down`).
2. Replace files with the new release.
3. Run `composer install` to update PHP dependencies.
4. Run database migrations.
5. Restart the queue worker to pick up new code.
6. Bring the Panel back up (`php artisan up`).

---

## Updating Wings

```bash
systemctl stop wings
curl -L -o /usr/local/bin/wings "https://github.com/pterodactyl/wings/releases/latest/download/wings_linux_$([[ "$(uname -m)" == "x86_64" ]] && echo "amd64" || echo "arm64")"
chmod u+x /usr/local/bin/wings
systemctl start wings
```

Running game server containers are **not** affected by a Wings restart.

---

## Monitoring

| Component | What to Watch | How |
|-----------|--------------|-----|
| **Queue Worker** | Running? | `systemctl status pteroq` |
| **Wings** | Service health | `systemctl status wings`, `journalctl -u wings -f` |
| **Panel Logs** | Laravel errors | `storage/logs/laravel-*.log` |
| **Webserver Logs** | 4xx/5xx rates | `tail -f /var/log/nginx/error.log` |
| **Redis** | Memory, evictions | `redis-cli info stats` |
| **MariaDB/MySQL** | Slow queries | `SHOW FULL PROCESSLIST` |
| **Docker** | Daemon health | `docker info`, `docker system df` |
| **Disk** | Volume storage | `df -h /var/lib/pterodactyl/volumes` |

---

## Troubleshooting

### 500 / Blank-Page Errors on Panel
1. Check `storage/logs/laravel-*.log` for the actual error.
2. Permissions: `storage/` and `bootstrap/cache/` must be writable by the web server user.
3. Missing or incorrect `APP_KEY`: run `php artisan key:generate` if lost (breaks existing encrypted data).
4. Run `php artisan config:clear` and `php artisan view:clear`.

### Wings Offline in Panel
1. `systemctl status wings` — is the service running?
2. `journalctl -u wings -l --no-pager | tail -50` — look for connection errors.
3. Verify `config.yml` token, Panel URL, and SSL settings match.
4. Firewall: ensure ports 8080 (Wings API) and 2022 (SFTP) are open.
5. Run `wings --debug` to start in foreground with verbose logs.

### WebSocket / Console Failures
- Panel and Wings **must** use the same protocol (both HTTPS or both HTTP).
- SSL certificates must be valid and trusted.
- Browser extensions (AdBlock) can block WebSocket connections — test in incognito.
- CORS: Wings `config.yml` must include the Panel origin in `allowed_origins`.

### Invalid MAC / HMAC Errors
- Almost always a **mismatched `APP_KEY`** — restore from backup.

### Schedules Not Running
```bash
php artisan queue:restart
php artisan config:clear
php artisan cache:clear
```
- Verify the `pteroq` queue worker is running.
- Check crontab has `* * * * * php /var/www/pterodactyl/artisan schedule:run >> /dev/null 2>&1`.
- Check timezone alignment: system, Panel (.env), and Wings (config.yml).

### Containers Have No Internet
- Default Wings DNS is `1.1.1.1` / `1.0.0.1`. If the host blocks Cloudflare, change to the host's DNS in `/etc/pterodactyl/config.yml`.
- Find host DNS with: `nmcli -g ip4.dns dev show`, `resolvectl status`, or `/etc/resolv.conf`.

---

## Security

| Area | Action |
|------|--------|
| **APP_KEY** | Backup offline. Rotate only if compromised (breaks all encrypted data). |
| **HTTPS** | Enforce TLS everywhere — Panel, Wings API, SFTP. |
| **Security Headers** | Add `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy` in nginx/Caddy. |
| **reCAPTCHA** | Enable on login and registration in Panel settings. |
| **2FA** | Enforce for admin accounts. |
| **Docker Isolation** | Never use `--privileged`. Pin CPU/memory via Wings UI. |
| **PID Limits** | Default 512 per container — prevents fork bombs. |
| **SELinux** | Keep enforcing. Add policies for Wings/Pterodactyl paths if needed. |

---

## Performance

| Tuning | Where | Recommendation |
|--------|-------|----------------|
| **OPcache** | `php.ini` | `opcache.memory_consumption=128`, `opcache.max_accelerated_files=10000` |
| **Queue Worker** | Supervisor | Multiple `pteroq` processes: `numprocs=4` or more |
| **Redis** | `redis.conf` | `maxmemory` to 75% of RAM, `maxmemory-policy allkeys-lru` |
| **DB Indexing** | MariaDB/MySQL | Run `ANALYZE TABLE` on large tables |
| **FastCGI Buffers** | nginx | `fastcgi_buffers 8 16k; fastcgi_buffer_size 32k;` |
| **Upload Limits** | nginx + PHP | `client_max_body_size 100m`, `upload_max_filesize=100M`, `post_max_size=100M` |
| **Wings Throttle** | `config.yml` | Adjust `throttles` per-server limits |

---

## SSL Renewal

### certbot (Nginx/Apache)
```bash
certbot renew --quiet --post-hook "systemctl reload nginx && systemctl restart wings"
```

### acme.sh (Cloudflare DNS Challenge)
```bash
export CF_Token="..."
export CF_Zone_ID="..."
acme.sh --issue --dns dns_cf -d panel.example.com -d node.example.com
systemctl restart wings
```

Use DNS challenges when ports 80/443 are not available (e.g., Cloudflare proxied domains).

---

## Queue Worker Maintenance

```bash
supervisorctl restart pteroq
# After every Panel deployment:
php artisan queue:restart
```

Monitor the queue worker for memory leaks — restart periodically. Watch `supervisorctl status` and set up `startretries=5` in the Supervisor config.
