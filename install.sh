#!/usr/bin/env bash
# Paseo 커스텀 셋업 설치 스크립트 (macOS / Linux)
# 사용법: 저장소 클론 후 이 폴더에서  ./install.sh
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
stamp="$(date +%Y%m%d-%H%M%S)"
src="$repo/rules/model-routing.md"

[ -f "$src" ] || { echo "오류: $src 가 없습니다"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "오류: python3 가 필요합니다"; exit 1; }

# 1. Claude 전역 규칙 (전용 파일이므로 통째로 교체)
mkdir -p "$HOME/.claude/rules"
cp "$src" "$HOME/.claude/rules/paseo-models.md"
echo "[1/4] Claude 전역 규칙 -> ~/.claude/rules/paseo-models.md"

# 2. Codex 전역 규칙
#    ~/.codex/AGENTS.md 는 사용자의 다른 지침이 들어있을 수 있는 공용 파일이다.
#    기존 내용은 그대로 두고 마커 블록만 추가/갱신한다.
mkdir -p "$HOME/.codex"
agents="$HOME/.codex/AGENTS.md"
[ -f "$agents" ] && cp -p "$agents" "$agents.bak-$stamp"
python3 - "$agents" "$src" <<'PY'
import io, os, sys
target, source = sys.argv[1], sys.argv[2]
START, END = "<!-- paseo-setup:start -->", "<!-- paseo-setup:end -->"
body = io.open(source, encoding="utf-8").read().strip()
block = "%s\n%s\n%s" % (START, body, END)
old = io.open(target, encoding="utf-8").read() if os.path.exists(target) else ""
if START in old and END in old:
    head, rest = old.split(START, 1)
    tail = rest.split(END, 1)[1]
    new, how = head + block + tail, "기존 블록 갱신"
elif old.strip():
    new, how = old.rstrip() + "\n\n" + block + "\n", "기존 내용 유지하고 블록 추가"
else:
    new, how = block + "\n", "신규 생성"
io.open(target, "w", encoding="utf-8").write(new)
print("      %s" % how)
PY
echo "[2/4] Codex 전역 규칙 -> ~/.codex/AGENTS.md"

# 3. Paseo appendSystemPrompt 패치 (프로바이더 불문 모든 에이전트에 주입)
cfg="$HOME/.paseo/config.json"
if [ -f "$cfg" ]; then
  cp -p "$cfg" "$cfg.bak-$stamp"
  python3 - "$cfg" "$repo/paseo/append-system-prompt.txt" <<'PY'
import io, json, sys
cfg_path, prompt_path = sys.argv[1], sys.argv[2]
prompt = io.open(prompt_path, encoding="utf-8").read().strip()
cfg = json.load(io.open(cfg_path, encoding="utf-8"))
cfg.setdefault("daemon", {})["appendSystemPrompt"] = prompt
with io.open(cfg_path, "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("      appendSystemPrompt %d자 주입" % len(prompt))
PY
  echo "[3/4] Paseo config 패치 완료 (백업: $cfg.bak-$stamp)"
else
  echo "[3/4] ~/.paseo/config.json 이 없습니다"
  echo "      Paseo 앱을 한 번 실행한 뒤 이 스크립트를 다시 돌리세요 (1·2단계는 이미 끝났습니다)"
fi

# 4. 데몬에 설정 반영 (재시작이 아니라 reload — 돌고 있는 에이전트를 죽이지 않는다)
if command -v paseo >/dev/null 2>&1; then
  if paseo daemon reload >/dev/null 2>&1; then
    echo "[4/4] 데몬 설정 reload 완료 (에이전트 유지)"
  else
    echo "[4/4] reload 실패 - 데몬이 꺼져 있을 수 있습니다. 앱 실행 후 'paseo daemon reload'"
  fi
else
  echo "[4/4] paseo CLI 없음 - 앱 실행 후 'paseo daemon reload' 를 직접 돌리세요"
fi

cat <<'EOF'

완료.
- 라우팅 규칙(~/.claude/rules, ~/.codex/AGENTS.md)은 파일에서 바로 읽히므로 즉시 적용됩니다.
- appendSystemPrompt 는 `paseo daemon reload` 로 적용됩니다. 에이전트는 죽지 않습니다.
  (앱 재시작이나 `paseo daemon restart` 도 되지만, 그 경우 돌고 있는 에이전트가 전부 종료됩니다)
EOF
