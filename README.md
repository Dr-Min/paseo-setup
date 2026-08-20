# paseo-setup

파세오(Paseo) + 클로드/코덱스 커스텀 설정 이식용 저장소.
**오케스트레이터가 클로드든 코덱스든 동일하게 적용**되고, **클로드 없이 코덱스만으로도 동작**한다.

```bash
# macOS / Linux
git clone https://github.com/Dr-Min/paseo-setup.git && cd paseo-setup
./install.sh
```

```powershell
# Windows
git clone https://github.com/Dr-Min/paseo-setup.git; cd paseo-setup
.\install.ps1
```

설치 스크립트가 마지막에 `paseo daemon reload` 까지 돌려서 바로 적용한다.
**데몬을 재시작하지 않으므로 돌고 있는 에이전트가 죽지 않는다.**

- 라우팅 규칙(`~/.claude/rules`, `~/.codex/AGENTS.md`)은 파일에서 바로 읽히므로 reload 도 필요 없다.
- `appendSystemPrompt` 만 데몬에 반영이 필요하고, 그게 `paseo daemon reload` 다.
- CLI 가 없으면 앱 실행 후 직접 `paseo daemon reload` 를 돌리면 된다.
  `paseo daemon restart` 나 앱 재시작도 되지만 그 경우 에이전트가 전부 종료된다.

## 들어있는 것

| 파일 | 설치 위치 | 역할 |
|---|---|---|
| `rules/model-routing.md` | `~/.claude/rules/paseo-models.md`<br>`~/.codex/AGENTS.md` | **단일 원본.** 역할·선언승인·라우팅표·폴백·보안·비용 |
| `paseo/append-system-prompt.txt` | `~/.paseo/config.json` 의 `daemon.appendSystemPrompt` | 프로바이더 불문 **모든 에이전트**에 주입되는 운영 철칙 7줄 |
| `docs/PASEO-guide-ko.md` | (문서) | 파세오 한국어 실측 가이드 |
| `eval/` | (설치 안 함) | 라우팅 규칙 검증용 채점기·과제·측정 기록 |

라우팅 원본 하나를 양쪽 CLI에 뿌린다. `~/.claude/rules/`는 클로드만, `~/.codex/AGENTS.md`는
코덱스만 읽기 때문에 둘 다 필요하다. 파세오가 띄운 코덱스 에이전트가 `~/.codex/AGENTS.md`를
자동 로드하는 것은 실측 확인됨.

**기존 `~/.codex/AGENTS.md`는 지워지지 않는다.** 그 파일은 다른 지침이 들어있을 수 있는
공용 파일이라, 설치 스크립트가 아래 마커 블록만 추가하고 나머지는 그대로 둔다.
재설치하면 블록 안쪽만 갱신되므로 중복이 쌓이지 않는다.

```
<!-- paseo-setup:start -->
... 라우팅 규칙 ...
<!-- paseo-setup:end -->
```

## 설치 전 알아둘 것

- **로그인은 필요 없다.** 설치는 전부 파일 읽기/쓰기다. 네트워크를 타지 않고 인증을 건드리지 않는다.
  클로드·코덱스 CLI가 아직 없어도 설치되고, 나중에 깔면 그때부터 규칙이 먹는다.
- `python3` 가 필요하다 (JSON 패치용). macOS/Linux 기준.
- `~/.paseo/config.json` 은 **Paseo 앱을 최소 한 번 실행해야 생긴다.** 그 전에 돌리면
  1·2단계만 끝나고 3단계는 건너뛴다. 앱을 한 번 켠 뒤 스크립트를 다시 돌리면 된다.
- 모든 변경 대상은 실행 시각이 붙은 `.bak-YYYYmmdd-HHMMSS` 백업을 남긴다.

### Codex 플랜 제약

라우팅 표는 보안·난제·되돌릴 수 없는 작업에 `sol` 을 지정한다. 그런데 **Codex Free·Go 플랜은
Sol 을 쓸 수 없다**(Plus 이상부터 제공). Free/Go 사용자는 해당 행을 `terra` 로 내려 쓰되,
보안 작업에서는 정적분석 도구 비중을 더 높여야 한다 — `terra` 의 ExploitBench 는 52.9% 로
Sol(73.5%)보다 크게 낮다. 플랜별 실제 한도는 계정의 Codex Usage Dashboard 가 기준이다.

## 핵심 규칙 요약

**역할** — 오케스트레이터(기획·분해·판정·승인)와 서브에이전트(실행)를 나눈다. 서브에이전트 기본은 코덱스.
클로드는 선택 사항이고, 없으면 폴백으로 간다.

**선언·승인** — 서브에이전트를 띄우기 전에 프로바이더·모델·추론강도·범위·쓰기권한·위임 이유를
선언하고 **매 실행마다** 승인받는다. 포괄 허가는 면제가 아니다.

**라우팅** — 모델 격차는 작업 난이도에 비례한다. 일상 코딩에서 Sol-Luna 격차는
벤치마크에 따라 1.9~5.5%p지만 익스플로잇에서는 40.3%p다.
모델을 올리는 것보다 같은 모델 안에서 강도를 올리는 쪽이 훨씬 싸다
(Luna high→max 는 +5점에 $0.03, Luna high→Sol high 는 +10점에 27배).

| 어떤 일인가 | 설정 |
|---|---|
| 폴링·다운로드·파일 찾기 | `luna` low |
| **조사·리서치·코드 읽기** (기본값) | `luna` high |
| 대량 기계적 변환 | `luna` high N기 병렬 |
| 일상 코드 생성 | `luna` max → 오케스트레이터 검수 필수 (실행까지 확인) |
| 입력 200K 초과 장문 | `terra` high~max |
| 디버깅·근본원인 | 가설별 `luna` high 팬아웃 → `sol` xhigh 수렴 |
| 보안·암호·동시성·결제·인증 | `sol` xhigh + 보안 프로토콜 |
| 되돌릴 수 없는 것 | `sol` xhigh + 사전 승인 |
| 분해 불가 최난도 | `sol` max |

**금지** — `sol` low(`luna` max가 더 싸고 강하다), `ultra`(Paseo에서 `fork_turns`·depth를 못 건다).

**클로드가 확실히 나은 건 셋뿐** — 프로덕션 테스트 작성 / 고위험 보안 2차 검토 / 272K 초과 단일 요청.
코덱스 단독이면 각각 테스트 실제 실행·정적분석 도구 병행·샤딩으로 대체한다.
심층 리서치·초장문 품질·지시 준수는 클로드 우위 근거가 없다.

**코덱스가 쓴 코드는 검수 없이 머지 금지** — GPT-5.5 대비 Sol은 기능 테스트 통과율이 +3.33%p인데
critical 취약점 밀도는 6.25배다. 통과율이 올라 눈에 안 띄니 오히려 더 위험하다.

전체 근거와 출처는 `rules/model-routing.md` 참조.

수정하면 이 저장소에 커밋하고, 각 PC에서 `git pull` 후 설치 스크립트를 다시 실행한다.
