---
status: draft
service: pterodactyl
target: node-main (pterodactyl VM)
related_knowledge:
  - knowledge/technology/pterodactyl/panel-installation.md
  - knowledge/technology/pterodactyl/wings-daemon.md
  - knowledge/technology/pterodactyl/webserver-configuration.md
  - knowledge/technology/pterodactyl/homelab-overview.md
related_configs:
  - configs-and-adr/adr/0004-pterodactyl-game-server.md
  - configs-and-adr/node-main/pterodactyl/
  - configs-and-adr/node-main/vm/harvester-config.yaml
---

# Deploy Pterodactyl VM

Procedure to provision a Harvester VM on node-main and install Pterodactyl Panel + Wings on Ubuntu Server 22.04 LTS.

## Prerequisites

- Harvester HCI v1.8 running on node-main (192.168.111.51) — see ADR 0003
- Ubuntu Server 22.04 LTS cloud image uploaded to Harvester
- Static IP block: 192.168.111.52/24 reserved for the Pterodactyl VM
- VM resources available: 4 vCPU, 6 GB RAM, 50 GB disk
- DNS A record (optional) for pterodactyl.homelab.local pointing to 192.168.111.52
- SSH key pair for the VM

## Steps

### 1. Create the Harvester VM

1. In Harvester UI → Virtual Machines → Create
2. Set:
   - Name: `pterodactyl`
   - vCPU: 4
   - Memory: 6 GiB
   - Image: Ubuntu 22.04 LTS cloud image
   - Disk: 50 GiB (Longhorn, thin-provisioned)
   - Network: Management Network (default bridge, flat VLAN)
3. Under Advanced Options → Cloud Config, paste:

```yaml
#cloud-config
hostname: pterodactyl
users:
  - name: runicengines
    ssh_authorized_keys:
      - "ssh-ed25519 AAA... CHANGE-ME"
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: sudo
ssh_pwauth: false
packages:
  - qemu-guest-agent
runcmd:
  - systemctl enable --now qemu-guest-agent
```

4. Create the VM and start it

### 2. Configure Static IP

SSH into the VM and set a static IP via Netplan:

```bash
ssh runicengines@192.168.111.52
sudo nano /etc/netplan/00-installer-config.yaml
```

```yaml
network:
  ethernets:
    ens192:
      addresses:
        - 192.168.111.52/24
      gateway4: 192.168.111.1
      nameservers:
        addresses:
          - 192.168.111.1
      dhcp-identifier: mac
  version: 2
```

```bash
sudo netplan apply
```

### 3. Install System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common curl wget git unzip nginx mariadb-server redis-server
sudo add-apt-repository -y ppa:ondrej/php
sudo apt update
sudo apt install -y php8.3 php8.3-cli php8.3-common php8.3-gd php8.3-mysql php8.3-mbstring php8.3-bcmath php8.3-xml php8.3-fpm php8.3-curl php8.3-zip php8.3-intl php8.3-redis
curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer
```

### 4. Install Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes to take effect.

### 5. Configure Database

```bash
sudo mysql -u root
```

```sql
CREATE DATABASE pterodactyl;
CREATE USER 'pterodactyl'@'127.0.0.1' IDENTIFIED BY 'CHANGE-ME-STRONG-PASSWORD';
GRANT ALL PRIVILEGES ON pterodactyl.* TO 'pterodactyl'@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT
```

### 6. Install Pterodactyl Panel

```bash
sudo mkdir -p /var/www/pterodactyl
cd /var/www/pterodactyl
sudo chown -R www-data:www-data .
sudo -u www-data curl -Lo panel.tar.gz https://github.com/pterodactyl/panel/releases/latest/download/panel.tar.gz
sudo -u www-data tar -xzf panel.tar.gz
sudo -u www-data rm panel.tar.gz
sudo -u www-data cp .env.example .env
sudo -u www-data php artisan key:generate --force
```

Edit `/var/www/pterodactyl/.env`:
```env
APP_ENV=production
APP_DEBUG=false
APP_URL=https://192.168.111.52
DB_DATABASE=pterodactyl
DB_USERNAME=pterodactyl
DB_PASSWORD=CHANGE-ME-STRONG-PASSWORD
```

**Save the APP_KEY output to a password manager. Without it, all encrypted data is unrecoverable.**

```bash
sudo -u www-data php artisan migrate --seed --force
sudo -u www-data php artisan p:user:make
```

### 7. Configure Nginx

Create `/etc/nginx/sites-available/pterodactyl.conf` (use the SSL config from `knowledge/technology/pterodactyl/webserver-configuration.md`), then:

```bash
sudo ln -s /etc/nginx/sites-available/pterodactyl.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

