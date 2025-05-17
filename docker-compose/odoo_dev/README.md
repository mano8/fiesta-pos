# Odoo Docker compose

## Set up .env file

Copy .env.example.txt to `.env`

```bash
cp ./env.example.txt ./.env
```

Next you should set needed all values in `.env` file.

## Build containers

First build containers from docker-compose

```bash
sudo docker compose build
```

### Init data base in oddo container

Then run `fiesta_odoo` container with `bash` console.

```bash
sudo docker compose run fiesta_odoo bash
```

Then, in container console, run odoo CLI command to init data base.

```bash
odoo --init base --without-demo --database "${DB_DATABASE}" --stop-after-init --db_host=fiesta_db --db_user "${DB_USER}" --db_password "${DB_PASSWORD}"

# On export end's up
exit
```

Now we can run containers, normally with Odoo db initialyzed.

```bash
sudo docker compose run
```
