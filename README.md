# Docker Workshop - Minimal Run Instructions

- `wbouwmans/docker-workshop-db` - PostgreSQL image with the movie reviews dataset.
- `wbouwmans/docker-workshop-webapp` - Flask web app image that reads from PostgreSQL.

Use these PostgreSQL settings for the `db` container:

```yaml
POSTGRES_DB: moviereviews
POSTGRES_USER: appuser
POSTGRES_PASSWORD: apppass
```

Run the containers with these two commands:

```powershell
docker network create movie-net
docker run -d --name db --network movie-net -e POSTGRES_DB=moviereviews -e POSTGRES_USER=appuser -e POSTGRES_PASSWORD=apppass wbouwmans/docker-workshop-db
docker run -d --name web --network movie-net -e DB_HOST=db -p 8000:8000 wbouwmans/docker-workshop-webapp
```

Open `http://localhost:8000`.

