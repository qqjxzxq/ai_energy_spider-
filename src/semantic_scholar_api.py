import logging
from typing import Dict, Optional

import requests

from config import SEMANTIC_SCHOLAR_BASE, SLEEP_BETWEEN_REQ
from src.utils import sleep_with_jitter


FIELDS = ",".join(
    [
        "paperId",
        "externalIds",
        "title",
        "year",
        "venue",
        "referenceCount",
        "citationCount",
        "isOpenAccess",
        "openAccessPdf",
        "authors.authorId",
        "authors.name",
        "references.paperId",
        "references.externalIds",
    ]
)


class SemanticScholarClient:
    def __init__(
        self,
        session: Optional[requests.Session] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.session = session or requests.Session()
        self.logger = logger or logging.getLogger("ai_energy_spider")

    def fetch_by_doi(self, doi: str) -> Optional[Dict]:
        if not doi:
            return None
        url = f"{SEMANTIC_SCHOLAR_BASE}/DOI:{doi}"
        params = {"fields": FIELDS}
        resp = self.session.get(url, params=params, timeout=30)
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            self.logger.debug(
                "Semantic Scholar 请求失败 %s %s", resp.status_code, resp.text[:200]
            )
            return None
        sleep_with_jitter(SLEEP_BETWEEN_REQ)
        return resp.json()