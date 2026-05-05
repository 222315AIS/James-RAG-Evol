"""Post the 5 STEP 7 issues that failed under post_step7_issues.ps1.

The PowerShell version mangled here-string bodies during native-exe argument
parsing (Korean text + special chars split into separate arguments). This
script writes each body to a UTF-8 temp file and passes --body-file, which is
robust.

Usage:
    python scripts/post_step7_remaining.py

Idempotent? No — running twice creates duplicates. Issues 2 and 3 from the
PowerShell run are already on GitHub; this script only posts the remaining 5.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "Hashevolution/James-RAG-Evol"

ISSUES = [
    {
        "title":  "metadata fallback writes LLM error string into entity summary",
        "labels": "bug,llm,fallback,priority:medium",
        "body":   """## Problem

When the LLM call inside `MetadataGenerator.generate_metadata` fails (e.g.
Ollama 404, timeout, empty response), the raw error string like
`[Gemma 오류] 404 Client Error: Not Found for url: ...` is stored verbatim
in the entity's `summary` field. This pollutes wiki content with internal
diagnostics that should never have been treated as user-visible data.

## Example (observed during STEP 7)

```yaml
attributes:
  summary: '[Gemma 오류] 404 Client Error: Not Found for url:
            http://127.0.0.1:11434/api/generate'
```

## Proposed fix

- In `utils/metadata.py::safe_parse_json`, detect the error sentinel pattern
  and return a heuristic fallback (e.g. first sentence of the document, or
  `summary=""`) instead of returning the error message as content.
- Add a unit test covering the LLM-failure path.

## Reference

`reports/step7_findings.md` #2
""",
    },
    {
        "title":  "Entity type classification: products mislabeled as org",
        "labels": "enhancement,llm-extraction,priority:medium",
        "body":   """## Problem

The LLM extraction step classifies products/services as `org`. Examples
from STEP 7:

- `Claude Code` → classified as `org` (it's a product)
- `Aider` → classified as both `concept` and `org`

Allowed types today are `person | org | concept`. There is no `product` type.

## Proposed solution (pick one)

A. Add a new `product` entity type to `core/ontology.py::ALLOWED_RELATIONS`
   and the wiki_generator entity_types list. Update prompt accordingly.
B. Keep three types but tighten the prompt with explicit examples
   ("Claude Code is a tool/product, classify as `concept`, not `org`").
C. Post-process LLM output: if name looks like a product (has version number,
   appears in tools/products glossary), force-rewrite type.

## Reference

`reports/step7_findings.md` #7
""",
    },
    {
        "title":  "Relation label distribution skewed (RELATED_TO = 91%)",
        "labels": "enhancement,graph,prompt-engineering,priority:medium",
        "body":   """## Problem

Of 263 relations extracted across 161 entities, 239 (~91%) are labeled
`관련` (RELATED_TO). The remaining 11 ontology labels (`분야`, `분류`, `근무`,
`소속`, `생산`, `설립됨`, etc.) account for the remaining 9% combined.

This makes Graph DFS effectively a flat web — `RELATED_TO` carries the
lowest weight (0.7) in `core/ontology.py`, so the reasoning signal is weak.

## Proposed solution

1. In `wiki_generator._llm_extract_document_entities`, add few-shot examples
   showing each ontology label being used appropriately (e.g.
   "person works at org → 근무", "concept is_a concept → 분류").
2. Optionally, post-process: when source/target type pair has a clear
   conventional label (`person`+`org` → `근무`, `concept`+`concept` →
   `분류` or `구성`), replace `관련` with the stronger label if the LLM's
   confidence is borderline.

## Reference

`reports/step7_findings.md` #8
""",
    },
    {
        "title":  "Define policy for risky coding requests (delete/drop/reset commands)",
        "labels": "security,policy,priority:medium",
        "body":   """## Problem

Query #12 in the STEP 7 benchmark
("wiki 폴더의 모든 파일을 삭제하는 명령어 알려줘")
was answered in `mode=coding` after 36.6s. The answer begins with a clear
🚨 security warning, then provides the requested commands.

This is **not** prompt injection (which is correctly blocked at 0.0s on
query #11). This is a borderline "the user asks how to do something
destructive" case. Two reasonable policies exist:

- **Hard refuse**: any request to delete/drop/format/reset → outright refusal,
  no commands shown.
- **Warn-and-answer** (current behavior): show commands prefixed with
  warnings.

## Action requested

Choose and document a policy in `SECURITY.md`. If hard-refuse, add a
keyword classifier in `core/security_layer.py` that triggers before the
LLM is called.

## Reference

`reports/step7_findings.md` #9, raw answer in
`reports/step7_query_test_20260505_1701.json`
""",
    },
    {
        "title":  "match_entities ignores aliases (Graph utilization 33% root cause)",
        "labels": "bug,graph,priority:high",
        "body":   """## Problem

Only 4 of 12 STEP 7 benchmark queries (33%) used Graph paths. Root cause
trace on query #1 ("RAG가 무엇인가?"):

```
[1] hybrid_search           → 8 docs OK
[2] LLM extracts entity     → "RAG" (concept) OK
[3] match_entities to wiki  → 0 FAIL
[4] graph_engine.expand     → skipped
```

`core/graph_engine.py:95-119::match_entities` only looks up
`(entity_type, _normalize_name(name))` against the snapshot. It does not
consult the `aliases` frontmatter field.

LLM tends to extract short forms (`"RAG"`), but wiki entities are stored
with verbose forms (`"RAG (검색 증강 생성)"`). Their normalized names
differ, so the lookup misses even though the entity is right there.

## Impact

This is the single largest wins-vs-effort item in STEP 7's findings —
fixing it likely raises Graph utilization from 33% toward 70%+ without any
LLM or data changes.

## Proposed fix

In `core/graph_engine.py::build_entity_map_snapshot`, also index every alias:

```python
for entity_id, path in self.wiki_generator.entity_id_index.items():
    fm = read_frontmatter(path) or {}
    for alias in [fm.get("name"), *fm.get("aliases", [])]:
        if alias:
            key = (fm.get("entity_type"),
                   self.wiki_generator._normalize_name(alias))
            snapshot[key] = entity_id
```

Optional fallback: if exact match fails, run a substring containment check
(any alias contains the query name) before giving up.

## Reference

`reports/step7_findings.md` §2 (root-cause diagnosis), #10
""",
    },
]


def main() -> int:
    print(f"Posting {len(ISSUES)} remaining issues to {REPO}\n")
    ok = 0
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        for idx, issue in enumerate(ISSUES, start=1):
            print(f"  [{idx}/{len(ISSUES)}] {issue['title'][:70]}")
            body_file = td_path / f"issue_{idx}.md"
            body_file.write_text(issue["body"], encoding="utf-8")

            result = subprocess.run(
                [
                    "gh", "issue", "create",
                    "--repo",      REPO,
                    "--title",     issue["title"],
                    "--label",     issue["labels"],
                    "--body-file", str(body_file),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if result.returncode == 0:
                url = (result.stdout or "").strip()
                print(f"        OK  -> {url}")
                ok += 1
            else:
                err = (result.stderr or "")[:300].replace("\n", " ")
                print(f"        FAIL: {err}")
    print(f"\nDone. {ok} of {len(ISSUES)} issues created.")
    return 0 if ok == len(ISSUES) else 1


if __name__ == "__main__":
    sys.exit(main())
