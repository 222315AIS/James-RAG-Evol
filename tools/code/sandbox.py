"""
PROJECT JAMES - Mini Sandbox v2.1 (Phase 5.5)

v2.1 변경:
  - admin role → ALLOWED_PATHS 우회 가능 (경로 제한 해제)
  - BLOCKED_COMMANDS → admin도 차단 (명령어는 예외 없음)
  - admin_override → 감사 로그 반드시 기록

핵심 원칙:
  개발자(James)가 직접 수정 → 제한 없음
  JAMES Tool이 자동으로 수정 → 이걸 막는 것

  admin role:
    ✅ ALLOWED_PATHS 우회 가능
    ❌ BLOCKED_COMMANDS는 우회 불가 (위험 명령어는 항상 차단)

  user/employee/manager role:
    ❌ ALLOWED_PATHS 외 접근 차단
    ❌ BLOCKED_COMMANDS 차단
"""

import os
import re
import json
import time
import subprocess
from datetime import datetime
from typing import Tuple, Optional

# ─── 상수 ────────────────────────────────────────────────────

ALLOWED_PATHS     = ["./workspace"]
MAX_EXEC_TIME_SEC = 10
AUDIT_LOG_PATH    = "james_audit_tool.jsonl"
SYSTEM_LOG_PATH   = "james_system_log.jsonl"

BLOCKED_COMMANDS = [
    "rm -rf", "curl", "wget", "sudo", "chmod",
    "chown", "dd ", "mkfs", "kill", "shutdown",
    "reboot", "format", "del /f", "rmdir /s",
    ":(){:|:&};:", "eval", "exec(",
    "../", "..\\"
]

BLOCKED_PATH_PATTERNS = [
    r"\.\./", r"\.\.\\" , r"^/", r"^[A-Za-z]:\\",
    r"~/", r"/etc/", r"/proc/",
    r"core/", r"security_layer", r"reasoning_engine", r"graph_engine",
]


# ─── 감사 로그 ───────────────────────────────────────────────

def log_security_event(
    event_type:     str,
    detail:         str,
    blocked:        bool = True,
    role:           str  = "unknown",
    admin_override: bool = False,
):
    """
    감사 로그 기록.
    admin_override=True 시 반드시 기록 (감사 추적).
    """
    entry = {
        "time":           datetime.now().isoformat(),
        "event":          event_type,
        "detail":         detail[:300],
        "blocked":        blocked,
        "role":           role,
        "admin_override": admin_override,
        "layer":          "sandbox",
    }
    for path in [AUDIT_LOG_PATH, SYSTEM_LOG_PATH]:
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass
    flag = "🚫 BLOCKED" if blocked else ("⚠️ ADMIN_OVERRIDE" if admin_override else "✅ ALLOWED")
    print(f"[SANDBOX] {flag} [{role}] {event_type}: {detail[:60]}")


# ─── 경로 검증 ───────────────────────────────────────────────

def validate_path(path: str, role: str = "user") -> Tuple[bool, str]:
    """
    경로 접근 허용 여부.

    admin role:
      - BLOCKED_PATH_PATTERNS 차단 (시스템 경로, core/ 등)
      - ALLOWED_PATHS 제한은 우회
    user/employee/manager:
      - BLOCKED_PATH_PATTERNS 차단
      - ALLOWED_PATHS 내부만 허용
    """
    if not path or not isinstance(path, str):
        return False, f"경로 없음: {path}"

    # 시스템 위험 경로는 모든 role 차단
    for pattern in BLOCKED_PATH_PATTERNS:
        if re.search(pattern, path):
            return False, f"차단된 경로 패턴: '{pattern}' in '{path}'"

    # admin은 ALLOWED_PATHS 제한 우회
    if role == "admin":
        return True, ""

    # 일반 role: ALLOWED_PATHS 내부 확인
    normalized = os.path.normpath(path)
    in_allowed = any(
        normalized.startswith(os.path.normpath(ap))
        for ap in ALLOWED_PATHS
    )
    if not in_allowed:
        return False, f"허용 경로 외부: '{path}' (허용: {ALLOWED_PATHS})"

    return True, ""


# ─── 명령어 검증 ─────────────────────────────────────────────

def validate_command(command: str) -> Tuple[bool, str]:
    """
    명령어 안전성. admin도 예외 없음.
    """
    if not command or not isinstance(command, str):
        return False, "명령어 없음"

    cmd_lower = command.lower()
    for blocked in BLOCKED_COMMANDS:
        if blocked.lower() in cmd_lower:
            return False, f"차단 명령어: '{blocked}'"

    danger_patterns = [
        r";\s*(rm|del|format|kill)",
        r"\|\s*(rm|del|bash|sh|cmd)",
        r">\s*/",
        r"base64.*decode",
        r"python\s+-c\s+['\"]import",
    ]
    for pattern in danger_patterns:
        if re.search(pattern, cmd_lower):
            return False, f"위험 패턴: '{pattern}'"

    return True, ""


