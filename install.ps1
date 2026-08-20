# Paseo 커스텀 셋업 설치 스크립트 (Windows PowerShell 5.1+)
# 사용법: 저장소 클론 후 이 폴더에서  .\install.ps1
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$stamp = Get-Date -Format yyyyMMdd-HHmmss
$src = "$repo\rules\model-routing.md"

if (-not (Test-Path $src)) { throw "오류: $src 가 없습니다" }

# 1. Claude 전역 규칙
$rulesDir = "$env:USERPROFILE\.claude\rules"
New-Item -ItemType Directory -Force $rulesDir | Out-Null
Copy-Item $src "$rulesDir\paseo-models.md" -Force
Write-Host "[1/3] Claude 전역 규칙 -> $rulesDir\paseo-models.md"

# 2. Codex 전역 규칙 (같은 원본. 기존 파일은 백업 후 교체)
$codexDir = "$env:USERPROFILE\.codex"
New-Item -ItemType Directory -Force $codexDir | Out-Null
$codexAgents = "$codexDir\AGENTS.md"
if (Test-Path $codexAgents) {
  Copy-Item $codexAgents "$codexAgents.bak-$stamp"
  Write-Host "      기존 AGENTS.md 백업 -> $codexAgents.bak-$stamp"
}
Copy-Item $src $codexAgents -Force
Write-Host "[2/3] Codex 전역 규칙 -> $codexAgents"

# 3. Paseo appendSystemPrompt 패치 (프로바이더 불문 모든 에이전트에 주입)
$cfgPath = "$env:USERPROFILE\.paseo\config.json"
$prompt = (Get-Content "$repo\paseo\append-system-prompt.txt" -Raw -Encoding UTF8).Trim()
if (Test-Path $cfgPath) {
  Copy-Item $cfgPath "$cfgPath.bak-$stamp"
  $cfg = Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if (-not $cfg.daemon) { $cfg | Add-Member -MemberType NoteProperty -Name daemon -Value ([pscustomobject]@{}) }
  $cfg.daemon | Add-Member -MemberType NoteProperty -Name appendSystemPrompt -Value $prompt -Force
  $json = $cfg | ConvertTo-Json -Depth 10
  [IO.File]::WriteAllText($cfgPath, $json, [Text.UTF8Encoding]::new($false))
  Write-Host "[3/3] Paseo config 패치 완료 (백업: $cfgPath.bak-$stamp)"
} else {
  Write-Host "[3/3] ~/.paseo/config.json 이 없습니다 - Paseo 앱을 한 번 실행한 뒤 다시 돌리세요"
}

Write-Host ""
Write-Host "완료."
Write-Host "- 라우팅 규칙(~/.claude/rules, ~/.codex/AGENTS.md)은 즉시 적용됩니다."
Write-Host "- appendSystemPrompt는 Paseo 앱(데몬)을 재시작해야 적용됩니다."
Write-Host "  주의: 재시작하면 돌고 있는 에이전트가 전부 종료됩니다."
