# 阶段一说明（Stage 1 Notes）

## 1. 阶段目标

阶段一只做**最小可验证闭环**，不接入真实数据：

| 编号 | 任务 | 交付物 |
|---|---|---|
| A | 检查 Python 版本与磁盘空间 | 环境检查记录（见验收报告第 1 节） |
| B | 创建项目目录 | `config/ data/ src/ tests/ reports/ docs/ logs/` |
| C | 创建 requirements.txt | `requirements.txt` |
| D | 小型 JSONL 校验脚本 | `src/check_jsonl.py` |
| E | JSONL → Parquet 导出脚本 | `src/jsonl_to_parquet.py` |
| F | 10 条合成测试记录 | `data/interim/sample_records.jsonl` |
| G | 运行测试并生成报告 | `reports/initial_test_report.md` |
| H | 输出实际文件与测试结果 | 验收报告第 6 节 |

---

## 2. 数据模型

每条记录为一行 JSON（JSONL），字段如下：

```json
{
  "entity_id": "Q900000001",
  "entity_label_zh": "合成量子拓扑材料",
  "entity_label_en": "Synthetic Quantum Topological Material",
  "entity_type": "concept",
  "description": "这是一个用于测试的虚构材料概念……",
  "description_lang": "zh",
  "aliases": ["拓扑量子材料（虚构）"],
  "source": "synthetic-fixture",
  "license": "CC0-1.0 (synthetic fixture, contains no real-world data)",
  "retrieved_at": "2026-10-12T00:00:00Z",
  "is_synthetic": true,
  "data_origin": "SYNTHETIC_TEST_ONLY"
}
```

**必填字段**：`entity_id`、`source`、`is_synthetic`、`data_origin`
（定义于 `config/settings.json`，可调整而无需改代码。）

---

## 3. 合成测试集覆盖的边界情况

| 行号 | entity_id | 覆盖点 |
|---|---|---|
| 1 | Q900000001 | 纯中文文本 |
| 2 | Q900000002 | 纯英文文本 |
| 3 | Q900000003 | 中英混合 |
| 4 | Q900000004 | 缺失可选字段（description / aliases 为 null） |
| 5 | Q900000005 | 缺失英文标签 |
| 6 | Q900000002 | **重复 entity_id**（与第 2 行冲突） |
| 7 | QABC123 | **非法 QID**（含字母） |
| 8 | 42 | **非法 QID**（缺 Q 前缀） |
| 9 | Q900000009 | 多语言（日文 + 德文 + 变音符号 ä ö ü ß） |
| 10 | Q900000010 | 空字符串标签 |

语言覆盖：简体中文、英文、日文、德文 —— 用于验证 UTF-8 端到端读写。

---

## 4. 处理规则

### 4.1 校验（`check_jsonl.py`）

- **error 级**：JSON 解析失败、顶层非对象、缺必填字段、QID 非法
- **warning 级**：重复 `entity_id`（保留首条）、中英文标签同时为空
- 有效记录 = 可解析 − error 级 − 重复行

### 4.2 导出（`jsonl_to_parquet.py`）

- 跳过：解析失败 / 缺必填字段 / QID 非法 / 重复 `entity_id`
- 跳过明细写入 `reports/parquet_export_<时间戳>.json`，便于**修复后重跑**
- 输出已存在时默认拒绝覆盖，需 `--force`

---

## 5. 可重复运行与失败恢复

- 所有脚本**幂等**：`make_sample_data.py` 使用固定 `retrieved_at`，
  重复运行产出字节级一致的文件。
- 小批次流式读取：`--batch-size`，内存占用与文件大小无关。
- 失败恢复：被跳过的行带行号与原因记录在报告中；修复输入后重跑即可，
  无需手工清理中间状态。
- 报告文件名带 UTC 时间戳，不会互相覆盖历史结果。

---

## 6. 本阶段明确未做的事

- 未下载任何 Wikidata / Wikipedia 数据
- 未调用任何收费 API
- 未上传任何本地文件
- 未定义真实数据源的字段映射与许可审核流程
- 未实现增量抓取、图谱构建、去重合并等下游能力

---

## 7. 下一阶段的前置条件

1. 明确数据来源、接口形态与**使用许可**
2. 完成来源合法性审核；许可不明则先出待审核报告
3. 用户确认后再接入真实数据，并新增对应测试
