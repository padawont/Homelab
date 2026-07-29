---
sources:
  - "https://pterodactyl.io/panel/1.0/webserver_configuration.html"
  - "https://pterodactyl.io/project/introduction.html"
last_audit_date: 2026-07-29
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
status: draft
date: 2026-07-29
---

# Webserver Configuration

## Overview

This note covers production-ready web server configurations for the Pterodactyl Panel (PHP-based frontend). **Wings** (the Go daemon) runs on port **8080** and is **never proxied through the web server** — it communicates with the Panel directly via its own HTTP API.

All `server_name` and `ssl_certificate` entries must be replaced with real values.

---

## Nginx — Production SSL

```nginx
server {
    listen 443 ssl http2;
    server_name panel.example.com;

    root /var/www/pterodactyl/public;
    index index.php;

    access_log /var/log/nginx/pterodactyl-panel.access.log;
    error_log  /var/log/nginx/pterodactyl-panel.error.log;

    ssl_certificate     /etc/letsencrypt/live/panel.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/panel.example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;

    add_header X-Content-Type-Options    "nosniff" always;
    add_header X-XSS-Protection          "1; mode=block" always;
    add_header X-Frame-Options           "SAMEORIGIN" always;
    add_header Referrer-Policy           "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy   "frame-ancestors 'self'" always;

    client_max_body_size 100m;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param PATH_INFO       $fastcgi_path_info;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PHP_VALUE "upload_max_filesize = 100M \n post_max_size=100M";
        fastcgi_read_timeout 300;
        fastcgi_send_timeout 300;
        fastcgi_connect_timeout 60;
        fastcgi_buffers 16 16k;
        fastcgi_buffer_size 32k;
    }

    location ~ /\.ht {
        deny all;
    }
}

server {
    listen 80;
    server_name panel.example.com;
    return 301 https://$host$request_uri;
}
```

---

## Nginx — Non-SSL (Internal / LAN Only)

```nginx
server {
    listen 80;
    server_name panel.internal.example.com;

    root /var/www/pterodactyl/public;
    index index.php;

    client_max_body_size 100m;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param PATH_INFO       $fastcgi_path_info;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_read_timeout 300;
        fastcgi_send_timeout 300;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

---

## Apache — SSL Alternative

Enable required modules:
```bash
a2enmod rewrite proxy_fcgi setenvif headers ssl http2
```

```apache
<VirtualHost *:443>
    ServerName panel.example.com
    DocumentRoot /var/www/pterodactyl/public
    Protocols h2 http/1.1

    SSLEngine on
    SSLCertificateFile     /etc/letsencrypt/live/panel.example.com/fullchain.pem
    SSLCertificateKeyFile  /etc/letsencrypt/live/panel.example.com/privkey.pem
    SSLProtocol             all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite          ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder     on

    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection       "1; mode=block"
    Header always set X-Frame-Options        "SAMEORIGIN"

    <Directory /var/www/pterodactyl/public>
        AllowOverride All
        Require all granted
    </Directory>

    <FilesMatch \.php$>
        SetHandler "proxy:unix:/var/run/php/php8.3-fpm.sock|fcgi://localhost"
    </FilesMatch>
</VirtualHost>

<VirtualHost *:80>
    ServerName panel.example.com
    Redirect permanent / https://panel.example.com/
</VirtualHost>
```

---

## Caddy — Auto SSL

Caddy manages Let's Encrypt certificates automatically.

```caddyfile
panel.example.com {
    root * /var/www/pterodactyl/public
    php_fastcgi unix//var/run/php/php8.3-fpm.sock

    header {
        X-Content-Type-Options "nosniff"
        X-XSS-Protection       "1; mode=block"
        X-Frame-Options        "SAMEORIGIN"
        Referrer-Policy        "no-referrer-when-downgrade"
    }

    request_body max_size 100MB
    encode gzip
}
```

---

## SSL Setup via Certbot

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d panel.example.com
certbot renew --dry-run
```

### Auto-Renewal Cron

```cron
0 3 * * * /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
```

For Cloudflare proxied domains, use acme.sh with DNS challenge instead.

---

## Security Headers Reference

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME-type sniffing |
| `X-XSS-Protection` | `1; mode=block` | Enable browser XSS filter |
| `X-Frame-Options` | `SAMEORIGIN` | Block clickjacking |
| `Referrer-Policy` | `no-referrer-when-downgrade` | Control referrer header |
| `Content-Security-Policy` | `frame-ancestors 'self'` | Mitigate clickjacking |

## Performance Tuning

| Setting | Recommendation |
|---------|---------------|
| `client_max_body_size` | `100m` — allows large egg installer / backup uploads |
| `fastcgi_read_timeout` | `300` — accommodates long-running PHP processes |
| `fastcgi_send_timeout` | `300` — large request bodies |
| `fastcgi_buffers` | `16 16k` — reduces disk I/O for large responses |
| `fastcgi_buffer_size` | `32k` — prevents "upstream sent too big header" errors |

**OPcache settings (php.ini):**
```ini
opcache.enable=1
opcache.memory_consumption=128
opcache.max_accelerated_files=10000
opcache.revalidate_freq=60
```

---

## Key Reminders

- **Wings runs on port 8080** — do not proxy it through the web server
- **Panel root** is `/var/www/pterodactyl/public` (not the project root)
- **PHP socket** must match the installed PHP version (e.g., `php8.3-fpm.sock`)
- **Queue worker** is required for sending emails and executing server actions
- **File ownership** must be `www-data:www-data` on Debian/Ubuntu
