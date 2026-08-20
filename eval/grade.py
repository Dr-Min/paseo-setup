#!/usr/bin/env python3
"""모델 대조 채점기.

사용법:  python3 grade.py [run_dir]
  run_dir 기본값은 이 파일 옆의 runs/ 에서 가장 최근 디렉터리.
  구조는  <run_dir>/<t1|t2|t3>/<모델이름>/solution.py

이 채점기는 구현을 보기 전에 작성됐다. 새 모델을 재측정할 때도
채점기를 고치지 마라 — 고치면 이전 회차와 비교가 성립하지 않는다.
"""
import importlib.util, os, sys, tempfile, threading, time, traceback

def load(path):
    spec = importlib.util.spec_from_file_location("sol_%d" % id(path), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def check(results, name, fn):
    try:
        ok = fn()
        results.append((name, bool(ok), "" if ok else "오답"))
    except Exception as e:
        results.append((name, False, "%s: %s" % (type(e).__name__, e)))

# ---------- T1: semver ----------
def grade_t1(mod):
    r, c = [], mod.compare
    def raises(a, b):
        try:
            c(a, b); return False
        except ValueError:
            return True
        except Exception:
            return False
    check(r, "기본 major",      lambda: c("2.0.0", "1.0.0") == 1)
    check(r, "기본 minor",      lambda: c("1.2.0", "1.10.0") == -1)
    check(r, "숫자 비교(문자열 아님)", lambda: c("1.0.10", "1.0.9") == 1)
    check(r, "동일",            lambda: c("1.2.3", "1.2.3") == 0)
    check(r, "prerelease < 정식", lambda: c("1.0.0-alpha", "1.0.0") == -1)
    check(r, "prerelease 순서",  lambda: c("1.0.0-alpha", "1.0.0-beta") == -1)
    check(r, "prerelease 숫자 식별자", lambda: c("1.0.0-alpha.1", "1.0.0-alpha.2") == -1)
    check(r, "숫자 < 영숫자",    lambda: c("1.0.0-1", "1.0.0-alpha") == -1)
    check(r, "식별자 개수 많은 쪽이 큼", lambda: c("1.0.0-alpha", "1.0.0-alpha.1") == -1)
    check(r, "빌드메타데이터 무시", lambda: c("1.0.0+build1", "1.0.0+build2") == 0)
    check(r, "빌드메타+prerelease", lambda: c("1.0.0-alpha+001", "1.0.0-alpha+999") == 0)
    check(r, "선행 0 거부",      lambda: raises("01.0.0", "1.0.0"))
    check(r, "prerelease 선행 0 거부", lambda: raises("1.0.0-01", "1.0.0"))
    check(r, "불완전 버전 거부",  lambda: raises("1.0", "1.0.0"))
    check(r, "빈 문자열 거부",    lambda: raises("", "1.0.0"))
    check(r, "음수 거부",        lambda: raises("-1.0.0", "1.0.0"))
    check(r, "공백 거부",        lambda: raises("1.0.0 ", "1.0.0"))
    check(r, "잘못된 문자 거부",  lambda: raises("1.0.0-alpha_1", "1.0.0"))
    return r

# ---------- T2: token bucket ----------
def grade_t2(mod):
    r, TB = [], mod.TokenBucket
    def initial_full():
        return TB(5, 1.0).try_acquire(5) is True
    def over_capacity():
        return TB(5, 1.0).try_acquire(6) is False
    def no_partial_consume():
        b = TB(5, 1.0)
        b.try_acquire(6)          # 실패해야 하고 차감도 없어야 함
        return b.try_acquire(5) is True
    def depletes():
        b = TB(3, 0.0)
        return [b.try_acquire() for _ in range(4)] == [True, True, True, False]
    def refills():
        b = TB(10, 100.0)
        b.try_acquire(10)
        time.sleep(0.15)          # 약 15토큰 충전분 -> capacity 10으로 상한
        return b.try_acquire(5) is True
    def caps_at_capacity():
        b = TB(5, 1000.0)
        time.sleep(0.05)          # 50토큰어치 시간이 흘러도 상한은 5
        got = sum(1 for _ in range(100) if b.try_acquire())
        return got <= 8           # 상한 초과 누적이면 훨씬 큰 값이 나옴
    def thread_safe():
        b = TB(1000, 0.0)
        got = []
        lock = threading.Lock()
        def worker():
            n = sum(1 for _ in range(500) if b.try_acquire())
            with lock:
                got.append(n)
        ts = [threading.Thread(target=worker) for _ in range(8)]
        for t in ts: t.start()
        for t in ts: t.join()
        return sum(got) == 1000   # 초과 발급되면 > 1000
    check(r, "초기 만충",            initial_full)
    check(r, "용량 초과 요청 거부",   over_capacity)
    check(r, "실패 시 부분 차감 없음", no_partial_consume)
    check(r, "고갈",                depletes)
    check(r, "시간 경과 충전",       refills)
    check(r, "용량 상한 준수",       caps_at_capacity)
    check(r, "동시성 8스레드 초과발급", thread_safe)
    return r

# ---------- T3: safe_join ----------
def grade_t3(mod):
    r, sj = [], mod.safe_join
    base = tempfile.mkdtemp()
    os.makedirs(os.path.join(base, "sub"), exist_ok=True)
    outside = tempfile.mkdtemp()
    def blocks(p):
        try:
            sj(base, p); return False
        except ValueError:
            return True
        except Exception:
            return False
    def allows(p):
        try:
            got = sj(base, p)
            return os.path.isabs(got) and (
                os.path.realpath(got) == os.path.realpath(os.path.join(base, p))
            )
        except Exception:
            return False
    check(r, "정상 파일 허용",        lambda: allows("a.txt"))
    check(r, "정상 하위경로 허용",     lambda: allows("sub/a.txt"))
    check(r, "단순 상위 탈출 차단",    lambda: blocks("../etc/passwd"))
    check(r, "깊은 상위 탈출 차단",    lambda: blocks("../../../../etc/passwd"))
    check(r, "중간 상위 탈출 차단",    lambda: blocks("sub/../../etc/passwd"))
    check(r, "절대경로 주입 차단",     lambda: blocks("/etc/passwd"))
    check(r, "선행 슬래시 차단",       lambda: blocks("//etc/passwd"))
    check(r, "널바이트 차단",         lambda: blocks("a.txt\x00.png"))
    check(r, "점점점 차단",           lambda: blocks(".."))
    def prefix_confusion():
        # base 와 문자열 접두사만 같은 형제 디렉터리로 나가면 차단해야 함
        sibling = base + "_evil"
        os.makedirs(sibling, exist_ok=True)
        return blocks(os.path.join("..", os.path.basename(sibling), "x"))
    check(r, "접두사 혼동 차단",       prefix_confusion)
    def symlink_escape():
        link = os.path.join(base, "link")
        try:
            if not os.path.lexists(link):
                os.symlink(outside, link)
        except OSError:
            return True  # 심볼릭 링크 못 만들면 스킵
        return blocks("link/secret.txt")
    check(r, "심볼릭 링크 탈출 차단",  symlink_escape)
    return r

GRADERS = {"t1": grade_t1, "t2": grade_t2, "t3": grade_t3}

def discover(root):
    """run_dir 안에 실제로 있는 모델 이름을 찾는다."""
    names = set()
    for task in ("t1", "t2", "t3"):
        d = os.path.join(root, task)
        if os.path.isdir(d):
            names.update(n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n)))
    return sorted(names)


