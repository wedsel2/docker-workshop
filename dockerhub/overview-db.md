# Docker Workshop DB

PostgreSQL image preloaded for the Docker Workshop movie reviews project.

## Image

- `wedsel2/docker-workshop-db`

## Environment Variables

Use these settings when running the container:

```yaml
POSTGRES_DB: moviereviews
POSTGRES_USER: appuser
POSTGRES_PASSWORD: apppass
```

## Quick Start

```powershell
docker network create workshop-net
docker run -d --name db --network workshop-net -e POSTGRES_DB=moviereviews -e POSTGRES_USER=appuser -e POSTGRES_PASSWORD=apppass wedsel2/docker-workshop-db
```

This container is intended to be used by the workshop web app image on the same Docker network.

