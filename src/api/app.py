from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import subprocess
import json, tempfile
from src.coverage_map.main import main

app = FastAPI()

@app.get("/coverage")
async def coverage(
    from_date: str,
    to_date: str,
    collection: str,
    lonmin: float = -180,
    latmin: float = -90,
    lonmax: float = 180,
    latmax: float = 90,
    download: bool = False,
):
    
    result = main(from_date, to_date, collection, lonmin, latmin, lonmax, latmax)

    if download:
        tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")  # <-- note mode="w"
        json.dump(result, tmp)
        tmp.close()
        return FileResponse(tmp.name, filename="coverage.json")

    return result

@app.get("/")
def root():
    return {"message": "Server is running! Try /coverage"}

@app.get("/coverage/map", response_class=HTMLResponse)
async def map_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coverage Map</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <link
        rel="stylesheet"
        href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

        <style>
        #map { height: 100vh; width: 100vw; }
        </style>
    </head>
    <body>
        <div id="map"></div>

    <script>
        const map = L.map('map').setView([0, 0], 2);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);

        // Simple color scale based on count value
        function getColor(count) {
            return count > 50 ? '#800026' :
                count > 20 ? '#BD0026' :
                count > 10 ? '#E31A1C' :
                count > 5  ? '#FC4E2A' :
                count > 0  ? '#FD8D3C' :
                                '#FFEDA0';
        }

        function style(feature) {
            return {
                fillColor: getColor(feature.properties.count),
                weight: 1,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.7
            };
        }

        const params = new URLSearchParams(window.location.search);

        fetch('/coverage?' + params.toString())
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                const geojsonLayer = L.geoJSON(data, {
                    style: style,
                    onEachFeature: function(feature, layer) {
                        if (feature.properties && feature.properties.count !== undefined) {
                            layer.bindPopup('Count: ' + feature.properties.count);
                        }
                    }
                }).addTo(map);

                if (geojsonLayer.getBounds().isValid()) {
                    map.fitBounds(geojsonLayer.getBounds());
                }
            })
            .catch(error => {
                console.error('Error fetching GeoJSON:', error);
                alert('Failed to load coverage data.');
            });
    </script>

    </body>
    </html>
    """
