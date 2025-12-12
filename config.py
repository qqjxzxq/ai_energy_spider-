import os

# 获取项目根目录（绝对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# OpenAlex API
OPENALEX_BASE = "https://api.openalex.org/works"
SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1/paper"

# 构造绝对路径
OUTPUT_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "ai_energy_papers.csv")
LOG_FILE = os.path.join(LOG_DIR, "spider.log")

# 创建必要目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

PER_PAGE = 200
MAX_RESULTS = 12000
SLEEP_BETWEEN_REQ = 0.4

AI_TERMS = [
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

ENERGY_TERMS = [
    "energy demand",
    "energy consumption",
    "load forecast",
    "electricity demand",
    "power load",
    "smart grid",
    "demand response",
    "renewable energy",
    "solar energy",
    "photovoltaic",
    "PV",
    "wind power",
    "wind speed",
    "hydropower",
    "energy efficiency",
    "building energy",
    "HVAC",
    "energy management",
    "energy conservation",
    "carbon emission",
    "carbon price",
    "energy market",
    "electricity price",
    "emission trading",
    "electric vehicle",
    "EV",
    "charging station",
    "battery",
    "energy storage",
    "state of charge",
]
