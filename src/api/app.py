from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import subprocess
import json, tempfile
from src.coverage_map.main import main, get_coll

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

@app.get("/collection")
async def collection():
    result = get_coll()
    return result

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
        #map { height: 90vh; width: 100vw;}
        #controls {
            margin: 10px;
        }
        label, input, select {
            margin: 5px;
        }

        .colorbar {
            background: white;
            padding: 10px;
            border-radius: 6px;
            font-size: 12px;
        }

        .colorbar .gradient {
            width: 150px;
            height: 15px;
            background: linear-gradient(to right, hsl(60,100%,50%), hsl(0,100%,30%));
            border: 1px solid #999;
            margin-bottom: 5px;
        }

        .colorbar .labels {
            display: flex;
            justify-content: space-between;
        }

        </style>
    </head>
    <body>

    <div id="controls">
        <form id="paramForm" onsubmit="event.preventDefault(); submitForm();">
            <label for="from_date">From Date:</label>
            <input type="date" id="from_date" name="from_date" required />
            
            <label for="to_date">To Date:</label>
            <input type="date" id="to_date" name="to_date" required />
            
            <label for="collection">Collection:</label>
            <select id="collection" name="collection" required>
                <option value="" disabled selected>Loading collections...</option>
            </select>
            <br/>
            <label for="lonmin">Lon Min:</label>
            <input type="number" id="lonmin" name="lonmin" value="-180" step="0.5" />
            
            <label for="latmin">Lat Min:</label>
            <input type="number" id="latmin" name="latmin" value="-90" step="0.5" />
            
            <label for="lonmax">Lon Max:</label>
            <input type="number" id="lonmax" name="lonmax" value="180" step="0.5" />
            
            <label for="latmax">Lat Max:</label>
            <input type="number" id="latmax" name="latmax" value="90" step="0.5" />
            
            <br/>
            <button type="submit">Load Coverage</button>
        </form>
    </div>

    <div id="map"></div>

    <script>
        const map = L.map('map').setView([0, 0], 2);
        map.setView([30, 0], 3); 
        let colorbarControl = null;
        let minVal = 0;
        let maxVal = 1;



        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
        }).addTo(map);

        let geojsonLayer = null;

        function getColor(value) {
            const ratio = (value - minVal) / (maxVal - minVal); 
            
            const hue = 55 - ratio * 55;    
            const saturation = 50;     
            const lightness = 75 - ratio * 25;  

            return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
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

        function addColorbar(minVal, maxVal) {
            if (colorbarControl) {
                map.removeControl(colorbarControl);
            }

            colorbarControl = L.control({ position: 'bottomright' });

            colorbarControl.onAdd = function () {
                const div = L.DomUtil.create('div', 'colorbar');
                div.innerHTML = `
                    <div class="gradient"></div>
                    <div class="labels">
                        <span>${minVal}</span>
                        <span>${maxVal}</span>
                    </div>
                `;
                return div;
            };

            colorbarControl.addTo(map);
        }



        window.onload = function() {
            fetch('/collection')
                .then(response => {
                    if (!response.ok) throw new Error('Failed to load collections');
                    return response.json();
                })
                .then(collections => {
                    const select = document.getElementById('collection');
                    select.innerHTML = ''; // clear loading option
                    
                    if (collections.length === 0) {
                        const opt = document.createElement('option');
                        opt.value = '';
                        opt.textContent = 'No collections found';
                        opt.disabled = true;
                        select.appendChild(opt);
                        return;
                    }

                    const placeholder = document.createElement('option');
                    placeholder.value = '';
                    placeholder.textContent = 'Select a collection';
                    placeholder.disabled = true;
                    placeholder.selected = true;
                    select.appendChild(placeholder);

                    collections.forEach(c => {
                        const option = document.createElement('option');
                        option.value = c;
                        option.textContent = c;
                        select.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error(err);
                    const select = document.getElementById('collection');
                    select.innerHTML = '';
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'Error loading collections';
                    option.disabled = true;
                    select.appendChild(option);
                });
        };

        // Submit handler
        function submitForm() {
            const form = document.getElementById('paramForm');
            const formData = new FormData(form);
            const params = new URLSearchParams();

            for (const [key, value] of formData.entries()) {
                if(value) params.append(key, value);
            }

            fetch('/coverage?' + params.toString())
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    if (geojsonLayer) {
                        map.removeLayer(geojsonLayer);
                    }

                    // Dynamic min/max
                    const counts = data.features.map(f => f.properties.count);
                    minVal = Math.min(...counts);
                    maxVal = Math.max(...counts);

                    if (window.colorbarControl) {
                        map.removeControl(window.colorbarControl);
                    }
                    window.colorbarControl = addColorbar(minVal, maxVal);

                    geojsonLayer = L.geoJSON(data, {
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

        }
    </script>

    </body>
    </html>

    """

