# hermes-export-skills

面向外贸出口业务的 Hermes / Codex Agent Skills 包。它把海外客户开发流程拆成可复用的 Agent skills 和可执行工具，从找客户、背调、评分、写开发信，到报价单导出，形成一套轻量的 B2B 外贸工作流。

![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Status](https://img.shields.io/badge/status-v0.1%20beta-orange.svg)

## 适合谁

- 外贸业务员：想让 Agent 帮你整理产品资料、找客户、写开发信和做报价草稿。
- 外贸团队：想把客户开发 SOP 变成可复用的 Agent 工作流。
- Agent 开发者：想参考一个面向垂直业务场景的 skills 包结构。

本项目不提供客户数据库，不自动发送邮件，不自动成交报价。所有客户判断、开发信和报价文件都应由人工审核后再使用。

## 核心能力

| 场景 | 能力 |
| --- | --- |
| 外贸入口 | 根据用户意图展示工作菜单，并路由到对应 skill |
| 产品资料 | 读取产品型号、尺寸、包装尺寸、MOQ、认证、交期和价格规则 |
| 客户发现 | 生成搜索任务，或通过配置的采集 API 获取候选客户 |
| 批量名单 | 清洗 CSV / Excel 客户名单，去重、背调、评分并生成开发信草稿 |
| 公司背调 | 分析公司网站、业务类型、产品线、证据和风险 |
| 客户评分 | 按产品匹配度、渠道价值、市场价值和决策层线索分级 |
| 决策层线索 | 从公司页面或配置 API 中提取角色、邮箱状态和来源页面 |
| 开发信 | 基于客户证据和产品事实生成个性化英文邮件草稿 |
| 回复处理 | 分类客户回复，并生成下一步建议 |
| 跟进计划 | 根据客户优先级和回复状态生成跟进任务 |
| 报价单 | 生成报价草稿，并导出 HTML / PDF / Excel |

## 快速安装

Linux / Mac：

```bash
curl -fsSL https://raw.githubusercontent.com/Xuxchloris/hermes-export-skills/main/bootstrap.sh | bash
```

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/Xuxchloris/hermes-export-skills/main/bootstrap.ps1 | iex
```

指定 profile 名称：

```bash
curl -fsSL https://raw.githubusercontent.com/Xuxchloris/hermes-export-skills/main/bootstrap.sh | bash -s -- my-export-profile
```

```powershell
$env:HERMES_PROFILE_NAME="my-export-profile"
irm https://raw.githubusercontent.com/Xuxchloris/hermes-export-skills/main/bootstrap.ps1 | iex
```

## 手动安装

```bash
git clone https://github.com/Xuxchloris/hermes-export-skills.git
cd hermes-export-skills
```

Linux / Mac：

```bash
chmod +x install.sh create-profile.sh
./install.sh
./create-profile.sh demo-trade-agent
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
powershell -ExecutionPolicy Bypass -File .\create-profile.ps1 demo-trade-agent
```

如果 Hermes 数据目录不是默认的 `~/.hermes`，先设置 `HERMES_HOME`：

```bash
export HERMES_HOME="$HOME/.hermes"
```

```powershell
$env:HERMES_HOME="$HOME\.hermes"
```

## 配置文件

创建 profile 后，编辑：

```text
~/.hermes/profiles/demo-trade-agent/data/config/PRODUCT.yaml
~/.hermes/profiles/demo-trade-agent/data/config/MARKET.yaml
~/.hermes/profiles/demo-trade-agent/data/config/TONE.yaml
~/.hermes/profiles/demo-trade-agent/data/config/PRICING.yaml
~/.hermes/profiles/demo-trade-agent/data/config/DISCOVERY.yaml
```

模板在 [templates](templates/) 目录。

## 使用方式

只输入“外贸”或“开发海外客户”，`trade-workflow-router` 会先展示工作菜单：

```text
外贸
```

也可以直接提出具体任务：

```text
请背调 https://example-distributor.com，判断它是否适合开发我们的折叠露营桌，并写一封英文开发信草稿。
```

## 批量客户开发

没有采集 API 时，先生成搜索任务：

```bash
python tools/collect_prospects.py \
  --discovery templates/DISCOVERY.example.yaml \
  --product templates/PRODUCT.example.yaml \
  --output-dir exports/prospect-collection
```

有客户名单后，运行批量流水线：

```bash
python tools/batch_prospect_pipeline.py \
  --input exports/prospect-collection/prospects.raw.csv \
  --product templates/PRODUCT.example.yaml \
  --market templates/MARKET.example.yaml \
  --tone templates/TONE.example.yaml \
  --output-dir exports/pipeline
```

单独查决策层线索：

```bash
python tools/decision_maker_finder.py \
  --website https://example.com \
  --output exports/decision-makers.json
```

## 报价导出

安装 Python 依赖：

```bash
python -m pip install -r requirements.txt
```

导出 HTML 和 Excel：

```bash
python tools/render_quotation.py examples/quotation.example.json \
  --output-dir exports/demo \
  --formats html excel
```

导出 HTML、Excel 和 PDF：

```bash
python tools/render_quotation.py examples/quotation.example.json \
  --output-dir exports/demo \
  --formats html excel pdf
```

PDF 从 HTML 转换，需要本机存在 Chrome、Edge 或 WeasyPrint。

## Skills 列表

| Skill | 用途 |
| --- | --- |
| `trade-workflow-router` | 外贸任务入口和工作流路由 |
| `product-loader` | 读取产品和价格配置 |
| `prospect-discovery` | 客户发现策略和采集 API 配置 |
| `prospect-list-enrichment` | 客户名单清洗、去重和批量处理 |
| `company-research` | 公司网站背调 |
| `prospect-scoring` | 客户优先级评分 |
| `decision-maker-finder` | 决策层角色和邮箱状态线索 |
| `email-crafting` | 个性化开发信和跟进邮件草稿 |
| `reply-classification` | 客户回复分类 |
| `follow-up-planner` | 跟进计划 |
| `quotation-generator` | 报价草稿和导出规范 |

## 工具脚本

| 脚本 | 输出 |
| --- | --- |
| `tools/collect_prospects.py` | `prospect_search_tasks.csv` 或 `prospects.raw.csv` |
| `tools/batch_prospect_pipeline.py` | `prospects.enriched.xlsx`、`scores.xlsx`、`email_drafts.xlsx`、`research_reports.json` |
| `tools/decision_maker_finder.py` | 决策层线索 JSON |
| `tools/render_quotation.py` | HTML / PDF / Excel 报价文件 |

## 项目结构

```text
skills/       Agent skills
tools/        可执行工具脚本
templates/    profile 配置模板
examples/     示例报价数据
docs/         使用、部署、合规和路线图
tests/        结构校验和工具测试
```

## 验证

```bash
python tests/validate_skills.py .
python -m unittest tests/test_trade_automation.py tests/test_render_quotation.py -v
```

成功时会看到：

```text
PASS: skill package structure and required content are valid
OK
```

## 合规边界

- 邮件和报价都作为草稿输出，需要人工审核。
- 不编造客户事实、联系人姓名、采购意图、认证、价格、运费或交期。
- 记录每个客户线索和个性化表达的来源。
- API key、真实客户名单、价格表和私有数据不要提交到 Git。

更多说明见 [docs/compliance.md](docs/compliance.md)。

## 路线图

- CRM 导出格式
- Campaign 文件夹输出结构
- 更多外贸行业模板
- 多语言开发信参考
- 可选 Apollo / Hunter 等 enrichment API 接入指南

## License

MIT
