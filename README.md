# paseo-setup

파세오(Paseo) + 클로드 커스텀 설정 이식용 저장소. 새 PC에서 아래 두 줄이면 끝.

```powershell
git clone https://github.com/Dr-Min/paseo-setup.git; cd paseo-setup
.\install.ps1
```

설치 후 **Paseo 앱을 재시작**해야 적용됩니다 (재시작 시 돌고 있는 에이전트 전부 종료 주의).

## 들어있는 것

| 파일 | 설치 위치 | 역할 |
|---|---|---|
| `claude-rules/paseo-models.md` | `~/.claude/rules/` | 서브에이전트 모델×추론강도 선택 기준 (클로드 세션 전역) |
| `paseo/append-system-prompt.txt` | `~/.paseo/config.json`의 `daemon.appendSystemPrompt` | 파세오가 띄우는 **모든 에이전트**(claude/codex 불문)에 주입되는 운영 철칙 5줄 |
| `docs/PASEO-guide-ko.md` | (문서) | 파세오 v0.4.0 한국어 실측 가이드 |

## 운영 철칙 요약 (appendSystemPrompt)

1. 검증·리뷰 역할: 파일 수정 금지, 명령 직접 실행 + 출력 인용, 마지막 줄 `DONE=true/false`
2. 리서치 보고: 출처 URL 필수, 미확인은 '추정' 명시
3. 단순 작업에 과잉 사고 금지
4. 파괴적 작업은 명시적 지시가 있을 때만
5. 최종 보고는 한국어

## 모델 선택 기준 요약

- 기본값: `codex/gpt-5.6-luna` + thinking high (단순 작업은 low)
- 긴 컨텍스트(256K+): `gpt-5.6-terra` 이상 / 난제·장기 에이전트: `gpt-5.6-sol`
- 검수: `claude-haiku-4-5`(가벼움) / `claude-opus-5`(중요)
- gpt-5.5·5.4 구세대는 신규 작업에 사용 안 함

수정하면 이 저장소에 커밋하고, 각 PC에서 `git pull` 후 `.\install.ps1` 재실행.
