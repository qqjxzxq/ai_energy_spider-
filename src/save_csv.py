from typing import Dict, List
import os
import pandas as pd


class CsvWriter:
    def __init__(self, output_path: str) -> None:
        self.output_path = output_path
        # 如果文件存在，说明之前已经写过，不需要 prepare
        self._initialized = os.path.exists(self.output_path)
        # --- 🔥 新增：自动创建目录 ---
        os.makedirs(os.path.dirname(output_path), exist_ok=True)


    def _prepare(self, columns: List[str]) -> None:
        """首次运行创建 CSV，写入表头"""
        if self._initialized:
            return
        pd.DataFrame(columns=columns).to_csv(self.output_path, index=False)
        self._initialized = True

    def append(self, rows: List[Dict]) -> None:
        """追加行，不反复写表头"""
        if not rows:
            return

        if not self._initialized:
            # 首次运行创建并写表头
            self._prepare(list(rows[0].keys()))

        df = pd.DataFrame(rows)
        df.to_csv(self.output_path, mode="a", index=False, header=False)
