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
from app.services.ingestion import run_moa_daily_ingestion


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取农业农村部每日批发价格简报并入库。")
    parser.add_argument("--pages", type=int, default=3, help="抓取列表页数量，默认 3 页。")
    parser.add_argument("--max-articles", type=int, default=20, help="最多处理的文章数，默认 20。")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        scanned_articles, inserted_articles, inserted_metrics = run_moa_daily_ingestion(
            db,
            pages=max(args.pages, 1),
            max_articles=max(args.max_articles, 1),
        )
    print(
        f"fetch_moa_daily: scanned={scanned_articles} inserted_articles={inserted_articles} inserted_metrics={inserted_metrics}"
    )


if __name__ == "__main__":
    main()
