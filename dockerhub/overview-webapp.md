# Docker Workshop Web App

Flask web application image for the Docker Workshop.  
Reads movie reviews data from PostgreSQL.

## Image

- `wedsel2/docker-workshop-webapp`

## Dependency

Run this image with:

- a PostgreSQL container named `db`
- both containers on the same Docker network
- `DB_HOST=db`

## Quick Start

```powershell
docker network create workshop-net
docker run -d --name db --network workshop-net -e POSTGRES_DB=moviereviews -e POSTGRES_USER=appuser -e POSTGRES_PASSWORD=apppass wedsel2/docker-workshop-db
docker run -d --name web --network workshop-net -e DB_HOST=db -p 8000:8000 wedsel2/docker-workshop-webapp
```

Open: `http://localhost:8000`

