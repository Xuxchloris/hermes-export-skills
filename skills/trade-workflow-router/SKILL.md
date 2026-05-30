---
name: trade-workflow-router
description: Use when a user mentions foreign trade, export sales, overseas customer development, B2B outreach, 外贸, 海外客户开发, or asks what trade-agent work can be done next
---

# Trade Workflow Router

## Overview

Act as the entry point for foreign-trade workflows. The core rule is to ask the user to choose a clear task when their request is broad, then route the selected work to the relevant skill or executable tool.

## When to Use

Use this skill when the user only mentions foreign trade, export sales, customer development, or asks what the agent can do.

When the user already asks for a specific task, route directly to the matching skill without showing the full menu.

## Inputs

- User request
- Existing profile configuration, if available
- Existing customer list, website URL, reply text, or quotation details, if provided

## Outputs

```json
{
  "intent": "",
  "selected_workflow": "",
  "required_inputs": [],
  "skills_to_use": [],
  "tools_to_run": [],
  "next_step": ""
}
```

## Procedure

1. If the user request is broad, ask the user to choose from this 外贸工作菜单:
   1. Find overseas prospects and collect lead candidates
   2. Process a CSV or Excel customer list in batch
   3. Research a company website
   4. Score and prioritize prospects
   5. Find decision-maker clues
   6. Write personalized outreach emails
   7. Classify buyer replies
   8. Plan follow-up tasks
   9. Create a quotation draft
   10. Export quotation HTML, PDF, or Excel files
2. Ask the user to choose one item or describe the desired result in their own words.
3. Route prospect collection to `prospect-discovery`; use `tools/collect_prospects.py` when file output is needed. If the agent has source pages for the current task, pass them as runtime `--source-url` values. If `DISCOVERY.yaml` sets `discovery_mode: "native_scrapling_spider"` or `scrapling_spider.enabled: true`, `collect_prospects.py` uses `tools/scrapling_spider_runner.py` and writes `prospects.raw.csv`, `prospects.raw.json`, and `crawl_report.json`. If MCP is configured, the same workflow is exposed by `tools/scrapling_mcp_server.py`.
4. Route batch list processing to `prospect-list-enrichment`; use `tools/batch_prospect_pipeline.py` when one-step file output is needed.
5. Route website background research to `company-research`.
6. Route ranking and qualification to `prospect-scoring`.
7. Route decision-maker work to `decision-maker-finder`; use `tools/decision_maker_finder.py` when JSON output is needed.
8. Route personalized email drafting to `email-crafting`.
9. Route inbound buyer messages to `reply-classification`.
10. Route reminders and next-touch timing to `follow-up-planner`.
11. Route quotations to `quotation-generator`; use `tools/render_quotation.py` for HTML, PDF, or Excel file export.
12. When the user provides a website, CSV, Excel file, or discovery configuration, run the tool for the selected workflow before summarizing results.
13. Do not output company facts, scores, buyer claims, or personalized email lines unless they are backed by fetched evidence from the downstream tool output.
14. After completing one workflow, recommend the most relevant next workflow and ask whether the user wants to continue.

## Verification

- Broad foreign-trade requests receive the menu before work begins.
- Specific requests route directly to the matching skill.
- The selected workflow lists missing inputs before execution.
- The router does not claim completion before the selected downstream workflow finishes.
- Website and list workflows are based on fetched evidence, not generic examples.
- Prospect discovery with configured public source URLs produces `crawl_report.json`; if no rows are found, report that status instead of inventing prospects.
- The router offers a relevant next step after each completed workflow.

## Common Mistakes

| Mistake | Fix |
| --- | --- |
| Showing the menu after a specific request | Route directly to the requested skill |
| Running every skill at once | Use only the selected workflow and required dependencies |
| Asking vague follow-up questions | List the exact missing files or fields |
| Stopping after one task without context | Offer the most relevant next workflow |
