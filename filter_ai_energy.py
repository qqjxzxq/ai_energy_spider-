import csv
import os
import re

# =========================
# 文件路径
# =========================
INPUT_CSV = "data/ai_energy_papers_full.csv"
OUTPUT_CSV = "data/final/clean_8.csv"

# =========================
# 强 AI 关键词（必须至少命中 1 个）
# =========================
STRONG_AI_KEYWORDS = [
    "machine learning",
    "deep learning",
    "artificial intelligence",

    "neural network",
    "artificial neural network",
    "convolutional neural network",
    "recurrent neural network",

    "transformer",
    "attention mechanism",

    "graph neural network",
    "generative adversarial network",

    "reinforcement learning",

    "large language model",
    "foundation model",
    "chatgpt",
    "machine learning",
    "deep learning", 
    "artificial intelligence", 
    "AI", 
    "data-driven", 
    "regression", 
    "support vector machine",
    "SVM", 
    "random forest", 
    "gradient boosting",
    "XGBoost",
    "neural network",
    "NN", 
    "artificial neural network",
    "ANN",
    "recurrent neural network",
    "RNN",
    "LSTM",
    "GRU", 
    "convolutional neural network",
    "CNN",
    "transformer",
    "attention mechanism",
    "graph neural network",
    "GNN",
    "generative adversarial network",
    "GAN",
    "reinforcement learning",
    "RL",
    "large language model",
    "LLM",
    "foundation model",
    "pretrained model",
    "ChatGPT",
    "time series analysis",
    "transfer learning",
]

# =========================
# 弱 AI 关键词（必须搭配强词）
# =========================
WEAK_AI_KEYWORDS = [
    "regression",
    "support vector machine",
    "svm",

    "time series"
    
    
]

# =========================
# 明确排除的非 AI 关键词（黑名单）
# =========================
BLACKLIST_KEYWORDS = [
    "pcr",
    "turbine",
    "gas bearing",
    "wind turbine",
    "expansion turbine",

    "policy",
    "planning",
    "market",
    "economic analysis",

    "indoor environment",
    "ieq",
    "epiqr",

    "voltage-clock",
    "real-time system",
    "scheduling",
]

# =========================
# AI 判定函数（加强版）
# =========================
def is_ai_related(row):
    """
    AI 判定逻辑：
    1. title + abstract + concepts 合并
    2. 先排除 blacklist
    3. 命中强 AI 关键词 -> True
    4. 命中弱词 + 强词 -> True
    """
    text = " ".join([
        row.get("title", ""),
        row.get("abstract", "")
        # row.get("concepts", ""),
    ]).lower()

    # ---------- 黑名单优先 ----------
    for kw in BLACKLIST_KEYWORDS:
        if kw in text:
            return False

    # ---------- 强 AI 关键词 ----------
    for kw in STRONG_AI_KEYWORDS:
        if kw in text:
            return True

    # ---------- 弱词 + 强词 ----------
    weak_hit = any(kw in text for kw in WEAK_AI_KEYWORDS)
    strong_hit = any(kw in text for kw in STRONG_AI_KEYWORDS)

    if weak_hit and strong_hit:
        return True

    return False


# =========================
# 主流程
# =========================
def main():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"找不到输入文件：{INPUT_CSV}")

    total = 0
    ai_count = 0

    with open(INPUT_CSV, "r", encoding="utf-8") as fin, \
         open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)

        writer.writeheader()

        for row in reader:
            total += 1

            if is_ai_related(row):
                writer.writerow(row)
                ai_count += 1

    print("====== AI + 能源 严格筛选完成 ======")
    print(f"能源论文总数: {total}")
    print(f"AI + 能源论文数: {ai_count}")
    print(f"结果文件: {OUTPUT_CSV}")


# =========================
# 启动
# =========================
if __name__ == "__main__":
    main()
