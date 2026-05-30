param(
  [string]$ProfileName = $(if ($env:HERMES_PROFILE_NAME) { $env:HERMES_PROFILE_NAME } else { "demo-trade-agent" })
)

$ErrorActionPreference = "Stop"

$RepoUrl = if ($env:HERMES_EXPORT_SKILLS_REPO_URL) { $env:HERMES_EXPORT_SKILLS_REPO_URL } else { "https://github.com/Xuxchloris/hermes-export-skills.git" }
$env:HERMES_HOME = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME ".hermes" }
$WorkDir = Join-Path ([System.IO.Path]::GetTempPath()) ("hermes-export-skills-" + [guid]::NewGuid().ToString("N"))

try {
  if (Get-Command git -ErrorAction SilentlyContinue) {
    git clone --depth 1 $RepoUrl $WorkDir | Out-Null
  } else {
    throw "git is required for bootstrap.ps1"
  }

  if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m pip install -r (Join-Path $WorkDir "requirements.txt")
  } else {
    throw "Python is required to install tool dependencies."
  }

  & (Join-Path $WorkDir "install.ps1")
  & (Join-Path $WorkDir "create-profile.ps1") $ProfileName

  Write-Host "Bootstrapped hermes-export-skills into profile: $ProfileName"
}
finally {
  if (Test-Path -LiteralPath $WorkDir) {
    Remove-Item -LiteralPath $WorkDir -Recurse -Force
  }
}
