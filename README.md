# AI_Energy_Spider

用于抓取 AI 与 Energy 交叉领域论文数据（基于 OpenAlex + Semantic Scholar）。输出 CSV，字段齐全，支持断点续爬与去重。

## 安装

```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## 使用

```bash
python run.py --max-results 9000 --resume
```

- 默认基于 OpenAlex 抓取 AI × Energy 论文，并调用 Semantic Scholar 丰富引用信息。
- 输出 CSV 位于 `data/ai_energy_papers.csv`，字段包含作者、机构、引用、OA 等信息，可直接用于构建合作者网络与引文网络。
- `--skip-semantic` 可跳过 Semantic Scholar 以提升速度；`--resume` 会读取已保存文件并跳过重复 ID。
# AI_Energy_Spider

用于抓取 AI 与 Energy 交叉领域论文数据（基于 OpenAlex + Semantic Scholar）。输出 CSV，字段齐全，支持断点续爬与去重。

## 安装

```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt# ai_energy_spider-
