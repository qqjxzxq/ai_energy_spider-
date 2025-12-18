import requests
import time
import csv
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# =========================
# 基本配置
# =========================
BASE_URL = "https://api.openalex.org/works"
PER_PAGE = 200
SLEEP = 0.6
START_YEAR = 1990
END_YEAR = 2025
MAX_PAPERS = 50000

OUTPUT_CSV = "data/ai_energy_papers_full.csv"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("energy_spider")

# =========================
# OpenAlex Concepts
# =========================
ENERGY_CONCEPT_IDS = [
    # "C10558101",    # Smart grid
    # "C188573790",    # Renewable energy
    # "C78600449",     # Wind power
    # "C7817414",      # Energy management
    # "C2780165032"   # Energy consumption 1
    # "C77715397",     #"Electrical load"
    # "C2777103469",   #"Smart city"
    # # "C2776422217",   #"Electric vehicle" 2
    # "C73916439", #"Energy storage"
    # "C541104983", #"Solar energy"
    # "C41291067" #"Photovoltaic system" 3
    
    # "C40675005", #"Hydropower"
    # "C92311004" # "Hydroelectricity" 4
    
    # "C2742236", #"Efficient energy use"
    # "C2776409380" #"Building energy simulation" 5
    
    # "C103742991",#"Air conditioning"
    # "C122346748",  #HVAC 空调暖气. 
    # "C47737302" #"Greenhouse gas" 6
    
    
    #### 超相关     #########
    # "C119599485",      #"Electrical engineering"
    # "C2776422217",   #"Electric vehicle" 
    # "C10558101"    # Smart grid
    
    # "C2779607880", #"Charging station"
    # "C2778324724", #"Electrification"
    # "C555008776" #"Battery (electricity)"
    
    "C163258240", #"Power (physics)"
    "C38864968", #"Grid energy storage"
    "C2776849302", #"Energy market"
    "C2776784348" # "Microgrid"
]

# AI_CONCEPT_IDS = [
#     "C154945302",    # Artificial intelligence
# ]


# =========================
# 工具函数
# =========================

def create_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session


SESSION = create_session()


def build_concept_filter(concept_ids):
    # OR 关系
    joined = "|".join(concept_ids)
    return f"concepts.id:{joined}"


def extract_concept_ids(work):
    """
    从 work 中提取 Concept ID（Cxxxx）
    """
    return {
        c["id"].split("/")[-1]
        for c in work.get("concepts", [])
        if "id" in c
    }


# def is_ai_energy_paper(work):
#     """
#     能源 + AI 双 Concept 命中
#     """
#     concept_ids = extract_concept_ids(work)
#     return (
#         len(concept_ids & set(ENERGY_CONCEPT_IDS)) > 0
#         and len(concept_ids & set(AI_CONCEPT_IDS)) > 0
#     )


# =========================
# 核心爬取逻辑
# =========================
def fetch_energy_works_by_year(year, max_per_year=2000):
    results = []
    cursor = "*"

    energy_filter = build_concept_filter(ENERGY_CONCEPT_IDS)

    while True:
        params = {
            "filter": f"{energy_filter},publication_year:{year}",
            "per-page": PER_PAGE,
            "cursor": cursor,
        }

        r = SESSION.get(BASE_URL, params=params, timeout=30)
        if r.status_code != 200:
            print("ERROR:", r.text)
            break

        data = r.json()
        works = data.get("results", [])
        results.extend(works)

        # ✅ 年内数量限制
        if len(results) >= max_per_year:
            return results[:max_per_year]

        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

        time.sleep(SLEEP)

    return results





# =========================
# CSV 保存
# =========================
def save_csv(works):
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # =========================
        # CSV 表头（完整字段）
        # =========================
        writer.writerow([
            "paper_openalex_id",        # OpenAlex ID
            "paper_doi",                # DOI
            "title",                    # 标题
            "author_list",              # 作者名列表
            "author_id_list",           # 作者ID列表
            "affiliation_list",         # 作者机构
            "publication_year",         # 年份
            "venue",                    # 期刊/会议
            "paper_type",               # Article / Conference / Review
            "cited_by_count",           # 被引次数
            "abstract",                 # 摘要
            "fulltext_url",             # 全文链接
            "open_access_status",       # OA 状态
            "is_oa",                    # 是否 OA
            "referenced_ids_openalex",  # 参考文献ID（引文网络）
            "concepts",                 # Concepts（debug / 备用）
        ])

        for w in works:
            # ===== DOI =====
            doi = w.get("doi")

            # ===== Authors & Affiliations =====
            author_names = []
            author_ids = []
            affiliations = []

            for a in w.get("authorships", []):
                author = a.get("author", {})
                name = author.get("display_name")
                author_names.append(name if isinstance(name, str) else "")

                aid = author.get("id")
                author_ids.append(aid if isinstance(aid, str) else "")


                insts = a.get("institutions", [])
                if insts:
                    affiliations.append(
                        "|".join(
                            i.get("display_name") if isinstance(i.get("display_name"), str) else ""
                            for i in insts
                        )

                    )
                else:
                    affiliations.append("")

            # ===== Abstract =====
            abstract = ""
            inverted = w.get("abstract_inverted_index")
            if inverted:
                tmp = {}
                for word, pos_list in inverted.items():
                    for p in pos_list:
                        tmp[p] = word
                abstract = " ".join(tmp[i] for i in sorted(tmp))

            # ===== OA & Fulltext =====
            oa = w.get("open_access", {})
            fulltext_url = oa.get("oa_url") or \
                w.get("primary_location", {}).get("landing_page_url")

            # ===== Venue =====
            primary_location = w.get("primary_location") or {}
            source = primary_location.get("source") or {}
            venue = source.get("display_name")

            # ===== References =====
            referenced_ids = "|".join(w.get("referenced_works", []))

            # ===== Concepts =====
            concepts = "; ".join(
                c.get("display_name", "") for c in w.get("concepts", [])
            )

            writer.writerow([
                w.get("id"),
                doi,
                w.get("title"),
                ";".join(author_names),
                ";".join(author_ids),
                ";".join(affiliations),
                w.get("publication_year"),
                venue,
                w.get("type"),
                w.get("cited_by_count"),
                abstract,
                fulltext_url,
                oa.get("oa_status"),
                oa.get("is_oa"),
                referenced_ids,
                concepts,
            ])


# =========================
# 主流程
# =========================
def main():
    all_energy = []
    ai_energy = []

    for year in range(START_YEAR, END_YEAR + 1):
        logger.info(f"--- 抓取 {year} 年论文 ---")
        works = fetch_energy_works_by_year(year, max_per_year=2000)
        logger.info(f"{year} 年抓取：{len(works)} 篇")

        all_energy.extend(works)
        time.sleep(2)  # 年份级冷却


        for w in works:
            ai_energy.append(w)
            if len(ai_energy) >= MAX_PAPERS:
                logger.info(">>> 已达到最大论文数量限制")
                save_csv(ai_energy)
                return



    logger.info(f">>> 能源论文总数：{len(all_energy)}")
    # logger.info(f">>> AI + 能源论文总数：{len(ai_energy)}")

    save_csv(ai_energy)
    logger.info(f">>> 已保存至 {OUTPUT_CSV}")


# =========================
# 启动
# =========================
if __name__ == "__main__":
    main()
