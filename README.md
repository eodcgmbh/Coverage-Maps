# STAC Coverage Maps

FastAPI application for generating coverage maps from PGSTAC.

## Running the application

The application is intended to be run **via Docker only**.

### 1. Environment variables

Create a shell file containing the required environment variables, for example:

```bash
# creds.sh
export DB_HOST=...
export DB_USER=...
export DB_PASSWORD=...
export DB_IP=...
export DB_PORT=...
export API_BASE_URL=...
```

### 2. Build the Docker image

From the project root, build the Docker image:

```bash
docker build -t stac-coverage-maps .
```

### 3. Run the container

Run the container and pass the environment variables:

```bash
docker run --env-file creds.sh -p 4000:4000 stac-coverage-maps
```

### 4. Access the API

Once the container is running, the API will be available at:

API root: http://localhost:4000

Swagger UI: http://localhost:4000/docs

Coverage Map Viewer: http://localhost:4000/coverage/map