# Docker Workshop - Minimal Run Instructions

- `wedsel2/docker-workshop-db` - PostgreSQL image with the movie reviews dataset.
- `wedsel2/docker-workshop-webapp` - Flask web app image that reads from PostgreSQL.

Use these PostgreSQL settings for the `db` container:

```yaml
POSTGRES_DB: moviereviews
POSTGRES_USER: appuser
POSTGRES_PASSWORD: apppass
```

Create a shared network and run the containers:

```powershell
docker network create workshop-net
docker run -d --name db --network workshop-net -e POSTGRES_DB=moviereviews -e POSTGRES_USER=appuser -e POSTGRES_PASSWORD=apppass wedsel2/docker-workshop-db
docker run -d --name web --network workshop-net -e DB_HOST=db -p 8000:8000 wedsel2/docker-workshop-webapp
```

Open `http://localhost:8000`.

## Development

Build the latest local images before running containers:

```powershell
docker build -f Dockerfile.db -t wedsel2/docker-workshop-db .
docker build -f Dockerfile.web -t wedsel2/docker-workshop-webapp .
```