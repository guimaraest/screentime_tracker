import csv
import argparse
from pathlib import Path
from screen_time import get_last_sessions

EXPORT_LIMIT = 100
OUTPUT_FILE = Path("last_sessions.csv")


def export_csv(output_path):
    sessions = get_last_sessions(EXPORT_LIMIT)

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
        description="Export last 100 app sessions to CSV"
    )
    parser.add_argument(
        "--out",
        default=OUTPUT_FILE,
        type=Path,
        help="Output CSV file path",
    )

    args = parser.parse_args()
    export_csv(args.out)
    print(f"Exported last {EXPORT_LIMIT} sessions to {args.out}")


if __name__ == "__main__":
    main()