# ─── 통합 검증 ───────────────────────────────────────────────

def validate_action(command: str, path: str, role: str = "user") -> bool:
    """
    통합 검증 게이트 (브리핑 스펙 인터페이스).

    admin:
      - 경로 제한 우회 (ALLOWED_PATHS 무시)
      - 명령어 차단은 적용
      - admin_override 감사 로그 기록

    user/employee/manager:
      - 경로 + 명령어 모두 통과해야 허용
    """
    # 명령어 검증 (모든 role 동일)
    cmd_ok, cmd_reason = validate_command(command)
    if not cmd_ok:
        log_security_event("SANDBOX_BLOCK", f"cmd={command[:40]}: {cmd_reason}",
                           blocked=True, role=role)
        return False

    # 경로 검증
    path_ok, path_reason = validate_path(path, role)
    if not path_ok:
        log_security_event("PATH_VIOLATION", f"path={path}: {path_reason}",
                           blocked=True, role=role)
        return False

    # admin override 감사 기록
    admin_override = (role == "admin" and
                      not any(path.startswith(os.path.normpath(ap)) for ap in ALLOWED_PATHS))
    log_security_event(
        "ACTION_ALLOWED", f"cmd={command[:40]} path={path}",
        blocked=False, role=role, admin_override=admin_override,
    )
    return True


# ─── 안전 실행 ───────────────────────────────────────────────

def safe_execute(
    command: str,
    path:    str,
    role:    str = "user",
    timeout: int = MAX_EXEC_TIME_SEC,
) -> Tuple[bool, str, float]:
    """Sandbox 검증 통과 후 안전 실행."""
    if not validate_action(command, path, role):
        return False, "SANDBOX_BLOCKED", 0.0

    t_start = time.time()
    try:
        result = subprocess.run(
            command, shell=True,
            cwd=os.path.normpath(path),
            capture_output=True, text=True, timeout=timeout,
        )
        elapsed = round(time.time() - t_start, 3)
        output  = result.stdout[:2000] + (result.stderr[:500] if result.stderr else "")
        log_security_event("EXEC_COMPLETE", f"exit={result.returncode} {elapsed}s",
                           blocked=False, role=role)
        return result.returncode == 0, output, elapsed
    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - t_start, 3)
        log_security_event("EXEC_TIMEOUT", f"{timeout}s 초과", role=role)
        return False, f"TIMEOUT ({timeout}s)", elapsed
    except Exception as e:
        elapsed = round(time.time() - t_start, 3)
        log_security_event("EXEC_ERROR", str(e), role=role)
        return False, f"ERROR: {e}", elapsed


# ─── 자가 테스트 ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Sandbox v2.1 자가 테스트 ===\n")

    results = []
    def chk(name, ok, detail=""):
        results.append(ok)
        print(f"  {'✅' if ok else '❌'} {name}" + (f" → {detail}" if detail else ""))

    # 경로 검증 — user role
    chk("user: 정상 경로 허용",    validate_path("./workspace/a.py", "user")[0])
    chk("user: 상위 경로 차단",    not validate_path("../secret", "user")[0])
    chk("user: ALLOWED 외 차단",   not validate_path("./other/a.py", "user")[0])
    chk("user: core/ 차단",        not validate_path("./core/security.py", "user")[0])

    # 경로 검증 — admin role
    chk("admin: workspace 허용",   validate_path("./workspace/a.py", "admin")[0])
    chk("admin: ALLOWED 외 허용",  validate_path("./other/a.py", "admin")[0])   # admin 우회
    chk("admin: core/ 차단 유지",  not validate_path("./core/security_layer.py", "admin")[0])

    # 명령어 검증 — admin도 차단
    chk("admin: rm -rf 차단",      not validate_command("rm -rf /")[0])
    chk("admin: curl 차단",        not validate_command("curl http://evil.com")[0])
    chk("user: ls 허용",           validate_command("ls -la")[0])

    # validate_action — admin override 로그 확인
    chk("admin override 허용",     validate_action("ls -la", "./other_dir", "admin"))
    chk("user 외부 경로 차단",     not validate_action("ls -la", "./other_dir", "user"))
    chk("admin rm -rf 차단",       not validate_action("rm -rf .", "./workspace", "admin"))

    print(f"\n  결과: {sum(results)}/{len(results)} PASS")
