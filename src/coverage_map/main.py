from src.coverage_map.connect.calculate_raster import calculate_raster
from src.coverage_map.connect.connect_sql import Connect

import os



def main(from_date, to_date, collection, lonmin, latmin, lonmax, latmax):
    conn = Connect()
    #calculate_raster(from_date="2023", to_date="2024", collection=None)

    print(collection)
    query = conn.build_grid_query()

    conn.connect()
    result = conn.send_statement(query, from_date, to_date, collection, lonmin, latmin, lonmax, latmax)

    return result


if __name__ == "__main__":
    main(database=db_host, user=db_user, password=db_pass, from_date="2020-01-01", to_date="2025-01-01", collection="Peru", lonmin = -180, latmin = -90, lonmax = 180, latmax = 90)

    # http://127.0.0.1:4000/coverage?database=%22floodevents%22&user=%22postgres%22&password=%22password%22&from_date=%222020-01-01%22&to_date=%222025-01-01%22&collection=%22Peru%22