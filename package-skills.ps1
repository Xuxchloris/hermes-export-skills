# package-skills.ps1 — 将每个 skill 目录打包为 Cowork 兼容的 .skill 文件
# 用法: .\package-skills.ps1 [version]
# 示例: .\package-skills.ps1 v0.1.0

param(
    [string]$Version = "v0.1.0"
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsDir = Join-Path $RootDir "skills"
$ReleasesDir = Join-Path $RootDir "releases"

if (Test-Path $ReleasesDir) {
    Remove-Item -Recurse -Force $ReleasesDir
}
New-Item -ItemType Directory -Force -Path $ReleasesDir | Out-Null

Write-Host "=== Packaging skills from $SkillsDir ==="
Write-Host ""

$packed = 0
Get-ChildItem -Path $SkillsDir -Directory | ForEach-Object {
    $skillName = $_.Name
    $skillDir = $_.FullName
    $skillMd = Join-Path $skillDir "SKILL.md"

    if (-not (Test-Path $skillMd)) {
        Write-Host "SKIP: $skillName (no SKILL.md)"
        return
    }

    # 读取 skill 描述
    $description = ""
    Get-Content $skillMd | Select-Object -First 5 | ForEach-Object {
        if ($_ -match "^description: (.+)") {
            $description = $Matches[1]
        }
    }

    $outputFile = Join-Path $ReleasesDir "${skillName}-${Version}.skill"

    # 打包为 zip（.skill 本质是 zip）
    $currentLocation = Get-Location
    Set-Location $skillDir
    Compress-Archive -Path * -DestinationPath $outputFile -Force
    Set-Location $currentLocation

    $size = "{0:N1} KB" -f ((Get-Item $outputFile).Length / 1KB)
    Write-Host "OK: $skillName -> ${skillName}-${Version}.skill ($size)"
    Write-Host "    $description"
    Write-Host ""
    $global:packed++
}

$packed = $global:packed
Write-Host "=== Done: $packed skills packaged to $ReleasesDir ==="
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Upload files in releases/ to GitHub Releases"
Write-Host "  2. Or distribute directly via link/email"
Write-Host "  3. Users download .skill file -> Cowork shows 'Save skill' button -> one-click install"
