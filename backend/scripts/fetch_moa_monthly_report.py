from __future__ import annotations

import argparse
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.ingestion import run_moa_monthly_report_sync


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取农业农村部农产品供需形势月报并归档。")
    parser.add_argument("--limit", type=int, default=12, help="最多下载的月报数量，默认 12。")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        scanned_reports, downloaded_reports = run_moa_monthly_report_sync(db, limit=max(args.limit, 1))
    print(f"fetch_moa_monthly_report: scanned={scanned_reports} downloaded={downloaded_reports}")


if __name__ == "__main__":
    main()
