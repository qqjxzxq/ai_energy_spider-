import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence


def ensure_directories(paths: Sequence[str]) -> None:
    """确保输出与日志目录存在。"""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def setup_logging(log_file: str) -> logging.Logger:
    """初始化日志配置，返回 logger。"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger("ai_energy_spider")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    return logger


def inverted_index_to_text(index: Optional[Dict[str, List[int]]]) -> str:
    """将 OpenAlex abstract_inverted_index 转成原始摘要文本。"""
    if not index:
        return ""
    tokens = sorted(
        [(pos, word) for word, positions in index.items() for pos in positions],
        key=lambda pair: pair[0],
    )
    return " ".join(word for _, word in tokens)


def chunk_iterable(items: Iterable[Dict], size: int) -> Iterable[List[Dict]]:
    """按固定大小切分迭代器结果，用于批量写入 CSV。"""
    batch: List[Dict] = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def load_existing_ids(csv_path: str, id_column: str) -> set:
    """读取已存在 CSV，返回指定列的去重集合。"""
    if not os.path.exists(csv_path):
        return set()
    import pandas as pd

    try:
        df = pd.read_csv(csv_path, usecols=[id_column])
        return set(df[id_column].dropna().tolist())
    except Exception:
        return set()


def write_state(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp)


def read_state(path: str) -> Dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def sleep_with_jitter(base: float) -> None:
    """避免固定间隔导致的节奏一致，增加随机抖动。"""
    jitter = base * 0.3
    wait = base + (jitter * (0.5 - os.urandom(1)[0] / 255))
    time.sleep(max(wait, 0.05))