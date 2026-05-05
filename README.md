# Docker Workshop - Minimal Run Instructions

- `wedsel2/docker-workshop-db` - PostgreSQL image with the movie reviews dataset.
- `wedsel2/docker-workshop-webapp` - Flask web app image that reads from PostgreSQL.

Use these PostgreSQL settings for the `db` container:

```yaml
POSTGRES_DB: moviereviews
POSTGRES_USER: appuser
POSTGRES_PASSWORD: apppass
```

Run the containers with these two commands:

```powershell
docker run -d --name db -e POSTGRES_DB=moviereviews -e POSTGRES_USER=appuser -e POSTGRES_PASSWORD=apppass wedsel2/docker-workshop-db
docker run -d --name web -e DB_HOST=db -p 8000:8000 wedsel2/docker-workshop-webapp
```

Open `http://localhost:8000`.
