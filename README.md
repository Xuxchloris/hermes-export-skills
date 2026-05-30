# hermes-export-skills

`hermes-export-skills` 是一套面向外贸出口业务的 Agent Skills 包，用于帮助 Hermes / openclaw类 Agent 搭建 B2B 海外客户开发工作流。

项目覆盖从产品资料读取、海外客户发现、批量名单处理、公司网站背调、客户评分、决策层线索提取、个性化开发信撰写、客户回复分类、跟进计划，到外贸报价单生成与 HTML / PDF / Excel 导出的完整基础流程。

本项目定位为外贸业务助手和工作流工具包，不提供客户数据库，不自动发送邮件，不自动完成报价成交。所有开发信、客户判断和报价文件都应由人工审核后再使用。

## 安装

先下载项目：

```bash
git clone https://github.com/your-name/hermes-trade-agent-skills.git
cd hermes-trade-agent-skills
```

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
powershell -ExecutionPolicy Bypass -File .\create-profile.ps1 demo-trade-agent
```

Linux：

```bash
chmod +x install.sh create-profile.sh
./install.sh
./create-profile.sh demo-trade-agent
```

Mac：

```bash
chmod +x install.sh create-profile.sh
./install.sh
./create-profile.sh demo-trade-agent
```

如果 Hermes 数据目录不是默认的 `~/.hermes`，可以先设置 `HERMES_HOME`：

```bash
export HERMES_HOME="$HOME/.hermes"
```

Windows PowerShell：

```powershell
$env:HERMES_HOME="$HOME\.hermes"
```

## 配置文件

创建 profile 后，编辑这些文件：

```text
~/.hermes/profiles/demo-trade-agent/data/config/PRODUCT.yaml
~/.hermes/profiles/demo-trade-agent/data/config/MARKET.yaml
~/.hermes/profiles/demo-trade-agent/data/config/TONE.yaml
~/.hermes/profiles/demo-trade-agent/data/config/PRICING.yaml
~/.hermes/profiles/demo-trade-agent/data/config/DISCOVERY.yaml
```

模板在 `templates/` 目录里。

## 外贸工作入口

如果用户只说“外贸”“开发海外客户”或“我接下来可以做什么”，`trade-workflow-router` 会先展示工作菜单，让用户选择客户采集、名单处理、网站背调、客户评分、决策层线索、开发信、回复分类、跟进计划、报价或报价导出。

如果用户已经明确提出具体任务，就会直接进入对应 skill。

## 报价导出

先安装 Python 依赖：

```bash
python -m pip install -r requirements.txt
```

使用示例报价数据导出 HTML 和 Excel：

```bash
python tools/render_quotation.py examples/quotation.example.json --output-dir exports/demo --formats html excel
```

导出 PDF 时增加 `pdf`：

```bash
python tools/render_quotation.py examples/quotation.example.json --output-dir exports/demo --formats html excel pdf
```

PDF 从 HTML 转换，需要本机存在 Chrome、Edge 或 WeasyPrint。

## 批量开发客户

没有采集 API 时，先生成搜索任务：

```bash
python tools/collect_prospects.py --discovery templates/DISCOVERY.example.yaml --product templates/PRODUCT.example.yaml --output-dir exports/prospect-collection
```

有客户名单后，运行批量流水线：

```bash
python tools/batch_prospect_pipeline.py --input exports/prospect-collection/prospects.raw.csv --product templates/PRODUCT.example.yaml --market templates/MARKET.example.yaml --tone templates/TONE.example.yaml --output-dir exports/pipeline
```

单独查决策层线索：

```bash
python tools/decision_maker_finder.py --website https://example.com --output exports/decision-makers.json
```

## 当前实现的 Skills

| Skill | 已实现功能 |
| --- | --- |
| `trade-workflow-router` | 识别外贸任务，展示工作菜单，并串联调用对应 skills 和工具 |
| `product-loader` | 读取产品资料、SKU、尺寸、包装、MOQ、价格规则、认证、交期，并标记缺失字段 |
| `prospect-discovery` | 制定合规客户发现策略，管理采集 API 配置，输出关键词、来源、候选客户字段和风险备注 |
| `prospect-list-enrichment` | 清洗 CSV / Excel 客户名单、去重、标记缺失字段，并生成待背调队列 |
| `company-research` | 根据客户网站或资料做背调，提取业务类型、产品线、证据、开发切入点和风险 |
| `prospect-scoring` | 按产品匹配度、渠道价值、市场价值、联系人线索和风险给客户 A/B/C/D 分级 |
| `email-crafting` | 基于背调证据生成英文开发信、跟进邮件、主题行和人工审核备注 |
| `reply-classification` | 分类客户回复，识别询价、目录、样品、异议、退订和待人工判断状态 |
| `follow-up-planner` | 根据客户优先级和回复状态生成待人工审核的跟进计划 |
| `decision-maker-finder` | 从公司页面和可配置 API 中提取决策层角色线索、来源页面和邮箱状态 |
| `quotation-generator` | 根据产品和价格规则生成报价草稿，并规范导出 HTML、PDF 或 Excel |

示例提问：

```text
请背调 https://example-distributor.com，判断它是否适合开发我们的折叠露营桌，并写一封英文开发信草稿。
```

## 后续优化方向

- 批量客户处理增强：增加批量背调执行器、评分汇总和结果导出。
- 行业模板扩展：增加户外用品、五金、家居、汽配、电子配件等常见外贸行业模板。
- 多语言开发信：补充西语、法语、德语、阿语等本地化邮件参考。
- 合规检查：加强退订提示、敏感地区、隐私和反垃圾邮件规则提醒。

## 验证

```bash
python tests/validate_skills.py .
```

成功时会看到：

```text
PASS: skill package structure and required content are valid
```

## License

MIT
