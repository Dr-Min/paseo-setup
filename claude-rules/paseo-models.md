# Paseo 서브에이전트 모델 선택 (전역 규칙)

선택 단위는 (모델 × 추론강도). 목록이 낡을 수 있으니 쓰기 전 `list_models` 확인.

| 작업 | 모델 + 추론강도 |
|---|---|
| 단순 웹검색·다운로드·폴링·툴 호출 | `codex/gpt-5.6-luna` + thinking **low** |
| 일반 작업 기본값 (리서치·코딩) | `codex/gpt-5.6-luna` + thinking **high** |
| 긴 컨텍스트(대량 문서, 256K+) | `codex/gpt-5.6-terra` + medium 이상 (Luna는 장문에서 급락) |
| 복잡 구현·장기 에이전트·난제 | `codex/gpt-5.6-sol` + high (실패 비용 클 때만) |
| 가벼운 검수 (plan 모드, 수정 금지) | `claude/claude-haiku-4-5` |
| 중요 검수·최종 판단 | `claude/claude-opus-5` 또는 오케스트레이터 직접 |

- gpt-5.5, gpt-5.4(-mini)는 구세대 — 신규 작업에 쓰지 않음 (2026-08 AA/CursorBench 검증: Luna high = Terra medium 동급 성능, 크레딧 Sol의 1/25)
- 힉스필드·미디어 생성 스킬은 claude 쪽에만 있음 → claude 에이전트 또는 오케스트레이터가 담당
- 근거: 2026-08 Artificial Analysis v4.1.1 / CursorBench 공개 데이터
