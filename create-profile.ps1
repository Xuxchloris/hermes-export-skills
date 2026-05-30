param(
  [Parameter(Mandatory=$true)]
  [string]$ProfileName
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME ".hermes" }
$ProfileDir = Join-Path (Join-Path $HermesHome "profiles") $ProfileName

New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "data\config") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "data\prospects") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "data\reports") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "data\emails") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "data\quotations") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "data\replies") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "data\follow-ups") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "sessions") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "memory") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "skills\custom") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ProfileDir "tools") | Out-Null

Copy-Item (Join-Path $RootDir "templates\PRODUCT.example.yaml") (Join-Path $ProfileDir "data\config\PRODUCT.yaml") -Force
Copy-Item (Join-Path $RootDir "templates\PRODUCTS.catalog.example.yaml") (Join-Path $ProfileDir "data\config\PRODUCTS.catalog.yaml") -Force
Copy-Item (Join-Path $RootDir "templates\MARKET.example.yaml") (Join-Path $ProfileDir "data\config\MARKET.yaml") -Force
Copy-Item (Join-Path $RootDir "templates\TONE.example.yaml") (Join-Path $ProfileDir "data\config\TONE.yaml") -Force
Copy-Item (Join-Path $RootDir "templates\PRICING.example.yaml") (Join-Path $ProfileDir "data\config\PRICING.yaml") -Force
Copy-Item (Join-Path $RootDir "templates\DISCOVERY.example.yaml") (Join-Path $ProfileDir "data\config\DISCOVERY.yaml") -Force
Copy-Item (Join-Path $RootDir "templates\.env.example") (Join-Path $ProfileDir ".env.example") -Force
Copy-Item (Join-Path $RootDir "tools\collect_prospects.py") (Join-Path $ProfileDir "tools\collect_prospects.py") -Force
Copy-Item (Join-Path $RootDir "tools\batch_prospect_pipeline.py") (Join-Path $ProfileDir "tools\batch_prospect_pipeline.py") -Force
Copy-Item (Join-Path $RootDir "tools\decision_maker_finder.py") (Join-Path $ProfileDir "tools\decision_maker_finder.py") -Force
Copy-Item (Join-Path $RootDir "tools\render_quotation.py") (Join-Path $ProfileDir "tools\render_quotation.py") -Force
Copy-Item (Join-Path $RootDir "tools\trade_utils.py") (Join-Path $ProfileDir "tools\trade_utils.py") -Force

@'
# Trade Agent Instructions

- Use `trade-workflow-router` as the entry point when the user mentions foreign trade broadly.
- Read product data from `data/config/PRODUCT.yaml`.
- For multiple products, read `data/config/PRODUCTS.catalog.yaml` and pass `--product-query` or `--sku` to profile tools.
- Read market strategy from `data/config/MARKET.yaml`.
- Read tone rules from `data/config/TONE.yaml`.
- Read quotation rules from `data/config/PRICING.yaml`.
- Read prospect discovery rules and collection API status from `data/config/DISCOVERY.yaml`.
- Save prospects in `data/prospects/`.
- Save research reports in `data/reports/`.
- Save email drafts in `data/emails/`.
- Save quotation drafts in `data/quotations/`.
- Save classified replies in `data/replies/`.
- Save follow-up plans in `data/follow-ups/`.
- Run local automation from this profile's `tools/` directory, such as `python tools/collect_prospects.py`.
- Never invent company facts, contact names, prices, certifications, or delivery dates.
- Use approved business sources and record source evidence for each prospect.
- Emails and quotations require human review before sending.
'@ | Set-Content -Encoding UTF8 -Path (Join-Path $ProfileDir "AGENTS.md")

Write-Host "Created profile at $ProfileDir"
