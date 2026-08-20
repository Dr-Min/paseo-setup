# Paseo 커스텀 셋업 설치 스크립트 (Windows PowerShell 5.1+)
# 사용법: 저장소 클론 후 이 폴더에서  .\install.ps1
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$stamp = Get-Date -Format yyyyMMdd-HHmmss
$src = "$repo\rules\model-routing.md"

if (-not (Test-Path $src)) { throw "오류: $src 가 없습니다" }
$utf8 = [Text.UTF8Encoding]::new($false)

# 1. Claude 전역 규칙 (전용 파일이므로 통째로 교체)
$rulesDir = "$env:USERPROFILE\.claude\rules"
New-Item -ItemType Directory -Force $rulesDir | Out-Null
Copy-Item $src "$rulesDir\paseo-models.md" -Force
Write-Host "[1/4] Claude 전역 규칙 -> $rulesDir\paseo-models.md"

# 2. Codex 전역 규칙
#    ~/.codex/AGENTS.md 는 사용자의 다른 지침이 들어있을 수 있는 공용 파일이다.
#    기존 내용은 그대로 두고 마커 블록만 추가/갱신한다.
$codexDir = "$env:USERPROFILE\.codex"
New-Item -ItemType Directory -Force $codexDir | Out-Null
$agents = "$codexDir\AGENTS.md"
$START = "<!-- paseo-setup:start -->"
$END = "<!-- paseo-setup:end -->"
$body = (Get-Content $src -Raw -Encoding UTF8).Trim()
$block = "$START`n$body`n$END"
if (Test-Path $agents) {
  Copy-Item $agents "$agents.bak-$stamp"
  $old = Get-Content $agents -Raw -Encoding UTF8
} else {
  $old = ""
}
if ($old.Contains($START) -and $old.Contains($END)) {
  $head = $old.Substring(0, $old.IndexOf($START))
  $tail = $old.Substring($old.IndexOf($END) + $END.Length)
  $new = $head + $block + $tail
  Write-Host "      기존 블록 갱신"
} elseif ($old.Trim()) {
  $new = $old.TrimEnd() + "`n`n" + $block + "`n"
  Write-Host "      기존 내용 유지하고 블록 추가"
} else {
  $new = $block + "`n"
  Write-Host "      신규 생성"
}
[IO.File]::WriteAllText($agents, $new, $utf8)
Write-Host "[2/4] Codex 전역 규칙 -> $agents"

# 3. Paseo appendSystemPrompt 패치 (프로바이더 불문 모든 에이전트에 주입)
$cfgPath = "$env:USERPROFILE\.paseo\config.json"
$prompt = (Get-Content "$repo\paseo\append-system-prompt.txt" -Raw -Encoding UTF8).Trim()
if (Test-Path $cfgPath) {
  Copy-Item $cfgPath "$cfgPath.bak-$stamp"
  $cfg = Get-Content $cfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if (-not $cfg.daemon) { $cfg | Add-Member -MemberType NoteProperty -Name daemon -Value ([pscustomobject]@{}) }
  $cfg.daemon | Add-Member -MemberType NoteProperty -Name appendSystemPrompt -Value $prompt -Force
  [IO.File]::WriteAllText($cfgPath, ($cfg | ConvertTo-Json -Depth 10), $utf8)
  Write-Host "[3/4] Paseo config 패치 완료 (백업: $cfgPath.bak-$stamp)"
} else {
  Write-Host "[3/4] ~/.paseo/config.json 이 없습니다"
  Write-Host "      Paseo 앱을 한 번 실행한 뒤 다시 돌리세요 (1·2단계는 이미 끝났습니다)"
}

# 4. 데몬에 설정 반영 (재시작이 아니라 reload — 돌고 있는 에이전트를 죽이지 않는다)
if (Get-Command paseo -ErrorAction SilentlyContinue) {
  paseo daemon reload *> $null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "[4/4] 데몬 설정 reload 완료 (에이전트 유지)"
  } else {
    Write-Host "[4/4] reload 실패 - 데몬이 꺼져 있을 수 있습니다. 앱 실행 후 'paseo daemon reload'"
  }
} else {
  Write-Host "[4/4] paseo CLI 없음 - 앱 실행 후 'paseo daemon reload' 를 직접 돌리세요"
}

Write-Host ""
Write-Host "완료."
Write-Host "- 라우팅 규칙(~/.claude/rules, ~/.codex/AGENTS.md)은 파일에서 바로 읽히므로 즉시 적용됩니다."
Write-Host "- appendSystemPrompt 는 'paseo daemon reload' 로 적용됩니다. 에이전트는 죽지 않습니다."
Write-Host "  (앱 재시작이나 'paseo daemon restart' 도 되지만, 그 경우 에이전트가 전부 종료됩니다)"
