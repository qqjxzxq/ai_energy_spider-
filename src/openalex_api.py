import logging
from typing import Dict, Iterator, Optional

import requests

from config import (
    MAX_RESULTS,
    OPENALEX_BASE,
    PER_PAGE,
    SLEEP_BETWEEN_REQ,
)

from src.utils import sleep_with_jitter


class OpenAlexClient:
    def __init__(self, session: Optional[requests.Session] = None, logger: Optional[logging.Logger] = None) -> None:
        self.session = session or requests.Session()
        self.logger = logger or logging.getLogger("ai_energy_spider")

    # --------------------------
    #  构造基本过滤
    # --------------------------
    def _build_filters(self, year: int) -> str:
        filters = [
            f"publication_year:{year}",
            "language:en",
            "type:journal-article",
        ]
        return ",".join(filters)

    # --------------------------
    #  构造 search 查询（摘要 / 关键词 / 标题）
    # --------------------------
    def _build_search_queries(self, ai_terms, energy_terms):
        combos = []
        for ai in ai_terms:
            for en in energy_terms:
                # abstract.search 可以精准命中摘要
                combos.append(f'(abstract.search:"{ai}" AND abstract.search:"{en}")')
                # search 匹配标题 + 摘要 + 关键词
                combos.append(f'(search:"{ai}" AND search:"{en}")')

        # 按长度拆成多个 search
        queries = []
        chunk = []
        char_count = 0

        for combo in combos:
            if char_count + len(combo) + len(chunk) > 900 and chunk:
                queries.append(" OR ".join(chunk))
                chunk = []
                char_count = 0
            chunk.append(combo)
            char_count += len(combo)

        if chunk:
            queries.append(" OR ".join(chunk))

        return queries

    # --------------------------
    #   主迭代器：按年份抓
    # --------------------------
    def iter_works(
        self,
        ai_terms,
        energy_terms,
        per_page: int = PER_PAGE,
        max_results: int = MAX_RESULTS,
        start_year: int = 2017,
        end_year: int = 2025,
    ) -> Iterator[Dict]:

        years = list(range(start_year, end_year + 1))
        per_year_target = max_results // len(years)

        delivered = 0

        params = {
            "per-page": per_page,
            "sort": "publication_year:desc",
        }

        for year in years:
            self.logger.info(f"--- 正在抓取 {year} 年的数据 ---")
            params["filter"] = self._build_filters(year)

            year_count = 0
            page = 1

            search_chunks = self._build_search_queries(ai_terms, energy_terms)

            for search_query in search_chunks:
                params["search"] = search_query

                while year_count < per_year_target and delivered < max_results:
                    params["page"] = page

                    resp = self.session.get(OPENALEX_BASE, params=params, timeout=30)
                    if resp.status_code != 200:
                        self.logger.warning(f"OpenAlex 请求失败 {resp.status_code} {resp.text[:200]}")
                        break

                    data = resp.json()
                    results = data.get("results", [])
                    if not results:
                        break

                    for item in results:
                        yield item
                        year_count += 1
                        delivered += 1

                        if year_count >= per_year_target or delivered >= max_results:
                            break

                    page += 1
                    sleep_with_jitter(SLEEP_BETWEEN_REQ)

                if delivered >= max_results:
                    break

            self.logger.info(f"{year} 年完成，共写入 {year_count} 条")

        self.logger.info(f">>> 采集完成，共写入 {delivered} 条")
