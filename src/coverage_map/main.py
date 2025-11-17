from src.coverage_map.connect.calculate_raster import calculate_raster
from src.coverage_map.connect.connect_sql import Connect

import os
import time


def get_res(from_date, to_date, collection, lonmin, latmin, lonmax, latmax):
    conn = Connect()
    lonmin, latmin, lonmax, latmax = conn.get_extent
    resolution = conn.calculate_extent_resolution(lonmin, latmin, lonmax, latmax)
    get_collection = conn.get_collection()
    conn.connect()
    result_collection = conn.send_statement(get_collection)
    return result_collection


def get_coll():
    conn = Connect()
    get_collection = conn.get_collection()
    conn.connect()
    result_collection = conn.send_statement(get_collection)
    return result_collection



def main(from_date, to_date, collection, lonmin, latmin, lonmax, latmax):
    conn = Connect()

    # --- measure Connect() initialization ---
    t0 = time.perf_counter()
    # Connect() already executed above
    t1 = time.perf_counter()
    print(f"Connect() initialization took {t1 - t0:.6f} seconds")

    # --- get_extent() ---
    t0 = time.perf_counter()
    getextent = conn.get_extent()
    t1 = time.perf_counter()
    print(f"conn.get_extent() took {t1 - t0:.6f} seconds")

    # --- connect() ---
    t0 = time.perf_counter()
    conn.connect()
    t1 = time.perf_counter()
    print(f"conn.connect() took {t1 - t0:.6f} seconds")

    # --- send_statement(getextent) ---
    t0 = time.perf_counter()
    lonmin, latmin, lonmax, latmax = conn.send_statement(
        getextent, from_date, to_date, collection,
        lonmin, latmin, lonmax, latmax
    )
    t1 = time.perf_counter()
    print(f"conn.send_statement(getextent) took {t1 - t0:.6f} seconds")

    # --- calculate_extent_resolution() ---
    t0 = time.perf_counter()
    resolution = conn.calculate_extent_resolution(lonmin, latmin, lonmax, latmax)
    t1 = time.perf_counter()
    print(f"conn.calculate_extent_resolution() took {t1 - t0:.6f} seconds")

    # --- build_grid_query() ---
    t0 = time.perf_counter()
    query = conn.build_grid_query()
    t1 = time.perf_counter()
    print(f"conn.build_grid_query() took {t1 - t0:.6f} seconds")

    # --- send_statement(query) ---
    t0 = time.perf_counter()
    result = conn.send_statement(
        query, from_date, to_date, collection,
        lonmin, latmin, lonmax, latmax, resolution
    )
    t1 = time.perf_counter()
    print(f"conn.send_statement(query) took {t1 - t0:.6f} seconds")

    return result


if __name__ == "__main__":
    main(database=db_host, user=db_user, password=db_pass, from_date="2020-01-01", to_date="2025-01-01", collection="Peru", lonmin = -180, latmin = -90, lonmax = 180, latmax = 90)

    # http://127.0.0.1:4000/coverage?database=%22floodevents%22&user=%22postgres%22&password=%22password%22&from_date=%222020-01-01%22&to_date=%222025-01-01%22&collection=%22Peru%22