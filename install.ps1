$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME ".hermes" }
$SkillDir = Join-Path $HermesHome "skills"
$ToolDir = Join-Path $HermesHome "tools"

New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
New-Item -ItemType Directory -Force -Path $ToolDir | Out-Null
Copy-Item -Path (Join-Path $RootDir "skills\*") -Destination $SkillDir -Recurse -Force
Copy-Item -Path (Join-Path $RootDir "tools\collect_prospects.py") -Destination (Join-Path $ToolDir "collect_prospects.py") -Force
Copy-Item -Path (Join-Path $RootDir "tools\scrapling_prospect_spider.py") -Destination (Join-Path $ToolDir "scrapling_prospect_spider.py") -Force
Copy-Item -Path (Join-Path $RootDir "tools\scrapling_spider_runner.py") -Destination (Join-Path $ToolDir "scrapling_spider_runner.py") -Force
Copy-Item -Path (Join-Path $RootDir "tools\scrapling_mcp_server.py") -Destination (Join-Path $ToolDir "scrapling_mcp_server.py") -Force
Copy-Item -Path (Join-Path $RootDir "tools\batch_prospect_pipeline.py") -Destination (Join-Path $ToolDir "batch_prospect_pipeline.py") -Force
Copy-Item -Path (Join-Path $RootDir "tools\decision_maker_finder.py") -Destination (Join-Path $ToolDir "decision_maker_finder.py") -Force
Copy-Item -Path (Join-Path $RootDir "tools\render_quotation.py") -Destination (Join-Path $ToolDir "render_quotation.py") -Force
Copy-Item -Path (Join-Path $RootDir "tools\trade_utils.py") -Destination (Join-Path $ToolDir "trade_utils.py") -Force

Write-Host "Installed trade skills to $SkillDir"
Write-Host "Installed trade tools to $ToolDir"
Write-Host "Run: .\create-profile.ps1 demo-trade-agent"
