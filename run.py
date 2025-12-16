import argparse
import os
from typing import Dict, List, Optional, Set

import requests
from tqdm import tqdm

from config import (
    AI_TERMS,
    ENERGY_TERMS,
    LOG_FILE,
    MAX_RESULTS,
    OUTPUT_CSV,
    OUTPUT_DIR,
)
from src.openalex_api import OpenAlexClient
from src.parser import merge_semantic_scholar, parse_openalex_work
from src.save_csv import CsvWriter
from src.semantic_scholar_api import SemanticScholarClient
from src.utils import (
    ensure_directories,
    load_existing_ids,
    setup_logging,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取 AI+Energy 论文（基于 Concept ID + 关键词）")
    parser.add_argument("--max-results", type=int, default=MAX_RESULTS, help="最多抓取多少条")
    parser.add_argument("--skip-semantic", action="store_true", help="跳过 Semantic Scholar")
    parser.add_argument("--resume", action="store_true", help="断点续爬，从已有 CSV 自动续写")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ensure_directories([OUTPUT_DIR, os.path.dirname(LOG_FILE)])

    logger = setup_logging(LOG_FILE)
    session = requests.Session()

    # 初始化 API Client
    openalex = OpenAlexClient(session=session, logger=logger)
    semantic = None if args.skip_semantic else SemanticScholarClient(session=session, logger=logger)
    csv_writer = CsvWriter(OUTPUT_CSV)

    # -------------------------
    # Resume 功能（断点续写）
    # -------------------------
    start_offset = 0
    seen_ids: Set[str] = set()

    if args.resume and os.path.isfile(OUTPUT_CSV):
        seen_ids = load_existing_ids(OUTPUT_CSV, "paper_openalex_id")
        start_offset = len(seen_ids)
        logger.info(">>> 已检测 CSV，已有 %d 条，将从 offset=%d 续爬", len(seen_ids), start_offset)
    else:
        logger.info(">>> 未启用断点续爬或 CSV 不存在，将从头开始")

    rows_buffer: List[Dict] = []

    progress = tqdm(desc="采集论文", total=args.max_results)
    delivered = 0

    # -------------------------
    #  正确的 iter_works 调用方式
    # -------------------------
    for work in openalex.iter_works(
        AI_TERMS,          # ← 必须传入
        ENERGY_TERMS,      # ← 必须传入
        max_results=args.max_results,
    ):
        oid = work.get("id")

        # 避免写重复
        if oid in seen_ids:
            continue
        seen_ids.add(oid)

        parsed = parse_openalex_work(work)
        if not parsed:
            continue

        # Semantic Scholar 信息（可选）
        semantic_data: Optional[Dict] = None
        if semantic:
            doi = parsed.get("paper_doi")
            if doi:
                semantic_data = semantic.fetch_by_doi(doi)

        record = merge_semantic_scholar(parsed, semantic_data or {})
        rows_buffer.append(record)
        delivered += 1
        progress.update(1)

        # 写缓存
        if len(rows_buffer) >= 1:
            csv_writer.append(rows_buffer)
            rows_buffer = []

        if delivered >= args.max_results:
            break

    progress.close()

    # 写剩余
    if rows_buffer:
        csv_writer.append(rows_buffer)

    logger.info("爬取完成，总计写入 %d 条。", delivered + start_offset)


if __name__ == "__main__":
    main()
