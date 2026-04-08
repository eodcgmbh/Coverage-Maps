# STAC Coverage Maps

A FastAPI application for generating coverage maps from PGSTAC (PostgreSQL STAC API). This tool allows users to query and visualize spatio-temporal coverage data from STAC collections stored in a PostgreSQL database with the PGSTAC extension.

## Features

- Query coverage data by date range, collection, and bounding box
- Generate GeoJSON coverage maps
- Interactive web-based map viewer
- RESTful API with automatic documentation
- Docker containerization for easy deployment

## Prerequisites

- Python 3.12+
- PostgreSQL with PGSTAC extension
- Docker (for containerized deployment)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd coverage-map
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Running Locally

1. Set up environment variables (see Docker section for details).

2. Run the application:
   ```bash
   poetry run uvicorn src.api.app:app --host 0.0.0.0 --port 4000
   ```

3. Access the API at http://localhost:4000

## Running with Docker

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

- API root: http://localhost:4000
- Swagger UI: http://localhost:4000/docs
- Coverage Map Viewer: http://localhost:4000/coverage/map

## API Endpoints

- `GET /` - Health check
- `GET /collection` - List available collections
- `GET /coverage` - Generate coverage map (parameters: from_date, to_date, collection, lonmin, latmin, lonmax, latmax, download)
- `GET /coverage/map` - Interactive map viewer

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add license information here]