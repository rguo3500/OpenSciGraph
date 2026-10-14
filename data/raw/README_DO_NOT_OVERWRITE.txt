data/raw —— 原始输入目录（只读保护区）
================================================

【用途】
存放"原始、未加工"的输入数据。任何脚本都不得修改、删除或覆盖本目录中的文件。

【硬性规则】
1. 项目所有脚本在写入前都会调用 assert_writable() 检查目标路径；
   只要目标位于 data/raw 之下，就会直接抛出 PermissionError 并终止。
   （该行为由 tests/test_pipeline.py::TestWriteProtection 验证。）

2. 所有派生结果请写到：
   - data/interim/    中间格式（JSONL 等）
   - data/processed/  交付格式（Parquet 等）

3. 如需修正原始数据，请新建带版本号的文件（例如 xxx_v2.jsonl），
   而不是原地覆盖。

【当前状态（阶段一）】
本目录为空。第一阶段未下载任何真实 Wikidata / Wikipedia 数据，
项目仅使用 data/interim/sample_records.jsonl 中的 10 条合成测试记录。

【数据来源与许可】
尚未接入真实数据源。接入前必须先完成来源与许可审核：
一旦发现来源许可不明，将停止发布流程并生成待审核报告。
