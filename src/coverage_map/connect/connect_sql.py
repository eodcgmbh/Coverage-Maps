import os
import json
import psycopg2
from psycopg2 import OperationalError, Error

class Connect:
    def __init__(self, host="localhost", port=5000, database=None, user=None, password=None, query=None):
        self.host = os.environ.get("DB_IP")
        self.port = os.environ.get("DB_PORT")
        self.database = os.environ.get("DB_HOST")
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASSWORD")
        self.conn = None
        self.query = query

    def connect(self):
        """Establishes a connection to the PostgreSQL database."""

        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print(f"Connected to {self.database} on {self.host}:{self.port} successfully.")
        except OperationalError as e:
            print(f"Error connecting to database: {e}")
            self.conn = None
        return self.conn
    
    def build_grid_query(self):
        """
        Builds a grid-based spatial aggregation query.
        """

        query = """
            WITH grid AS (
                SELECT lon, lat,
                    ST_SetSRID(ST_MakeEnvelope(lon, lat, lon + %(resolution)s, lat + %(resolution)s, 4326), 4326) AS cell_geom
                FROM generate_series(%(lonmin)s, %(lonmax)s + %(resolution)s, %(resolution)s) AS lon,
                    generate_series(%(latmin)s, %(latmax)s + %(resolution)s, %(resolution)s) AS lat
            ),
            counts AS (
                SELECT g.cell_geom, COUNT(*) AS cnt
                FROM pgstac.items i
                JOIN grid g ON ST_Intersects(i.geometry, g.cell_geom)
                WHERE i.datetime >= %(from_date)s
                AND (ST_XMax(i.geometry) - ST_XMin(i.geometry)) < 180
                AND i.end_datetime <= %(to_date)s
                AND i.collection = %(collection)s
                GROUP BY g.cell_geom
            )
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(
                    json_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(cell_geom)::json,
                        'properties', json_build_object('count', cnt)
                    ) ORDER BY cnt DESC
                )
            ) AS geojson
            FROM counts;
        """
        
        return query
    
    def get_collection(self):
        """
        Builds a grid-based spatial aggregation query.
        """
        query = """
            SELECT id
            FROM pgstac.collections;            
        """
        
        return query
    
    def get_extent(self):
        """
        Builds a grid-based spatial aggregation query.
        """
        query = """
            SELECT
            ST_XMin(extent) AS minX,
            ST_YMin(extent) AS minY,
            ST_XMax(extent) AS maxX,
            ST_YMax(extent) AS maxY
            FROM (
            SELECT ST_Extent(geometry) AS extent
            FROM pgstac.items
            WHERE datetime >= %(from_date)s
                AND (ST_XMax(geometry) - ST_XMin(geometry)) < 180
                AND end_datetime <= %(to_date)s
                AND collection = %(collection)s
                AND geometry && ST_MakeEnvelope(%(lonmin)s, %(latmin)s, %(lonmax)s, %(latmax)s, 4326)
            ) AS subquery;
            
            """  

        return query      
    
    def calculate_extent_resolution(self, lonmin, latmin, lonmax, latmax):
        """
        Calculates the spatial extent of the requested query.
        """

        lon_diff = lonmax-lonmin
        lat_diff = latmax-latmin

        extent = lon_diff*lat_diff

        if extent <= 360*180 and extent > 90*45:
            resolution = 2
        elif extent <= 90*45 and extent > 45*22.5:
            resolution = 1.5
        elif extent <= 45*22.5 and extent > 22.5*11.5:
            resolution = 1
        elif extent <= 22.5*11.5:
            resolution = 0.5

        return resolution


    
    def send_statement(self, query=None, from_date=None, to_date=None, collection=None, lonmin=None, latmin=None, lonmax=None, latmax=None, resolution=None):
        """
        Executes a SQL query with optional parameters.
        
        Args:
            query (str): SQL query to execute.
        """
        if not self.conn:
            print("No active connection. Please call connect() first.")
            return None

        try:
            with self.conn.cursor() as cur:
                print("Fetching results.")
                collection = self.clean_param(collection)
                from_date = self.clean_param(from_date)
                to_date = self.clean_param(to_date)

                params = {"lonmin":lonmin, "lonmax":lonmax, "latmin":latmin, "latmax": latmin, "latmax": latmax, "from_date": from_date, "to_date": to_date, "collection": collection, "resolution": resolution}

                cur.execute(query, params)
                print(resolution)
                result = cur.fetchall()
                if from_date == "None":
                    print("Results fetched.")
                    return result
                elif resolution == None:
                    return result[0][0], result[0][1], result[0][2], result[0][3]
                else:
                    print("Results fetched.")
                    return result[0][0]

        except Error as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()
            return None

    def close(self):
        """Closes the connection."""
        if self.conn:
            self.conn.close()
            print("Connection closed.")
            self.conn = None
    
    def clean_param(self, param):
        return str(param).strip('"').strip("'")