### 8. Set Up Queue Worker

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
sudo crontab -u www-data -e
```

Add: `* * * * * php /var/www/pterodactyl/artisan schedule:run >> /dev/null 2>&1`

### 9. Install Wings

```bash
sudo mkdir -p /etc/pterodactyl
sudo curl -L -o /usr/local/bin/wings "https://github.com/pterodactyl/wings/releases/latest/download/wings_linux_amd64"
sudo chmod +x /usr/local/bin/wings
```

### 10. Configure Wings

1. In the Panel UI: Admin → Nodes → Create Node
2. Set:
   - Name: `node-main-pterodactyl`
   - Domain: `192.168.111.52` (or `127.0.0.1` for localhost)
   - Port: `8080`
   - TLS: Off (localhost communication)
   - Behind Proxy: No
3. Set the node's resource limits to match the VM: 6144 MB memory, 50 GB disk, 400% CPU
4. Copy the auto-generated `config.yml` from the Configuration tab
5. Paste the config into `/etc/pterodactyl/config.yml` on the VM

**Modify the Wings config to bind API to localhost:**

```yaml
api:
  host: 127.0.0.1
  port: 8080
  ssl:
    enabled: false

system:
  sftp:
    bind: 0.0.0.0:2022
```

Create and start the Wings systemd service:

```bash
sudo tee /etc/systemd/system/wings.service << 'EOF'
[Unit]
Description=Pterodactyl Wings Daemon
After=docker.service
Requires=docker.service

[Service]
User=root
WorkingDirectory=/etc/pterodactyl
LimitNOFILE=4096
ExecStart=/usr/local/bin/wings
Restart=on-failure
RestartSec=5
StartLimitInterval=180
StartLimitBurst=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now wings
```

### 11. Configure Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw allow 2022/tcp
sudo ufw allow 25565/tcp  # Minecraft Java
sudo ufw allow 19132/udp  # Minecraft Bedrock
sudo ufw deny 8080/tcp     # Wings API — localhost only
sudo ufw --force enable
```

### 12. Set Up SSL

```bash
# For Let's Encrypt (requires DNS A record):
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d pterodactyl.homelab.local

# Or for self-signed (internal use only):
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/pterodactyl-selfsigned.key \
  -out /etc/ssl/certs/pterodactyl-selfsigned.crt \
  -subj "/CN=192.168.111.52"
```

## Verification Checklist

- [ ] Panel accessible at `https://192.168.111.52` (or `https://pterodactyl.homelab.local`)
- [ ] Admin user can log in
- [ ] Queue worker running: `systemctl status pteroq`
- [ ] Cron job active: `crontab -u www-data -l`
- [ ] Wings running: `systemctl status wings`
- [ ] Wings shows green/online in Panel Admin → Nodes
- [ ] Panel can create a server from an egg (e.g., Minecraft Paper)
- [ ] Server starts, is reachable on its game port

## Rollback

### Remove Pterodactyl Completely

```bash
# Stop services
sudo systemctl stop wings pteroq nginx php8.3-fpm mariadb redis-server
sudo systemctl disable wings pteroq nginx php8.3-fpm mariadb redis-server

# Remove panel files
sudo rm -rf /var/www/pterodactyl

# Remove Wings
sudo rm /usr/local/bin/wings
sudo rm -rf /etc/pterodactyl
sudo rm -rf /var/lib/pterodactyl

# Remove Docker containers and images
docker rm -f $(docker ps -aq) 2>/dev/null
docker system prune -a -f

# Remove database
sudo mysql -u root -e "DROP DATABASE pterodactyl; DROP USER 'pterodactyl'@'127.0.0.1';"

# Remove systemd units
sudo rm /etc/systemd/system/pteroq.service /etc/systemd/system/wings.service
sudo systemctl daemon-reload

# Remove nginx config
sudo rm /etc/nginx/sites-available/pterodactyl.conf
sudo rm /etc/nginx/sites-enabled/pterodactyl.conf
sudo systemctl restart nginx

# Reset firewall
sudo ufw --force disable
sudo ufw --force reset
```

### Harvester VM Rollback

Delete the VM and recreate from Harvester snapshot:

1. Harvester UI → Virtual Machines → pterodactyl → Snapshots
2. Select the last known-good snapshot
3. Click Restore
4. Start the VM
