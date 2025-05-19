# Odoo Docker compose

## Set up .env file

Copy .env.example.txt to `.env`

```bash
cp ./env.example.txt ./.env
nano .env
```

Next you should set needed all values in `.env` file.

## Set up Oddo config file

Add same data as `.env` file for db connection.

```bash
nano ./odoo/config/odoo.conf
```

## On linux: Set Correct owners for docker volumes

You must set volume files owner accordingelly with container user id.

- Get current user id in Odoo docker container

```bash
sudo docker run --rm odoo:18.0 id odoo
# Usually outputs: uid=100(odoo) gid=101(odoo) groups=101(odoo)
```

- Change volumes directory owners

```bash
sudo chown -R 100:101 ./odoo
```

## Build containers

First build containers from docker-compose

```bash
sudo docker compose up --build --remove-orphans
```

### Init data base in oddo container

Then run `fiesta_odoo` container with `bash` console.

```bash
sudo docker compose run fiesta_odoo bash
```

Then, in container console, run odoo CLI command to init data base.

```bash
odoo --init base --database DB_DATABASE --stop-after-init --db_host=fiesta_db --db_user DB_USER --db_password DB_PASSWORD  --without-demo=True

# On export end's up
exit
```

Now we can run containers, normally with Odoo db initialyzed.

```bash
sudo docker compose up --build --remove-orphans
```
