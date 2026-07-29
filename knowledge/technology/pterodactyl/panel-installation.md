---
sources:
  - "https://pterodactyl.io/panel/1.0/getting_started.html"
  - "https://github.com/pterodactyl/panel"
last_audit_date: 2026-07-29
related_configs:
  - "configs-and-adr/node-main/pterodactyl/"
status: draft
date: 2026-07-29
---

# Panel Installation (Ubuntu 22.04)

## System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Ubuntu 22.04 LTS |
| PHP | 8.3 (8.1/8.2 supported) |
| Database | MariaDB 10.11+ or MySQL 8.0+ |
| Web Server | Nginx |
| Cache / Queue | Redis 6+ |
| Composer | 2.x |

### PHP 8.3 Extensions

`php8.3-cli`, `php8.3-common`, `php8.3-gd`, `php8.3-mysql`, `php8.3-mbstring`, `php8.3-bcmath`, `php8.3-xml`, `php8.3-fpm`, `php8.3-curl`, `php8.3-zip`, `php8.3-intl`, `php8.3-redis`

---

## Step-by-Step Installation

### 1. System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common curl wget git unzip nginx mariadb-server redis-server
sudo add-apt-repository -y ppa:ondrej/php
sudo apt update
sudo apt install -y php8.3 php8.3-cli php8.3-common php8.3-gd php8.3-mysql php8.3-mbstring php8.3-bcmath php8.3-xml php8.3-fpm php8.3-curl php8.3-zip php8.3-intl php8.3-redis
curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer
```

### 2. Create Directory & Download Panel

```bash
sudo mkdir -p /var/www/pterodactyl
cd /var/www/pterodactyl
sudo chown -R www-data:www-data /var/www/pterodactyl
sudo -u www-data curl -Lo panel.tar.gz https://github.com/pterodactyl/panel/releases/latest/download/panel.tar.gz
sudo -u www-data tar -xzf panel.tar.gz
sudo -u www-data rm panel.tar.gz
```

### 3. Configure MariaDB

```bash
sudo mysql -u root
```

```sql
CREATE DATABASE pterodactyl;
CREATE USER 'pterodactyl'@'127.0.0.1' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON pterodactyl.* TO 'pterodactyl'@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT
```

### 4. Configure .env & Generate APP_KEY (CRITICAL)

```bash
sudo -u www-data cp /var/www/pterodactyl/.env.example /var/www/pterodactyl/.env
sudo -u www-data php /var/www/pterodactyl/artisan key:generate --force
sudo -u www-data php /var/www/pterodactyl/artisan key:generate --show
```

**Save the APP_KEY output somewhere secure (password manager, offline backup). Without it, all encrypted data is permanently unrecoverable.**

Edit `/var/www/pterodactyl/.env`:
```env
APP_ENV=production
APP_DEBUG=false
APP_URL=http://192.168.111.52

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=pterodactyl
DB_USERNAME=pterodactyl
DB_PASSWORD=your_strong_password
```

### 5. Run Migrations & Create Admin

```bash
sudo -u www-data php /var/www/pterodactyl/artisan migrate --seed --force
sudo -u www-data php /var/www/pterodactyl/artisan p:user:make
```

Follow the prompts to create the admin user (email, username, password).

### 6. Set Permissions & Configure Nginx

```bash
sudo chown -R www-data:www-data /var/www/pterodactyl/storage /var/www/pterodactyl/bootstrap/cache
sudo chmod -R 755 /var/www/pterodactyl/storage /var/www/pterodactyl/bootstrap/cache
```

Create `/etc/nginx/sites-available/pterodactyl.conf` (see [webserver-configuration.md](webserver-configuration.md) for the full config).

```bash
sudo ln -s /etc/nginx/sites-available/pterodactyl.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

---

## Queue Worker Configuration

### systemd Service

Create `/etc/systemd/system/pteroq.service`:

```ini
[Unit]
Description=Pterodactyl Queue Worker
After=redis-server.service mariadb.service nginx.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/pterodactyl
ExecStart=/usr/bin/php /var/www/pterodactyl/artisan queue:work --queue=high,standard,low --sleep=3 --tries=3
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pteroq.service
```

### Cron Job

```bash
sudo crontab -u www-data -e
```

Add:
```
* * * * * php /var/www/pterodactyl/artisan schedule:run >> /dev/null 2>&1
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Blank page / 502 | PHP-FPM not running | `systemctl status php8.3-fpm`, check socket path |
| DB connection error | Wrong credentials in .env | Test with `mysql -u pterodactyl -p -h 127.0.0.1 pterodactyl` |
| APP_KEY lost | .env not backed up | Restore from backup. Without it, data is unrecoverable. |
| Migrations fail | Cached config conflict | `php artisan optimize:clear` then `migrate --force -v` |
| Permissions error | Wrong ownership | `chown -R www-data:www-data storage/ bootstrap/cache/` |
| Queue not working | Worker not running | `systemctl status pteroq`, check `journalctl -u pteroq` |
| Port 80/443 conflict | Apache running | `systemctl stop apache2 && systemctl disable apache2` |
