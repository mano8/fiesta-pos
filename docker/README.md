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

- Move to docker certs folder

```bash
cd /opt/fiesta-pos/docker/certs
```

- Generate CA private key

```bash
openssl genrsa -out ca-key.pem 4096

openssl req -x509 -new -nodes -key ca-key.pem -sha256 -days 3650 -out ca.pem -subj "/C=ES/ST=Andalusia/L=Almería/O=Docker_Certs/CN=ca.local"
```

- Generate server certificates

```bash
openssl genrsa -out server-key.pem 2048

openssl req -new -key server-key.pem -out server.csr -config openssl.conf

openssl x509 -req -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 3650 -extensions req_ext -extfile openssl.conf
```

- Generate client certificates

```bash
openssl genrsa -out client-key.pem 2048

openssl req -new -key client-key.pem -out client.csr -subj "/C=ES/ST=Andalusia/L=Almería/O=Traefik/CN=traefik-client"

openssl x509 -req -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out client-cert.pem -days 3650
```

- Configure Docker deamon  (`/etc/docker/daemon.json`)

```json
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://127.0.0.1:2376"],
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
> LISTEN 0      4096       127.0.0.1:2376       0.0.0.0:*    users:(("dockerd",pid=16757,fd=4))

# check tls
# from directory /opt/fiesta-pos/docker/certs
sudo docker --tlsverify --tlscacert=ca.pem --tlscert=client-cert.pem --tlskey=client-key.pem -H tcp://127.0.0.1:2376 version
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