def default_root():
    runs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
    if not os.path.isdir(runs):
        sys.exit("runs/ 가 없습니다. 경로를 인자로 주세요: python3 grade.py <run_dir>")
    dirs = sorted(d for d in os.listdir(runs) if os.path.isdir(os.path.join(runs, d)))
    if not dirs:
        sys.exit("runs/ 가 비어 있습니다.")
    return os.path.join(runs, dirs[-1])


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else default_root()
    models = discover(root)
    if not models:
        sys.exit("%s 에서 모델 디렉터리를 찾지 못했습니다." % root)
    print("run: %s\n모델: %s\n" % (root, ", ".join(models)))
    summary = {}
    for task in ("t1", "t2", "t3"):
        for model in models:
            path = os.path.join(root, task, model, "solution.py")
            key = "%s/%s" % (task, model)
            if not os.path.exists(path):
                print("== %s == 파일 없음" % key); summary[key] = (0, 0); continue
            try:
                mod = load(path)
            except Exception:
                print("== %s == import 실패\n%s" % (key, traceback.format_exc()))
                summary[key] = (0, 0); continue
            rows = GRADERS[task](mod)
            passed = sum(1 for _, ok, _ in rows if ok)
            summary[key] = (passed, len(rows))
            print("== %s == %d/%d" % (key, passed, len(rows)))
            for name, ok, msg in rows:
                if not ok:
                    print("   FAIL %s %s" % (name, ("(" + msg + ")") if msg else ""))
    print("\n---- 요약 ----")
    for task in ("t1", "t2", "t3"):
        cells = ["%s %d/%d" % ((m,) + summary.get("%s/%s" % (task, m), (0, 0)))
                 for m in models]
        print("%s  %s" % (task, "   ".join(cells)))
    totals = ["%s %d" % (m, sum(summary.get("%s/%s" % (t, m), (0, 0))[0]
                                for t in ("t1", "t2", "t3"))) for m in models]
    print("합계  %s" % "   ".join(totals))

if __name__ == "__main__":
    main()
