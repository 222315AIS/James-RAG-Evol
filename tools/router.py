"""
PROJECT JAMES - Tool Router v2.1 (Phase 5.5)

역할:
  1. PROTECTED_FILES 체크 (환경변수로 관리)
  2. admin role → PROTECTED_FILES 우회 허용 + 감사 로그
  3. Tool 존재 / 권한 확인
  4. Tool 실행 위임

PROTECTED_FILES 관리:
  .env 또는 환경변수 JAMES_PROTECTED_FILES 수정으로 제어
  하드코딩 금지 — Phase 6 전환 시 목록에서 제거만 하면 됨

절대 금지:
  ❌ admin_override 감사 로그 누락
  ❌ PROTECTED_FILES 하드코딩
  ❌ shell_exec 구현 (Phase 6 이후)
"""

import os
import json
from datetime import datetime
from typing import Dict, Any

AUDIT_LOG_PATH = "james_audit_tool.jsonl"

# ─── PROTECTED_FILES (환경변수로 관리) ───────────────────────

PROTECTED_FILES: list = os.environ.get(
    "JAMES_PROTECTED_FILES",
    "core/graph_engine.py,"
    "core/security_layer.py,"
    "core/ontology.py,"
    "core/auth.py,"
    "core/reasoning_engine.py,"
    "core/graph_rag_engine.py,"
    "core/memory_loom.py,"
    "core/memory_trust.py,"
    "core/gemma_client.py,"
    "core/retrieval_engine.py"
).split(",")

PROTECTED_FILES = [f.strip() for f in PROTECTED_FILES if f.strip()]


def _log_tool_event(
    event:          str,
    action_name:    str,
    target:         str,
    role:           str,
    blocked:        bool,
    protected_block:bool = False,
    admin_override: bool = False,
    sandbox_block:  bool = False,
    exec_time_sec:  float = 0.0,
):
    """
    확장 감사 로그.
    브리핑 스펙: tool_used + protected_block + admin_override 필수 기록.
    """
    entry = {
        "time":            datetime.now().isoformat(),
        "event":           event,
        "tool_used":       action_name,
        "target_file":     target,
        "role":            role,
        "blocked":         blocked,
        "protected_block": protected_block,
        "admin_override":  admin_override,
        "sandbox_block":   sandbox_block,
        "exec_time_sec":   exec_time_sec,
        "layer":           "router",
    }
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    if blocked:
        reason = "PROTECTED" if protected_block else ("SANDBOX" if sandbox_block else "DENIED")
        print(f"[ROUTER] 🚫 BLOCK({reason}) [{role}] {action_name} → {target[:40]}")
    elif admin_override:
        print(f"[ROUTER] ⚠️  ADMIN_OVERRIDE [{role}] {action_name} → {target[:40]}")
    else:
        print(f"[ROUTER] ✅ ALLOW [{role}] {action_name} → {target[:40]}")


def _is_protected(target: str) -> bool:
    """target 경로가 PROTECTED_FILES 목록에 해당하는지 확인."""
    if not target:
        return False
    for protected in PROTECTED_FILES:
        # 경로 끝부분 매칭 (절대/상대 경로 모두 처리)
        if target.endswith(protected.strip()):
            return True
        if protected.strip() in target:
            return True
    return False


def execute_tool(action: dict, context: dict) -> dict:
    """
    Tool 실행 라우터.

    Args:
        action:  {"name": "read_file", "input": {"path": "...", ...}}
        context: {"user_role": "admin", "allow_fs": False, "allow_shell": False}

    Returns:
        {"success": bool, "result": Any, ...}
    """
    import time
    t_start    = time.time()
    action_name = action.get("name", "unknown")
    target      = action.get("input", {}).get("path", "")
    role        = context.get("user_role", "external")
    is_admin    = (role == "admin")

    # 1. PROTECTED_FILES 체크
    protected = _is_protected(target)
    if protected:
        if not is_admin:
            # admin 아닌 경우 → 차단
            _log_tool_event(
                "PROTECTED_BLOCK", action_name, target, role,
                blocked=True, protected_block=True,
            )
            return {"success": False, "result": None, "error": "PROTECTED",
                    "tool_used": action_name}
        else:
            # admin → 우회 허용 (반드시 감사 로그)
            _log_tool_event(
                "ADMIN_OVERRIDE", action_name, target, role,
                blocked=False, protected_block=True, admin_override=True,
            )

    # 2. Tool 존재 확인
    from tools.registry import TOOLS
    tool = TOOLS.get(action_name)
    if not tool:
        _log_tool_event("UNKNOWN_TOOL", action_name, target, role, blocked=True)
        return {"success": False, "result": None, "error": "UNKNOWN_TOOL",
                "tool_used": action_name}

    # 3. Tool 권한 확인
    if not tool.authorize(context):
        from core.security_layer import log_system_event
        log_system_event("tool_denied", f"tool={action_name} role={role}", role=role)
        _log_tool_event("TOOL_DENIED", action_name, target, role, blocked=True)
        return {"success": False, "result": None, "error": "DENIED",
                "tool_used": action_name}

    # 4. Tool 실행
    try:
        result = tool.execute(action["input"])
    except Exception as e:
        elapsed = round(time.time() - t_start, 3)
        _log_tool_event("TOOL_ERROR", action_name, target, role,
                        blocked=False, exec_time_sec=elapsed)
        return {"success": False, "result": None, "error": str(e),
                "tool_used": action_name}

    elapsed = round(time.time() - t_start, 3)
    _log_tool_event(
        "TOOL_EXECUTED", action_name, target, role,
        blocked=False,
        admin_override=is_admin and protected,
        exec_time_sec=elapsed,
    )
    return result


def get_protected_files() -> list:
    """현재 PROTECTED_FILES 목록 반환 (설정 확인용)."""
    return list(PROTECTED_FILES)


# ─── 자가 테스트 ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Router v2.1 자가 테스트 ===\n")
    print(f"PROTECTED_FILES ({len(PROTECTED_FILES)}개):")
    for f in PROTECTED_FILES:
        print(f"  • {f}")
    print()

    # protected 탐지 테스트
    tests = [
        ("core/security_layer.py",   True),
        ("core/graph_engine.py",     True),
        ("./workspace/app.py",       False),
        ("tools/router.py",          False),
        ("core/auth.py",             True),
    ]
    passed = 0
    for path, expect in tests:
        result = _is_protected(path)
        ok = result == expect
        passed += int(ok)
        print(f"  {'✅' if ok else '❌'} {path:35s} protected={result} (기대={expect})")

    print(f"\n  결과: {passed}/{len(tests)} PASS")
