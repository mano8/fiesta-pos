# Offline Mode

When you need to run the entire **Fiesta POS** stack with **no Internet** (e.g. in an air-gapped environment), you must:

1. **Vendor all Docker images** locally (Traefik, Postgres, Odoo, Python-fat)
2. **Cache all Python wheels** in `hw_proxy/wheelhouse/` and `hw_proxy/wheelhouse_dev/`
3. **Configure** Compose and Dockerfiles to install **only** from those local artifacts

---

## Repository Layout

```
/opt/fiesta-pos/
├── docker_offline/             ← offline-prep artifacts & Makefiles
│   ├── Makefile.prepare        ← pull → build → save (tarballs)
│   ├── Makefile.update         ← save → load → (optional compose up)
│   ├── Makefile.wheels         ← generate wheelhouse dirs
│   ├── traefik_v3.4.0.tar
│   ├── postgres_13.21-alpine3.20.tar
│   ├── odoo_18.0.tar
│   └── python-3.11-fat.tar
└── hw_proxy/
    ├── wheelhouse/             ← prod wheels (in `.gitignore`)
    ├── wheelhouse_dev/         ← dev wheels (in `.gitignore`)
    └── hw_proxy/
        ├── requirements-docker.txt
        ├── requirements-docker-dev.txt
        ├── Dockerfile.fat          ← Vendor Docker hw_proxy base image
        ├── Dockerfile.offline.dev  ← builds using local wheelhouses (dev)
        └── Dockerfile.offline      ← builds using local wheelhouses (prod)
```

---

## 1. Prepare offline artifacts (online workstation)

1. **Docker images**

   ```bash
   cd /opt/fiesta-pos/docker_offline
   make -f Makefile.prepare
   ```

   * Pulls Traefik, Postgres, Odoo, builds `python-3.11-fat`, and saves them to `*.tar`

2. **Python wheels**

   ```bash
   cd /opt/fiesta-pos/docker_offline
   make -f Makefile.wheels prod     # fills wheelhouse/
   make -f Makefile.wheels dev      # fills wheelhouse_dev/
   ```

---

## 2. Load & run offline (air-gapped host)

Copy the entire `/opt/fiesta-pos/` directory (including `docker_offline/*.tar` and both `wheelhouse*`) to the target host, then:

```bash
cd /opt/fiesta-pos/docker_offline
make -f Makefile.update
```

`Makefile.update` does:

1. Loads each `*.tar` via `docker load -i ...`

---

## 3. Manual fallback commands

### Docker images

```bash
cd /opt/fiesta-pos/docker_offline

docker pull traefik:v3.4.0
docker pull postgres:13.21-alpine3.20
docker pull odoo:18.0

docker build -f ../hw_proxy/FatDockerfile -t python-3.11-fat:latest ../hw_proxy

docker save traefik:v3.4.0   -o traefik_v3.4.0.tar
docker save postgres:13.21-alpine3.20 \
     -o postgres_13.21-alpine3.20.tar
docker save odoo:18.0         -o odoo_18.0.tar
docker save python-3.11-fat:latest \
     -o python-3.11-fat.tar

# On offline host:
docker load -i traefik_v3.4.0.tar
... (repeat for others)
```

### Python wheels for `hw_proxy`

```bash
cd /opt/fiesta-pos/hw_proxy

# Production wheels:
pip download --dest wheelhouse     -r requirements-docker.txt

# Development wheels:
pip download --dest wheelhouse_dev -r requirements-docker-dev.txt
```

---

With this setup, **every** piece (OS packages, images, Python libs) lives in your repo and can be built, loaded, and run **without** touching the Internet.
