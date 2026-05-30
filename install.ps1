$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME ".hermes" }
$SkillDir = Join-Path $HermesHome "skills"

New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
Copy-Item -Path (Join-Path $RootDir "skills\*") -Destination $SkillDir -Recurse -Force

Write-Host "Installed trade skills to $SkillDir"
Write-Host "Run: .\create-profile.ps1 demo-trade-agent"
