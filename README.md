# Plas-References — 等离激元纳米材料文献库（2016–2026）

等离激元纳米材料（plasmonic nanomaterials）领域 2016-01-01 至 2026-10-09 的回顾性文献检索归档。
由 `plasmonics-literature-pipeline` 流水线生成（Europe PMC + arXiv，6 组主题查询，11 个年度分段）。

## 仓库内容

| 路径 | 内容 |
|---|---|
| `literature_database.json` | 顶尖期刊精选库 9,313 条（期刊白名单 A–H × 相关度标注，含摘要/被引/DOI） |
| `05_Archive/` | 全量归档 35,758 条按年拆分（`literature_database_all_<YYYY>.json`，供审计与重刷） |
| `02_BibTeX/` | 全量 + 按年 BibTeX（`PLASMON_` 前缀）与命名清单 naming_manifest |
| `03_Reports/` | 2016–2026 回顾检索汇总报告、手动下载 Checklist、相关度复核表、期刊排除日志 |
| `04_Biomedical/` | **等离激元 × 生物医学应用子集（5,526 条）**：子集 JSON/CSV、BibTeX、Checklist、子集报告 |
| `tools/` | 流水线脚本（检索/入库/筛选/DOI/BibTeX/Checklist/相关度标注） |

## 统计概要

- 原始去重记录 35,758 条 → 期刊白名单保留 9,313 条（Nature 家族 492 / Science 家族 124 / 学科顶刊 2,057 / 次顶刊 4,202 等）
- 生物医学应用子集 5,526 条：SERS 传感 2,721 / LSPR 生物传感 1,859 / 肿瘤诊疗 917 / 光热光动力 786 等
- DOI 覆盖 99.9%+（缺失项保留英文原题供手动检索，未编造 DOI）

## Checklist 三态标记

- `[√]` = 已获取 PDF（头部方框）｜`[ ]` = 待下载｜`[x]` = 机构未订阅（「无法下载」方框）
- 重建/更新：`python tools/plm_rebuild_checklist.py --dir <项目或子集目录>`

## 版权红线

**出版商 PDF 永不上传**。本仓库仅含元数据、BibTeX、报告、checklist 与流水线脚本；`01_PDF/`、`*.pdf`、`raw/` 均被排除。
