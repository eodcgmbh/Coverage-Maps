import os
import json
import psycopg2
from psycopg2 import OperationalError, Error

class Connect:
    def __init__(self, host="localhost", port=5000, database=None, user=None, password=None, query=None):
        self.host = host
        self.port = port
        self.database = os.environ.get("db")
        self.user = os.environ.get("user")
        self.password = os.environ.get("password")
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
                    ST_SetSRID(ST_MakeEnvelope(lon, lat, lon + 1, lat + 1, 4326), 4326) AS cell_geom
                FROM generate_series(%s, %s + 1, 1) AS lon,
                    generate_series(%s, %s + 1, 1) AS lat
            ),
            counts AS (
                SELECT g.cell_geom, COUNT(*) AS cnt
                FROM items i
                JOIN grid g ON ST_Intersects(i.geometry, g.cell_geom)
                WHERE i.datetime >= %s
                AND i.end_datetime <= %s
                AND i.collection = %s
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

    
    def send_statement(self, query, from_date, to_date, collection, lonmin, latmin, lonmax, latmax):
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

                cur.execute(query, (lonmin, lonmax, latmin, latmax, from_date, to_date, collection))
                result = cur.fetchall()
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
