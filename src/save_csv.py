from typing import Dict, List
import os
import pandas as pd


class CsvWriter:
    def __init__(self, output_path: str) -> None:
        self.output_path = output_path

        # 自动创建目录
        dirpath = os.path.dirname(output_path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)

        # 文件存在 → 已初始化，无需创建表头
        self._initialized = os.path.exists(self.output_path)

    def _prepare(self, columns: List[str]) -> None:
        """首次运行创建 CSV，写入表头"""
        if self._initialized:
            return
        # 创建空 DataFrame 写入表头
        pd.DataFrame(columns=columns).to_csv(self.output_path, index=False)
        self._initialized = True

    def append(self, rows: List[Dict]) -> None:
        """以追加模式写入 CSV，不重复写表头"""

        if not rows:
            return

        # 如果还没初始化（首次写入）
        if not self._initialized:
            self._prepare(list(rows[0].keys()))

        # 统一字段顺序，避免列乱序导致错位
        df = pd.DataFrame(rows)
        df = df[list(df.columns)]  # 确保列顺序固定

        df.to_csv(self.output_path, mode="a", index=False, header=False)