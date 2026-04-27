#!/usr/bin/env python3
"""
Fetch ~10k smart contract creation records from BigQuery's public Ethereum dataset
while staying under the free-tier scan quota (<= 1 GB scanned) by restricting
to a small date range and selecting only a few columns.

Usage:
  python scripts/fetch_bigquery_sample.py \
      --start-date 2020-01-01 \
      --end-date 2020-01-02 \
      --limit 10000 \
      --output data/datasets/bigquery_contracts.csv

Notes:
- Requires Google Cloud credentials (ADC or set GOOGLE_APPLICATION_CREDENTIALS).
- The query restricts by DATE(block_timestamp) so BigQuery will only scan the
  relevant partition(s); keep the date window small to stay well under 1 GB.
"""
import argparse
import sys
import os
from pathlib import Path
from google.cloud import bigquery
import pandas as pd


DEFAULT_OUTPUT = "data/datasets/bigquery_contracts.csv"


def build_query(start_date: str, end_date: str, limit: int) -> str:
    # Select only essential columns and limit results
    query = f"""
    SELECT
      receipt_contract_address AS contract_address,
      from_address,
      value,
      block_number,
      block_timestamp
    FROM
      `bigquery-public-data.crypto_ethereum.transactions`
    WHERE
      receipt_contract_address IS NOT NULL
      AND DATE(block_timestamp) BETWEEN '{start_date}' AND '{end_date}'
    LIMIT {limit}
    """
    return query


def run_query(query: str) -> bigquery.job.QueryJob:
    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(use_query_cache=True)
    query_job = client.query(query, job_config=job_config)
    return query_job


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch contract creation samples from BigQuery")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=10000, help="Maximum rows to return")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output CSV path")

    args = parser.parse_args(argv)

    query = build_query(args.start_date, args.end_date, args.limit)
    print("Running BigQuery: fetching contract creations for", args.start_date, "->", args.end_date)

    try:
        job = run_query(query)
        result = job.result()  # waits for completion

        bytes_processed = getattr(job, "total_bytes_processed", None)
        if bytes_processed is not None:
            print(f"Bytes processed: {bytes_processed:,}")
            GB = 1_000_000_000
            if bytes_processed > GB:
                print("WARNING: Query scanned more than 1 GB. Consider narrowing the date range or reducing columns.")

        df = result.to_dataframe()
        if df.empty:
          print("No results returned for the given date range. Try expanding the date window slightly.")
          return 1

        # Ensure output directory exists (save into repo's data folder)
        out_path = args.output
        out_dir = Path(out_path).parent
        if not out_dir.exists():
          print(f"Creating output directory: {out_dir}")
          out_dir.mkdir(parents=True, exist_ok=True)

        df.to_csv(out_path, index=False)
        print(f"Saved {len(df)} rows to {out_path}")
        return 0

    except Exception as e:
        print("BigQuery query failed:", e)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
