import csv
import re

# =========================
# 文件路径
# =========================
INPUT_CSV = "data.csv"
OUTPUT_CSV = "data_cleaned.csv"

# =========================
# DOI 校验函数
# =========================
def is_valid_doi(doi):
    if not doi:
        return False

    doi = doi.strip().lower()

    # 常见无效值
    if doi in {"na", "n/a", "none"}:
        return False

    # # 必须以 10. 开头
    # if not doi.startswith("10."):
    #     return False

    # # 必须包含 /
    # if "/" not in doi:
    #     return False

    # # 不能有空格
    # if " " in doi:
    #     return False

    # # 明显 URL / arxiv
    # if doi.startswith("http") or "arxiv" in doi:
    #     return False

    # 基本 DOI 正则（宽松）
    # pattern = r"^10\.\d{4,9}/[-._;()/:a-z0-9]+$"
    # if not re.match(pattern, doi):
    #     return False

    return True


# =========================
# 主流程
# =========================
def main():
    total = 0
    valid = 0
    invalid = 0

    with open(INPUT_CSV, "r", encoding="utf-8") as fin, \
         open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            total += 1
            doi = row.get("paper_doi", "")

            if is_valid_doi(doi):
                valid += 1
            else:
                invalid += 1
                continue
                

            writer.writerow(row)

    print("====== DOI 清洗完成 ======")
    print(f"总论文数: {total}")
    print(f"合法 DOI: {valid}")
    print(f"无效 DOI（已置空）: {invalid}")
    print(f"输出文件: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
