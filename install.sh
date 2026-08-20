#!/usr/bin/env bash
# Paseo 커스텀 셋업 설치 스크립트 (macOS / Linux)
# 사용법: 저장소 클론 후 이 폴더에서  ./install.sh
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
stamp="$(date +%Y%m%d-%H%M%S)"
src="$repo/rules/model-routing.md"

[ -f "$src" ] || { echo "오류: $src 가 없습니다"; exit 1; }

# 1. Claude 전역 규칙
mkdir -p "$HOME/.claude/rules"
cp "$src" "$HOME/.claude/rules/paseo-models.md"
echo "[1/3] Claude 전역 규칙 -> ~/.claude/rules/paseo-models.md"

# 2. Codex 전역 규칙 (같은 원본. 기존 파일은 백업 후 교체)
mkdir -p "$HOME/.codex"
if [ -f "$HOME/.codex/AGENTS.md" ]; then
  cp -p "$HOME/.codex/AGENTS.md" "$HOME/.codex/AGENTS.md.bak-$stamp"
  echo "      기존 AGENTS.md 백업 -> ~/.codex/AGENTS.md.bak-$stamp"
fi
cp "$src" "$HOME/.codex/AGENTS.md"
echo "[2/3] Codex 전역 규칙 -> ~/.codex/AGENTS.md"

# 3. Paseo appendSystemPrompt 패치 (프로바이더 불문 모든 에이전트에 주입)
cfg="$HOME/.paseo/config.json"
if [ -f "$cfg" ]; then
  cp -p "$cfg" "$cfg.bak-$stamp"
  python3 - "$cfg" "$repo/paseo/append-system-prompt.txt" <<'PY'
import io, json, sys
cfg_path, prompt_path = sys.argv[1], sys.argv[2]
with io.open(prompt_path, encoding="utf-8") as f:
    prompt = f.read().strip()
with io.open(cfg_path, encoding="utf-8") as f:
    cfg = json.load(f)
cfg.setdefault("daemon", {})["appendSystemPrompt"] = prompt
with io.open(cfg_path, "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("      appendSystemPrompt %d자 주입" % len(prompt))
PY
  echo "[3/3] Paseo config 패치 완료 (백업: $cfg.bak-$stamp)"
else
  echo "[3/3] ~/.paseo/config.json 이 없습니다 - Paseo 앱을 한 번 실행한 뒤 다시 돌리세요"
fi

cat <<'EOF'

완료.
- 라우팅 규칙(~/.claude/rules, ~/.codex/AGENTS.md)은 즉시 적용됩니다.
- appendSystemPrompt는 Paseo 앱(데몬)을 재시작해야 적용됩니다.
  주의: 재시작하면 돌고 있는 에이전트가 전부 종료됩니다.
EOF
