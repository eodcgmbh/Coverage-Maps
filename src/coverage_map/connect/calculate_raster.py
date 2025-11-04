

class calculate_raster:
    def __init__(self, lonmin = -180, latmin = -90, lonmax = 180, latmax = 180, from_date = None, to_date = None, collection = None):
        self.lonmin = lonmin
        self.latmin = latmin
        self.lonmax = lonmax
        self.latmax = latmax
        self.from_date = from_date
        self.to_date = to_date
        self.collection = collection

    def sql_query(self):

        query = f"""
        WITH grid AS (
            SELECT
                lon,
                lat,
                ST_SetSRID(
                    ST_MakeEnvelope(
                        lon, lat, lon + 5, lat + 5, 4326
                    ), 4326
                ) AS cell_geom
            FROM generate_series({self.lonmin}, {self.lonmax} + 5, 5) AS lon,
                generate_series({self.latmin}, {self.latmax} + 5, 5) AS lat
        )
        SELECT
            ST_AsGeoJSON(g.cell_geom) AS geometry,
            COUNT(*) AS count
        FROM
            pgstac.items i
        JOIN
            grid g
            ON ST_Intersects(i.geometry, g.cell_geom)
        WHERE
            i.datetime >= {self.from_date}
            AND i.datetime <= {self.to_date}
            AND i.collection = {self.collection}
        GROUP BY
            i.collection,
            g.cell_geom
        ORDER BY
            count DESC;
            """
        return query

