# Local Docker Database Setup

This guide explains how to run the project MySQL database locally with Docker so the backend works entirely against containerised data.

## 1. Start the database container

```bash
# from the repository root
docker compose -f docker-compose.mysql.yml up -d
```

The compose file provisions `mysql:8.0` with credentials that match the backend defaults and automatically seeds schema + sample data from `scripts/init_database.sql`. The database is exposed on `localhost:3306`.

## 2. Inspect data in the container

Once the container reports "healthy", browse the data directly:

```bash
# open an interactive MySQL shell inside the container
docker exec -it city_brain_mysql mysql -u City_Brain_user_mysql -pCityBrain@2024 City_Brain_DB

# useful queries
SHOW TABLES;
SELECT * FROM QD_customer LIMIT 10;
SELECT * FROM QD_industry_brain;
```

You can also export data for analysis:

```bash
docker exec city_brain_mysql mysqldump \
  -u City_Brain_user_mysql -pCityBrain@2024 City_Brain_DB > backups/city_brain_dump.sql
```

## 3. Connect the backend

Ensure the backend `.env` (or shell environment) points to the container endpoint:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=City_Brain_user_mysql
DB_PASSWORD=CityBrain@2024
DB_DATABASE=City_Brain_DB
```

After updating the environment variables, restart the FastAPI service. The application will read data directly from the Docker-managed database.

## 4. Troubleshooting

- Check container status: `docker compose -f docker-compose.mysql.yml ps`
- Inspect logs: `docker logs city_brain_mysql`
- Reset data: `docker compose -f docker-compose.mysql.yml down -v` to wipe the volume and re-run `up -d` to reload seed data.

These steps provide a reproducible local environment for iterative design against the real schema.
