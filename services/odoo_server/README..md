# Odoo Server services

## 1. Auto configure ttyACM0 port for PP6800 printer

By default ttyACM0 is configure with baud od 9600.
This Service configure ttyACM0 with correct parameters for PP6800 printer

### Install and activate

- Add service to `systemd`

```bash
sudo cp services/odoo_server/serial-config.service /etc/systemd/system/serial-config.service
```

- Enable it

```bash
sudo systemctl enable serial-config.service
sudo systemctl start serial-config.service
```

- Check status

```bash
sudo systemctl status serial-config.service
```

## 2. Auto run docker compose containers

- Add service to `systemd`

```bash
sudo cp services/odoo_server/odoo-pos.service /etc/systemd/system/odoo-pos.service
```


- Enable it

```bash
sudo systemctl enable odoo-pos.service
sudo systemctl start odoo-pos.service
```

- Check status

```bash
sudo systemctl status odoo-pos.service
```

## 3. Containers logs

### Docker-Level Log Rotation

### Host-Side Log Rotation with logrotate

- create `/etc/logrotate.d/docker-containers`

```bash
sudo nano /etc/logrotate.d/docker-containers
```

- And add above content

```text
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  missingok
  copytruncate
  size 100M
  dateext
  notifempty
}
```
