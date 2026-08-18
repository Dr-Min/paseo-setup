# Paseo 커스텀 셋업 설치 스크립트 (Windows PowerShell 5.1+)
# 사용법: 저장소 클론 후 이 폴더에서  .\install.ps1
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Claude 전역 규칙 (~/.claude/rules) — 클로드 세션 전역 적용
$rulesDir = "$env:USERPROFILE\.claude\rules"
New-Item -ItemType Directory -Force $rulesDir | Out-Null
Copy-Item "$repo\claude-rules\*.md" $rulesDir -Force
Write-Host "[1/2] Claude 전역 규칙 설치 -> $rulesDir"

# 2. Paseo appendSystemPrompt 패치 — 파세오가 띄우는 모든 에이전트(provider 불문)에 주입
$cfgPath = "$env:USERPROFILE\.paseo\config.json"
$prompt = (Get-Content "$repo\paseo\append-system-prompt.txt" -Raw -Encoding UTF8).Trim()
if (Test-Path $cfgPath) {
  Copy-Item $cfgPath "$cfgPath.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
  $cfg = Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if (-not $cfg.daemon) { $cfg | Add-Member -MemberType NoteProperty -Name daemon -Value ([pscustomobject]@{}) }
  $cfg.daemon | Add-Member -MemberType NoteProperty -Name appendSystemPrompt -Value $prompt -Force
  $json = $cfg | ConvertTo-Json -Depth 10
  [IO.File]::WriteAllText($cfgPath, $json, [Text.UTF8Encoding]::new($false))
  Write-Host "[2/2] Paseo config 패치 완료 (백업 생성됨: $cfgPath.bak-*)"
} else {
  Write-Host "[2/2] ~/.paseo/config.json 이 없습니다 - Paseo 앱을 한 번 실행한 뒤 이 스크립트를 다시 돌리세요"
}

Write-Host ""
Write-Host "완료. Paseo 앱(데몬)을 재시작하면 적용됩니다."
Write-Host "주의: 재시작하면 돌고 있는 에이전트가 전부 종료됩니다."
