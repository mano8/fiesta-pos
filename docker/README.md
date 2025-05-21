# Docker configuration

## Active docker `userns-remap`

- Prepare subUID y subGID

```bash
grep -E '^(root|dockremap)' /etc/subuid /etc/subgid
```

- Read actual subUID y subGID Ranges

```bash
cat /etc/subuid
> myUser:100000:65536
```

- configure `/etc/docker/daemon.json`

```bash
sudo nano /etc/docker/daemon.json
```

  - Set above content

  ```json
  {
    "userns-remap": "default",
    "experimental": false,
    "storage-driver": "overlay2"
  }
  ```

  * global log driver: `"log-driver": "journald"`
  * userns-remap: `default`, docker will create user and ranges

- Restart docker deamon

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
getent passwd dockremap
> dockremap:x:997:985::/home/dockremap:/bin/sh
id dockremap
> uid=997(dockremap) gid=985(dockremap) grupos=985(dockremap)
```

## Set up mTls for docker demon sock

```bash
export DOCKER_HOST_IP=10.254.254.1
```

### Generate Certificates

- Generate all needed certificates for docker deamon API

```bash
sudo DOCKER_HOST_IP="$DOCKER_HOST_IP" /opt/fiesta-pos/docker/scripts/manage_docker_certs.sh generate
```

- To remove all those certificates

```bash
sudo /opt/fiesta-pos/docker/scripts/manage_docker_certs.sh remove
```

### Setup dummy interface for docker deamon api

#### With Network manager

- Ensure `NetworkManager` is active

```bash
systemctl is-enabled NetworkManager
> enabled
systemctl is-active  NetworkManager
> active
```

- Set Dummy interface with `nmcli`

```bash
sudo nmcli connection add  type dummy ifname docker0-mgmt con-name docker0-mgmt ip4 "$DOCKER_HOST_IP"/32 autoconnect yes
```

- Active interface

```bash
sudo nmcli connection up docker0-mgmt
```

- Control

```bash
ip addr show docker0-mgmt
nmcli device status | grep docker0-mgmt
```

### Configure Docker deamon  (`/etc/docker/daemon.json`)

```json
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://10.254.254.1:2376"],
  "tls": true,
  "tlsverify": true,
  "tlscacert": "/etc/docker/certs/ca.pem",
  "tlscert": "/etc/docker/certs/server-cert.pem",
  "tlskey": "/etc/docker/certs/server-key.pem",
  "storage-driver": "overlay2",
  "userns-remap": "default",
  "experimental": false
}
```

- Override docker systemd

```bash
sudo mkdir /etc/systemd/system/docker.service.d
sudo nano /etc/systemd/system/docker.service.d/override.conf
```

- Set content

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --containerd=/run/containerd/containerd.sock
```

- Reload docker

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo docker info | grep -E 'Storage Driver|Userns|Experimental'
```

- Check

```bash
sudo systemctl status docker

sudo ss -tlnp | grep dockerd
> LISTEN 0      4096       10.254.254.1:2376       0.0.0.0:*    users:(("dockerd",pid=16757,fd=4))

# check tls
# from directory /opt/fiesta-pos/docker/certs
sudo docker --tlsverify --tlscacert=/opt/fiesta-pos/docker/certs/ca.pem --tlscert=/opt/fiesta-pos/docker/certs/client-cert.pem --tlskey=/opt/fiesta-pos/docker/certs/client-key.pem -H tcp://10.254.254.1:2376 version
```

### Debug

- Systemd status

```bash
sudo systemctl restart docker
```

- Get basic journalctl logs

```bash
sudo journalctl -xeu docker.service
```

- Get last 5 min of journalctl logs

```bash
sudo journalctl -u docker.service --since "5 minutes ago"
```

- Debug docker

```bash
sudo dockerd --debug
```