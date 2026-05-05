"""
PROJECT JAMES - Tool Registry (Phase 5.5)

Tool 등록 및 조회 단일 지점.
Tool 추가 시 Core 수정 없이 여기서만 등록.
"""

from typing import Dict, Optional
from tools.base_tool import BaseTool

# Tool 등록소
TOOLS: Dict[str, BaseTool] = {}


def register(tool: BaseTool):
    """Tool 등록."""
    TOOLS[tool.name] = tool
    print(f"[REGISTRY] Tool 등록: {tool.name}")


def get_tool(name: str) -> Optional[BaseTool]:
    return TOOLS.get(name)


def list_tools() -> Dict[str, str]:
    return {name: tool.description for name, tool in TOOLS.items()}


# ── 기본 Tool 자동 등록 ────────────────────────────────────────

def _auto_register():
    """서버 시작 시 기본 Tool 자동 등록."""
    try:
        from tools.code.read_file import ReadFileTool
        register(ReadFileTool())
    except ImportError:
        pass

    try:
        from tools.code.code_analyzer import CodeAnalyzeTool
        register(CodeAnalyzeTool())
    except ImportError:
        pass


_auto_register()
