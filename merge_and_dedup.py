import csv
import os
import glob

# =========================
# 路径配置
# =========================
INPUT_DIR = "data/final"
OUTPUT_CSV = "all.csv"

# =========================
# 去重 key 构造
# =========================
def build_dedup_key(row):
    """
    优先级：
    1. DOI
    2. OpenAlex ID
    3. title + year
    """
    if row.get("paper_doi"):
        return f"doi::{row['paper_doi'].lower()}"

    if row.get("paper_openalex_id"):
        return f"oa::{row['paper_openalex_id']}"

    return f"title_year::{row.get('title','').lower()}::{row.get('publication_year','')}"


# =========================
# 主流程
# =========================
def main():
    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))

    if not csv_files:
        raise RuntimeError(f"{INPUT_DIR} 文件夹下没有 CSV 文件")

    print(f"📂 发现 {len(csv_files)} 个 CSV 文件")

    all_rows = []
    seen_keys = set()

    fieldnames = None
    total_rows = 0
    kept_rows = 0

    for csv_file in csv_files:
        print(f"➡️ 读取 {csv_file}")

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if fieldnames is None:
                fieldnames = reader.fieldnames

            for row in reader:
                total_rows += 1
                key = build_dedup_key(row)

                if key in seen_keys:
                    continue

                seen_keys.add(key)
                all_rows.append(row)
                kept_rows += 1

    # =========================
    # 写出结果
    # =========================
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print("\n====== 合并完成 ======")
    print(f"原始论文条数: {total_rows}")
    print(f"去重后论文条数: {kept_rows}")
    print(f"输出文件: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
