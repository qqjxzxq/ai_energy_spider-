from typing import Dict, List, Tuple

from src.utils import inverted_index_to_text


def _parse_authors(authorships: List[Dict]) -> Tuple[str, str, str]:
    names: List[str] = []
    ids: List[str] = []
    affiliations: List[str] = []

    for author in authorships or []:
        if not author:
            continue
        author_obj = author.get("author") or {}
        names.append(author_obj.get("display_name") or "")
        ids.append(author_obj.get("orcid") or author_obj.get("id") or "")
        insts = author.get("institutions") or []
        inst_names = [
            inst.get("display_name")
            for inst in insts
            if isinstance(inst, dict) and inst.get("display_name")
        ]
        affiliations.append(";".join(inst_names))
    return ";".join(names), ";".join(ids), ";".join(affiliations)


def parse_openalex_work(record: Dict) -> Dict:
    author_list, author_id_list, affiliation_list = _parse_authors(
        record.get("authorships", [])
    )

    host_venue = record.get("host_venue") or {}
    primary_location = record.get("primary_location") or {}
    referenced_works = record.get("referenced_works") or []
    authorships = record.get("authorships") or []

    # 安全防御：任何 None 列表都不处理
    if any(author is None for author in authorships) or any(ref is None for ref in referenced_works):
        return {}

    # 修复点：source 可能是 None
    source = primary_location.get("source") or {}

    venue_name = (
        host_venue.get("display_name")
        or source.get("display_name")   # <-- 不再报错
        or ""
    )

    oa = record.get("open_access") or {}
    oa_location = record.get("best_oa_location") or record.get("primary_location") or {}

    return {
        "paper_openalex_id": record.get("id"),
        "paper_doi": record.get("doi", ""),
        "title": record.get("title") or record.get("display_name", ""),
        "author_list": author_list,
        "author_id_list": author_id_list,
        "affiliation_list": affiliation_list,
        "publication_year": record.get("publication_year"),
        "venue": venue_name,
        "referenced_ids_openalex": ";".join(record.get("referenced_works") or []),
        "cited_by_count": record.get("cited_by_count", 0),
        "abstract": inverted_index_to_text(record.get("abstract_inverted_index")),
        "fulltext_url": oa_location.get("landing_page_url")
            or oa_location.get("pdf_url")
            or "",
        "paper_type": record.get("type") or "",
        "open_access_status": oa.get("oa_status") or "",
        "is_oa": oa.get("is_oa"),
    }


def merge_semantic_scholar(record: Dict, semantic_data: Dict) -> Dict:
    """合并 Semantic Scholar 数据字段。"""
    if not semantic_data:
        record.setdefault("paper_semantic_scholar_id", "")
        record.setdefault("referenced_ids_semantic", "")
        return record

    record["paper_semantic_scholar_id"] = semantic_data.get("paperId", "")
    references = semantic_data.get("references") or []
    ref_ids = []
    for ref in references:
        if not ref:
            continue
        external = ref.get("externalIds") or {}
        ref_ids.append(ref.get("paperId") or external.get("DOI", ""))
    record["referenced_ids_semantic"] = ";".join(filter(None, ref_ids))
    if not record.get("author_id_list"):
        authors = semantic_data.get("authors") or []
        author_ids: List[str] = []
        for author in authors:
            if not author:
                continue
            author_ids.append(author.get("authorId") or "")
        record["author_id_list"] = ";".join(filter(None, author_ids))
    return record