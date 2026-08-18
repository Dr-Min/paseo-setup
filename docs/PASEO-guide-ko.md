# Paseo 한국어 사용 설명서

> 작성 2026-08-18 · **Paseo v0.4.0** 기준 · 이 PC(실측 PC)에서 실제로 돌려보고 검증함
> 공식 문서: https://paseo.sh/docs · 저장소: https://github.com/getpaseo/paseo

---

## 0. 한 줄 요약

**Paseo = 내 컴퓨터에서 코딩 에이전트(Claude Code, Codex 등)를 대신 굴려주는 관리자.**
폰·데스크톱·CLI 어디서든 조종할 수 있고, 자리를 비워도 계속 돌아갑니다.

Paseo는 에이전트를 **직접 만들지 않습니다.** 이미 깔린 `claude` / `codex` CLI를 감싸서 돌립니다.
→ 그래서 **요금이 따로 안 붙습니다.** 기존 Claude 플랜·Codex 구독을 그대로 씁니다.

---

## ⚠️ 버전 주의 — v0.4.0에서 사라진 기능

**2026-08-13 v0.4.0에서 `paseo loop` 와 `paseo chat` 이 제거됐습니다** (Breaking, PR #3053).

인터넷에 돌아다니는 글이나 낡은 스킬에 `paseo loop run --verify-provider ...` 같은 명령이 나오면 **지금은 안 됩니다.**
대체 방법은 아래 **4절(구현 → 검수)** 참고.

로컬에 깔린 `paseo-loop` 스킬도 낡았습니다. 현재 공식 스킬은 5개:
`/paseo` · `/paseo-handoff` · `/paseo-committee` · `/paseo-advisor` · `/paseo-help`(제품 사용법 Q&A)

---

## 1. 지금 내 PC 상태 (실측)

| 항목 | 값 |
|---|---|
| 버전 | **0.4.0** (CLI·데몬 동일) |
| 설치 위치 | `C:\Program Files\Paseo\Paseo.exe` |
| CLI 실체 | `C:\Program Files\Paseo\resources\bin\paseo.cmd` |
| 데몬 | 데스크톱 앱이 자동 시작·관리 |
| 데이터 | `C:\Users\<사용자>\.paseo` |
| 로그 | `C:\Users\<사용자>\.paseo\daemon.log` |

> **앱이 켜지면 CLI도 같이 자동 업데이트됩니다.** 명령이 갑자기 안 먹으면 `paseo --version` 부터 확인하세요.

### provider와 모델 ID

```
claude : claude-opus-5       ← 현재 기본값. 1M 컨텍스트
         claude-fable-5      ← 최강·최고가. 1M 컨텍스트 ([1m] 표기는 별칭일 뿐 같은 모델)
         claude-sonnet-5     ← 일상용 (200K, [1m] 변형 있음)
         claude-haiku-4-5    ← 가장 쌈·빠름. 추론강도 옵션 자체가 없음
         구세대: opus-4-8 / 4-7 / 4-6, sonnet-4-6 (각각 [1m] 변형 있음)

codex  : gpt-5.6-sol         ← 프론티어 (현재 기본값). 크레딧 최대소모. 실패비용 큰 난제·장기 에이전트·긴 컨텍스트만
         gpt-5.6-terra       ← 밸런스형. 긴 문서(256K+) 리서치는 luna 대신 이걸로 (Luna는 장문에서 급락)
         gpt-5.6-luna        ← ★ 기본값 추천: luna + thinking high = Terra medium급 성능, 크레딧은 Sol의 1/25
         gpt-5.5             ← 구세대. 신규 작업에 쓸 이유 없음 (Sol이 같은 값에 전면 우위)
         gpt-5.4 / 5.4-mini  ← 구세대. luna에 밀림
         gpt-5.3-codex-spark ← 초고속 코딩 특화
```
> 크레딧 가중치 (입력/캐시/출력 per MTok): Sol·5.5=125/12.5/750 · Terra=50/5/300 · **Luna=5/0.5/30**
> ⚠️ 2026-08-18 저녁 실측: GPT-5.6 3형제(sol/terra/luna)가 추가됨. 위 목록이 낡아 보이면 `list_models`로 재확인할 것.

그 외 provider (2026-08-18 저녁 실측): `copilot`·`pi` 연결 안 됨 · `opencode` 에러 상태 · `omp` 비활성 → **실제로 쓸 수 있는 건 claude와 codex 둘뿐**

### 모드 ID (실측 확인 — 표시 이름 말고 이 값을 쓸 것)

```
claude : plan · default · acceptEdits · auto · bypassPermissions
codex  : auto · auto-review · full-access
```

`plan`은 **편집 불가**라 검증자 역할에 딱 맞습니다.
`full-access` / `bypassPermissions`는 승인 없이 파일을 쓰고 명령을 실행합니다.

### 추론강도 (thinking) — 모델마다 지정 가능 (2026-08-18 실측)

기본값은 거의 전부 **high**. 단순 작업에 high는 낭비다 — 강도를 올리면 출력 토큰(=사용량·시간)이 늘어난다.

```
claude : off · low · medium · high(기본) · xhigh · max · ultracode
         (fable-5는 off 없음, haiku-4-5는 옵션 자체가 없음)
codex  : low · medium · high(기본) · xhigh · max
         (gpt-5.6-sol만 ultra 추가 — 자동 작업 위임 포함)
```

지정 방법:
- CLI: `paseo run --thinking low --provider codex/gpt-5.6-luna "단순 검색"`
- MCP/자연어: create_agent의 `settings.thinkingOptionId`, 또는 "추론강도 low로 해서"라고 말하면 됨

권장: 단순 검색·다운로드·툴 호출 = low, 일반 리서치 = medium~high, 검수·난제 = high 이상.

### 힉스필드

`~/.claude.json`과 `~/.codex/config.toml` 양쪽에 MCP가 전역 등록돼 있어
Paseo가 띄우는 에이전트가 **자동으로 상속**합니다. 따로 붙일 것 없음.
단 `higgsfield-*` 스킬은 claude 쪽에만 있으니 **영상/이미지 생성은 claude 에이전트에게** 시키세요.

### 커스텀 설정 (2026-08-19)

`~/.paseo/config.json`의 `appendSystemPrompt`에 **전역 운영 철칙 5줄**이 주입돼 있다 (검증자 수정금지·DONE 판정, 출처 명시, 과잉사고 금지, 파괴적 작업 제한, 한국어 보고). **파세오가 띄우는 모든 에이전트(provider 불문)에 자동 적용.** 백업: `config.json.bak-20260819`. 데몬 재시작 후부터 적용됨.

### PATH — 제일 먼저 할 것

`paseo`가 PATH에 없습니다. PowerShell 프로필에 추가:
```powershell
Set-Alias paseo "C:\Program Files\Paseo\resources\bin\paseo.cmd"
```
또는 `paseo onboard`를 한 번 돌리면 `~/.local/bin`에 자동으로 걸어줍니다.

---

## 2. 개념 4개만 알면 됩니다

```
프로젝트 (Project)          = 등록된 저장소 폴더
   └ 워크스페이스 (Workspace) = 실제 작업 디렉터리
        └ 에이전트 (Agent)     = 일하는 AI 하나
             └ 서브에이전트     = 그 AI가 부린 또 다른 AI
```

**워크스페이스 격리 방식이 제일 중요합니다:**

| 방식 | 뜻 | 언제 |
|---|---|---|
| `local` | 현재 폴더에서 그대로 작업 | 혼자 돌릴 때, 빠름 |
| `worktree` | git worktree로 **격리된 복사본** 생성 | **무인 운영은 무조건 이것** |

무인으로 돌릴 땐 반드시 worktree. 에이전트가 폭주해도 `main`이 안전합니다.

---

## 3. 기본 명령

```bash
paseo run "테스트 고쳐줘"          # 에이전트 시작 (기본: 끝날 때까지 대기)
paseo run --background "..."        # 바로 반환, 백그라운드로 계속  (-d 도 동일)
paseo ls                            # 에이전트 목록
paseo attach <id>                   # 출력 실시간으로 보기
paseo send <id> "린트도 고쳐줘"     # 이미 도는 에이전트에게 추가 지시
paseo logs <id>                     # 작업 타임라인
paseo inspect <id>                  # 상세 정보
paseo wait <id>                     # 끝날 때까지 대기 (마지막 응답도 보여줌)
paseo stop <id>                     # 중단
paseo archive <id>                  # 목록에서 치우기
```

**provider/모델/모드 지정:**
```bash
paseo run --provider codex --model gpt-5.5 --mode full-access "API 리팩터링"
paseo run --provider claude --model claude-fable-5 --mode plan "이 diff 검토해줘"
paseo run --provider codex/gpt-5.4 "..."     # provider/model 축약형도 됨
paseo run --provider codex/gpt-5.6-luna --thinking low "단순 검색"   # 추론강도 지정
paseo run --image shot.png "이 이미지 기준으로 ..."   # 이미지 첨부 (여러 번 사용 가능)
```

**격리된 브랜치에서 작업:**
```bash
paseo run --new-workspace worktree --worktree-mode branch-off \
  --new-branch feature/x --base main "기능 X 구현"
```

**기존 워크스페이스에 추가로 붙이기** (검증자를 워커와 같은 곳에 둘 때 필수):
```bash
paseo run --workspace <workspace-id> "..."
```

---

## 4. ★ 핵심 — 구현 → 검수 (v0.4.0 방식)

`paseo loop`이 사라졌으므로 **두 에이전트를 같은 워크스페이스에 순서대로** 띄웁니다.
이게 공식 문서의 `Implement, then review` 워크플로입니다.

### 방법 A — CLI 수동 (실측 검증 완료)

```bash
# 1단계: 워커가 구현
paseo run --background --title worker \
  --provider codex --model gpt-5.5 --mode full-access \
  "<작업 지시>"
# → 출력에 AGENT ID와 workspace id가 찍힘

paseo wait <worker-id>

# 2단계: 검증자를 같은 워크스페이스에 (반드시 --workspace)
paseo run --background --title verifier \
  --workspace <workspace-id> \
  --provider claude --model claude-fable-5 --mode plan \
  "검증만 해라. 파일을 수정·생성·삭제하지 마라. 'npm test'를 직접 실행하고 변경된 파일을 읽어라. 실행한 명령과 그 출력을 그대로 인용해라. 마지막 줄에 DONE=true 또는 DONE=false와 한 줄 이유를 써라."

paseo wait <verifier-id>
```

검증자에 **`--mode plan`** 을 주는 게 핵심입니다. 편집 권한 자체가 없어서 실수로 코드를 못 만집니다.

### 방법 B — 말로 시키기 (더 편함)

`Settings → 내 호스트 → Agents → Enable Paseo tools` 켜고, 에이전트에게 한국어로:

> worktree 격리 워크스페이스를 만들고 워커를 띄워서 이 기능을 구현시켜.
> 끝나면 **같은 워크스페이스에** 두 번째 서브에이전트를 만들어서 diff를
> 정확성·누락된 테스트·불필요한 복잡도 관점으로 리뷰하게 하고, 결과를 여기로 가져와.

두 번째 에이전트는 **워커의 파일은 보되 대화 맥락은 공유하지 않아서** 리뷰가 더 독립적입니다.

### 반복(수렴)이 필요하면 — heartbeat

`loop`의 자동 반복을 대신합니다. 크론 주기로 같은 대화를 깨웁니다.

```bash
paseo heartbeat create --cron "*/10 * * * *" \
  "테스트가 아직 실패하면 계속 고쳐라. 전부 통과하거나 2시간 지나면 멈춰라."
paseo heartbeat delete <id>
```

### 검증자 프롬프트 철칙

> **"수정 제안하지 말고 사실만 검증해라"** 를 반드시 넣으세요.

검증자가 코드를 직접 고치기 시작하면 두 모델이 서로의 결정을 덮어써서 결과물이 산으로 갑니다.
**코드를 만지는 손은 하나만.**

좋은 검증자 프롬프트의 조건:
- 사실 확인만 한다 (고치지 않는다)
- **직접 명령을 실행**하고 그 출력을 근거로 인용한다
- "done"의 기준을 구체적으로 못박는다
- 마지막 줄에 `DONE=true/false`처럼 **파싱 가능한 결론**을 요구한다

---

## 5. 스케줄 vs 하트비트

| | 하트비트 (heartbeat) | 스케줄 (schedule) |
|---|---|---|
| 결과가 가는 곳 | **지금 이 대화로 되돌아옴** | 매번 **새 에이전트**가 생김 |
| 쓰임 | 진행 중인 작업 계속 밀어붙이기, CI 감시 | 매일 아침 트리아지 같은 독립 작업 |
| 수정 | `update`로 주기 변경 | `update`로 수정 |

```bash
paseo schedule create --cron "0 9 * * *" --provider codex "어제 이슈 정리해줘"
paseo schedule ls / inspect / logs / pause / resume / run-once / update / delete
```

---

## 6. 폰에서 접속하기

**데스크톱 앱:** `Settings → 내 호스트 → Pair Device`
→ QR 코드를 폰의 Paseo 앱으로 스캔, 또는 페어링 링크 복사해서 붙여넣기.

**연결 방식:**
- **릴레이 (권장)** — 데몬이 `relay.paseo.sh`로 **밖으로** 나가서 만납니다. 포트 개방 불필요, 종단간 암호화
- **직접 연결** — TCP / Tailscale / VPN으로 주소 직접 입력

> ⚠️ **PC가 켜져 있어야 합니다.** 절전 모드로 들어가면 끊깁니다.
> 24시간 운영은 절전 해제 필수, 또는 VPS에 Docker로 별도 데몬:
> ```bash
> docker run -d -p 6767:6767 -e PASEO_PASSWORD=change-me \
>   -v "$PWD/paseo-home:/home/paseo" -v "$PWD:/workspace" \
>   ghcr.io/getpaseo/paseo:latest
> ```
> Docker 이미지는 **웹 UI도 같이 서빙**합니다 (`http://localhost:6767`).
> 데스크톱 앱이 관리하는 데몬은 웹 UI를 서빙하지 않습니다.

---

## 7. Paseo 서브에이전트가 특별한 이유

|  | 일반(네이티브) 서브에이전트 | Paseo 서브에이전트 |
|---|---|---|
| provider | 부모와 **같은 것만** | **아무거나** (Claude → Codex 가능) |
| 작업 디렉터리 | 부모가 결정 | 내가 지정 |
| 추가 지시 | 불가 | 가능 |
| 볼 수 있는 것 | 읽기 전용 타임라인 | 완전한 세션 |

**Paseo 서브에이전트만 provider 경계를 넘습니다.** 이게 Paseo를 쓰는 핵심 이유입니다.

---

## 8. 세션 가져오기 (실측 확인됨)

**Paseo가 만든 세션은 각 provider의 표준 저장소에 그대로 쌓입니다.** 확인 결과:

| provider | 저장 위치 | 이어서 열기 |
|---|---|---|
| codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` (`originator: codex_app_server_daemon`) | `codex resume <id>` |
| claude | `~/.claude/projects/<경로인코딩>/<세션UUID>.jsonl` | `claude --resume <UUID>` |

### 양방향 왕복 — 실측 검증 완료 (2026-08-18)

**핵심: "복사"가 아니라 같은 파일을 번갈아 여는 것입니다.**

```
        하나의 세션 = 하나의 .jsonl 파일
                    ↕
   Claude Code  ←──────────→  Paseo
        둘 다 같은 파일에 이어 씁니다
```

Paseo는 자기만의 대화 DB를 만들지 않습니다. Claude Code와 **똑같은 저장소**를 씁니다.
그래서 컨텍스트 손실 지점이 원리적으로 없고, **왕복 횟수에 제한이 없습니다.**

**Paseo → Claude Code** (검증됨)
```bash
claude --resume <세션UUID>
claude --resume                # 인자 없이 치면 선택창
```
Paseo가 만든 리뷰어 세션을 열었더니 검증 대상 함수명·최종 판정(DONE=true)·테스트 개수를 정확히 기억했습니다.

**Claude Code → Paseo** (검증됨)
```bash
paseo agent import <세션UUID> --provider claude --cwd <작업폴더>
```
임포트 후 질문하니 이전 대화의 세부사항(필터 쿼리, 소급 적용 건수까지)을 그대로 기억했습니다.

**Paseo에서 추가한 턴이 다시 Claude Code에 보이는지** (검증됨)
Paseo에서 한 턴 더 주고받은 뒤 `claude --resume`으로 열었더니, **Paseo에서 보낸 문장을 그대로 인용**했습니다.
파일을 확인해보니 새 세션이 생긴 게 아니라 **원본 `.jsonl`의 마지막 줄로 추가**돼 있었습니다 (sessionId 동일).

### 제약 4가지

**① provider를 넘나들 수 없습니다.**
codex 세션은 Claude Code에서 못 엽니다. 저장소가 아예 다릅니다.
claude↔claude, codex↔codex만 가능. (codex는 `codex resume <id>`)

**② 동시에 양쪽에서 열지 마세요.**
같은 `.jsonl`을 두 프로세스가 쓰면 순서가 꼬입니다. **한쪽을 닫고** 넘기세요.

**③ 작업 폴더(cwd)가 맞아야 합니다.**
세션은 경로별로 폴더가 갈립니다. `--cwd`를 원래 경로로 줘야 찾습니다.

**④ 넘어가는 건 "대화"지 "Paseo 상태"가 아닙니다.**
제목·라벨·워크스페이스 연결 같은 Paseo 메타데이터는 새로 붙습니다. 대화 내용과 맥락만 그대로입니다.

> 💡 앱에서 **이미 열어둔** 세션은 파일이 바뀌어도 화면 갱신이 안 될 수 있습니다. 닫았다 다시 여세요.
> 💡 안 보인다고 느껴지면 **세션 ID를 먼저 확인**하세요. 다른 세션을 보고 있을 가능성이 큽니다.

---

## 9. 문제 생기면 (디버깅 순서)

```bash
# 1. provider가 제대로 잡혔나 — 제일 유용
paseo provider diagnostic claude
paseo provider diagnostic codex --json

# 2. 데몬 상태
paseo daemon status

# 3. 로그
tail -n 200 ~/.paseo/daemon.log
```

`provider diagnostic`은 데몬이 실제로 쓰는 명령어, PATH, 셸, 바이너리 위치, 버전, 모델 개수까지 다 보여줍니다.

### 실제로 겪은 문제 2가지

**① `Failed to create agent: failed to load configuration: config.toml:5:16: unknown variant 'default'`**
→ `~/.codex/config.toml`의 `service_tier = "default"` 가 원인. codex 0.130.0은 `fast` 또는 `flex`만 받습니다.
→ **2026-08-18에 이 줄을 주석 처리했습니다.** 백업: `~/.codex/config.toml.bak-20260818`
→ 이건 Paseo 문제가 아니라 codex 자체 문제였습니다 (`codex login status`도 똑같이 실패했음).

**② claude 에이전트가 `Not logged in · Please run /login` 만 뱉음**
→ Paseo는 시스템에 설치된 `claude` CLI를 그대로 씁니다. 그 CLI가 별도로 로그인돼 있어야 합니다.
→ 확인: `claude auth status` → `"loggedIn": false` 면 터미널에서 `claude` 실행 후 `/login`.
→ Claude 데스크톱 앱에 로그인돼 있어도 **CLI 로그인은 별개**입니다.

> ⛔ **데몬을 함부로 재시작하지 마세요.** 돌고 있는 에이전트가 전부 죽습니다.

---

## 10. 치트시트

```bash
# 상태 확인
paseo --version
paseo provider ls
paseo provider models claude
paseo provider diagnostic codex

# 격리 워크스페이스 만들고 작업
paseo workspace create --isolation worktree --mode branch-off --new-branch auto-work --base main
paseo run --workspace <id> --provider codex --mode full-access "작업 내용"

# 구현 → 검수 (가장 많이 쓸 패턴)
paseo run -d --title worker --provider codex --model gpt-5.5 --mode full-access "<작업>"
paseo wait <worker-id>
paseo run -d --title verifier --workspace <ws-id> --provider claude --model claude-fable-5 --mode plan \
  "검증만. 수정 금지. 명령 직접 실행하고 출력 인용. 마지막 줄에 DONE=true/false."
paseo wait <verifier-id>

# 감시 / 정리
paseo ls
paseo attach <id>
paseo archive <id>
```

---

## 11. 실전 교훈 (2026-08-18 실제 테스트에서 얻음)

한국어 자연어 한 줄로 "코덱스 구현 → 하이쿠 검수" 전 과정을 성공시키며 확인한 것들.

### ① CLI로 보낼 때 프롬프트는 반드시 **한 줄**로

`paseo.cmd`는 배치 트램폴린이라 인자를 `%*`로 넘깁니다. **cmd.exe가 개행에서 잘라먹습니다.**
여러 줄 프롬프트를 보내면 **첫 줄만 도착**하고, 에이전트는 무슨 일인지 모른 채 스스로 일을 지어냅니다.

실제로 이것 때문에 두 번 실패했습니다. 앱 채팅창에서 입력할 땐 상관없습니다.

### ② **"Paseo로"** 라고 말해야 합니다

오케스트레이터는 네이티브 `Task` 툴과 Paseo 도구를 **둘 다** 갖고 있습니다.
그냥 "서브에이전트 띄워"라고 하면 네이티브를 쓸 수 있고, 그러면 **provider 경계를 못 넘습니다.**

```
❌  코덱스 서브에이전트 띄워서 이거 시켜
✅  Paseo로 코덱스 서브에이전트 띄워서 이거 시켜
```
공식 문서 예시가 전부 `Use Paseo to…`로 시작하는 이유입니다.

### ③ 서브에이전트 **모드를 지정**하세요

Paseo가 만드는 서브에이전트의 기본 모드는 **Always Ask**입니다.
무인으로 돌리면 Bash 승인 대기에서 계속 멈춥니다.

> …리뷰어를 만들되 **mode 를 bypassPermissions 로** 지정해서 승인 대기 없이 실행하게 해라.

오케스트레이터가 `Respond To Permission` 도구로 대신 승인해주기도 하지만, 매 명령마다 왕복이라 느립니다.

> ⚠️ CLI의 `paseo permit allow`는 **버그가 있습니다.** `permit ls`에는 대기 중으로 뜨는데
> `allow`는 "No pending permissions"라고 거부합니다. 앱 UI나 오케스트레이터를 통해 승인하세요.

### ④ 리뷰어에게 **올바른 비교 기준**을 주세요

리뷰어가 `git diff HEAD`로 판단하면, 커밋되지 않은 이전 변경까지 섞여서 **오판**합니다.
실제로 1차 리뷰어가 이것 때문에 잘못된 실패 판정을 냈습니다.

> 비교 기준은 작업 시작 시점의 코드다. `git diff HEAD`는 오래된 커밋과 비교라 의미 없다.

### ⑤ 성공한 프롬프트 (그대로 복사해 쓰세요)

한 줄, "Paseo로" 명시, 모델·모드·워크스페이스 지정:

```
너는 오케스트레이터로 남아서 코드를 직접 짜지 말고, 반드시 Paseo를 써서(네이티브 Task 툴 말고) 서브에이전트를 만들어라. 1단계: Paseo로 codex 의 gpt-5.4-mini 서브에이전트를 이 워크스페이스에 띄워서 <작업>을 하게 해라. 2단계: 그게 끝나면 Paseo로 claude 의 claude-haiku-4-5 서브에이전트를 같은 워크스페이스에 mode 는 bypassPermissions 로 만들어 리뷰시켜라. 리뷰어는 파일을 수정하거나 만들거나 지우지 말고, 직접 명령을 실행해 사실만 확인하고, 실행한 명령과 출력을 그대로 인용하고, 마지막 줄에 DONE=true 또는 DONE=false 를 써라. 3단계: 둘 다 끝나면 나에게 한국어로 요약 보고해라.
```

**검증된 결과**: 오케스트레이터(Sonnet 5) → `codex/gpt-5.4-mini` 구현 → `claude/claude-haiku-4-5` 검증 → DONE=true.
리뷰어가 실제로 명령을 실행하고 출력을 인용했으며, 왕복 변환 스팟체크까지 자발적으로 수행했습니다.

---

## 12. 자연어 트리거 사전

| 하고 싶은 것 | 이렇게 말하세요 |
|---|---|
| 다른 모델에 위임 | "**Paseo로** 코덱스 띄워서 ~ 시켜" |
| 구현 후 검수 | "…끝나면 **같은 워크스페이스에** Paseo로 리뷰어 하나 더" |
| 막혔을 때 (2모델 근본원인 분석) | "**committee** 열어줘" / `/paseo-committee` |
| 2차 소견 | "**어드바이저** 붙여줘" / `/paseo-advisor` |
| 작업 이관 | "이거 **핸드오프** 해줘" / `/paseo-handoff` |
| 계속 밀기 (루프 대체) | "**하트비트** N분마다 걸어줘" |
| 정기 작업 | "매일 N시에 **스케줄** 만들어줘" |
| 안전 격리 | "**worktree 격리**해서" |
| PR 리뷰 | "**PR 42번 체크아웃**한 워크스페이스 만들어줘" |
| 리서치 병렬 | "Paseo로 서브에이전트 3개 만들어서 각각 ~ 조사시켜. 파일 수정 금지." |
| 상태 확인 | "지금 애들 뭐 해?" |
| 방향 전환 | "파서 워커한테 ~도 추가하라고 전해줘" |

모델 이름은 몰라도 됩니다. **"제일 싼 걸로"**, **"제일 강한 걸로 검수시켜"** 라고 하면 알아서 목록을 조회해서 고릅니다.

### 스킬 5개 요약

| 스킬 | 하는 일 | 편집 |
|---|---|---|
| `/paseo` | 기반 참조 사전 (직접 부를 일 거의 없음) | - |
| `/paseo-help` | 파세오 제품 사용법/설정/트러블슈팅 Q&A | - |
| `/paseo-handoff` | 맥락 통째로 다른 에이전트에 이관 | 함 |
| `/paseo-committee` | 서로 다른 provider 2개가 각자 근본원인 분석 → 계획 → 구현 후 재검토 | **안 함** |
| `/paseo-advisor` | 에이전트 1개가 판단만 제공 | **안 함** |

> ⛔ 로컬의 `/paseo-loop`은 **쓰지 마세요.** 삭제된 `paseo loop` 명령을 부르는 유령 스킬입니다.

---

## 13. 주의사항

1. **`--workspace`를 안 주면 매번 새 워크스페이스가 생깁니다.** 검증자는 반드시 워커의 워크스페이스로.
2. **검증자는 `--mode plan`.** 편집 권한을 아예 주지 마세요.
3. **`full-access` / `bypassPermissions`는 승인 없이 파일을 쓰고 명령을 실행합니다.** 반드시 worktree와 함께.
4. **힉스필드 생성은 크레딧을 태웁니다.** 영상/이미지 작업은 반복 횟수를 짧게.
5. **PC가 자면 폰 연결이 끊깁니다.** 24시간 운영은 절전 해제 필수.
6. **검증자에게 코드를 고치게 하지 마세요.** 손은 하나만.
7. **앱이 자동 업데이트되면 CLI 명령이 바뀔 수 있습니다.** (v0.4.0에서 `loop`·`chat` 제거됨)
