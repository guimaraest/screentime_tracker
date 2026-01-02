import csv
import argparse
from pathlib import Path

from db import get_last_sessions
from constants import *

DEFAULT_LIMIT = 100
DEFAULT_OUTPUT = Path("last_sessions.csv")


def export_csv(output_path, limit):
    sessions = get_last_sessions(limit)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "app", "start_ts", "end_ts", "duration"])

        for session_id, app, start_ts, end_ts in sessions:
            duration = (
                end_ts - start_ts
                if end_ts is not None
                else ""
            )

            writer.writerow(
                [session_id, app, start_ts, end_ts, duration]
            )


def main():
    parser = argparse.ArgumentParser(
        description="Export recent app sessions to CSV"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Number of sessions to export (default: {DEFAULT_LIMIT})",
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output CSV file path",
    )

    args = parser.parse_args()

    export_csv(args.out, args.limit)

    print(f"Exported last {args.limit} sessions to {args.out}")


if __name__ == "__main__":
    main()
