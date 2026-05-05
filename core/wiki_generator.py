# =========================
# PROJECT JAMES - FINAL STABLE WikiGenerator
# =========================

import os
import json
import yaml
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from config import WIKI_DIR
from core.gemma_client import GemmaClient
from core.vector_store import VectorStore
from utils.metadata import MetadataGenerator


class WikiGenerator:

    def __init__(self, source_type: str = "prod"):
        """
        [P4.5-1] source_type 분리
          source_type='prod' → wiki/entity/prod/{type}/
          source_type='test' → wiki/entity/test/{type}/
        """
        self.gemma_client = GemmaClient()
        self.metadata_gen = MetadataGenerator()
        self.vector_store = VectorStore()

        # [P4.5-1] source_type에 따라 entity 경로 분리
        self.source_type    = source_type if source_type in ("prod", "test") else "prod"
        self.wiki_base_path = Path(WIKI_DIR)
        self.entity_path    = self.wiki_base_path / "entity" / self.source_type

        self.entity_types = ["person", "concept", "org", "document"]

        for t in self.entity_types:
            (self.entity_path / t).mkdir(parents=True, exist_ok=True)

        self.index_path = self.wiki_base_path / "index.md"
        if not self.index_path.exists():
            self._create_index_template()

        self.entity_id_index: Dict[str, Path] = {}
        self._build_entity_id_index()


    def _create_index_template(self):
        """index.md 초기 템플릿 생성"""

        content = (
            "---\n"
            f'updated_at: "{datetime.now().isoformat()}"\n'
            "total_entities: 0\n"
            "---\n\n"
            "# 자메스 Wiki Index\n\n"
            "## person (0)\n\n"
            "## concept (0)\n\n"
            "## org (0)\n\n"
            "## document (0)\n"
        )

        self.index_path.write_text(content, encoding="utf-8")

    # =========================
    # INDEX BUILD
    # =========================

    def _build_entity_id_index(self):
        self.entity_id_index.clear()

        for t in self.entity_types:
            d = self.entity_path / t
            if not d.exists():
                continue

            for f in d.glob("*.md"):
                fm = self._read_frontmatter(f)
                if fm and fm.get("entity_id"):
                    self.entity_id_index[fm["entity_id"]] = f

        print(f"[INDEX] {len(self.entity_id_index)} entities loaded")

    def refresh_entity_map(self):
        self._build_entity_id_index()

    def _register_entity_id(self, entity_id: str, filepath: Path):
        self.entity_id_index[entity_id] = filepath

    # =========================
    # ID GENERATION (SECURE)
    # =========================

    def _generate_entity_id(self, name: str, entity_type: str) -> str:
        normalized = self._normalize_name(name)

        # 🔐 보안: SALT 추가
        SALT = "JAMES_SECURE_V1"
        raw = f"{normalized}_{entity_type}_{SALT}"

        h = hashlib.sha256(raw.encode()).hexdigest()[:8]   # graph_rag_engine 정규식 {8} 일치
        return f"e_{entity_type}_{h}"

    def _normalize_name(self, name: str) -> str:
        return re.sub(r"[^\w가-힣]", "_", name.strip().lower())

    # =========================
    # ENTITY SEARCH (FIXED)
    # =========================

    def _find_existing_entity_id(
        self,
        name: str,
        entity_type: Optional[str]
    ) -> Optional[str]:

        normalized = self._normalize_name(name)

        # 🔥 핵심 FIX: None 대응
        if entity_type:
            search_types = [entity_type]
        else:
            search_types = self.entity_types

        for t in search_types:
            d = self.entity_path / t
            if not d.exists():
                continue

            for f in d.glob("*.md"):
                fm = self._read_frontmatter(f)
                if not fm:
                    continue

                if fm.get("normalized_name") == normalized:
                    return fm.get("entity_id")

                for alias in fm.get("aliases", []):
                    if self._normalize_name(alias) == normalized:
                        return fm.get("entity_id")

        return None

    # =========================
    # FRONTMATTER
    # =========================

    def _read_frontmatter(self, path: Path) -> Optional[Dict]:
        try:
            content = path.read_text(encoding="utf-8")
            if not content.startswith("---"):
                return None

            end = content.find("---", 3)
            if end < 0:
                return None

            return yaml.safe_load(content[3:end]) or {}
        except:
            return None

    # =========================
    # CREATE ENTITY
    # =========================

    def create_entity_file(
        self,
        entity:    Dict,
        filename:  str,
        chunk_ids: List[str],
        user_role: str = "admin",     # [P4.5-MTS] write 주체 role
    ) -> str:
        """
        [P4.5-MTS] Memory Trust Scoring 연동.
        write 전 신뢰도 검증 → 미달 시 ValueError 발생.
        """
        # ── Memory Trust 검증 ──────────────────────────────
        try:
            from core.memory_trust import verify_before_write
            ok, reason, score = verify_before_write(
                entity    = entity,
                user_role = user_role,
                wiki_dir  = str(self.wiki_base_path),
            )
            if not ok:
                raise ValueError(f"[TRUST] write 거부: {reason}")
            print(f"[TRUST] ✅ {entity.get('name','?')} score={score:.3f}")
        except ImportError:
            pass   # memory_trust.py 없으면 건너뜀 (하위 호환)
        except ValueError:
            raise   # write 거부는 상위로 전파

        entity_type = entity.get("type", "concept")
        name = entity.get("name", "unknown")

        normalized = self._normalize_name(name)
        entity_id = self._generate_entity_id(name, entity_type)

        path = self.entity_path / entity_type / f"{normalized}.md"

        # aliases
        aliases = list({name})
        if entity.get("attributes", {}).get("약자"):
            aliases.append(entity["attributes"]["약자"])

        # =========================
        # RELATIONS + Ontology 정규화
        # =========================
        try:
            from core.ontology import (
                normalize_relation, validate_relation,
                infer_relations, get_relation_label
            )
            use_ontology = True
        except ImportError:
            use_ontology = False

        relations = []

        for rel in entity.get("relations", []):
            target_name = rel.get("대상") or rel.get("target")
            target_type = rel.get("유형") or rel.get("target_type") or rel.get("type") or "concept"
            raw_label   = rel.get("라벨") or rel.get("label") or "관련"
            confidence  = float(rel.get("신뢰도", rel.get("confidence", 0.8)))

            # Ontology: relation label 표준화
            if use_ontology:
                std_type = normalize_relation(raw_label)
                validate_relation(entity_type, std_type, strict=False)
                display_label = get_relation_label(std_type)
            else:
                std_type      = raw_label
                display_label = raw_label

            target_id = self._find_existing_entity_id(target_name, target_type)

            relations.append({
                "target":      target_name,
                "target_id":   target_id or "UNRESOLVED",
                "target_type": target_type,
                "type":        std_type,
                "label":       display_label,
                "confidence":  confidence,
            })

        # Ontology: IS_A 자동 추론 relation 추가
        if use_ontology:
            inferred = infer_relations(name, entity_type)
            for inf_rel in inferred:
                inf_target = inf_rel.get("target", "")
                inf_tid    = self._find_existing_entity_id(inf_target, "concept")
                relations.append({
                    "target":      inf_target,
                    "target_id":   inf_tid or "UNRESOLVED",
                    "target_type": "concept",
                    "type":        inf_rel.get("type", "IS_A"),
                    "label":       inf_rel.get("label", "분류"),
                    "confidence":  inf_rel.get("confidence", 1.0),
                    "inferred":    True,
                })

        attributes = entity.get("attributes", {})
        if not isinstance(attributes, dict):
            attributes = {}

        confidence = min(round(0.7 + 0.3 * len(attributes), 2), 1.0)

        frontmatter = {
            # ── 식별 정보 ──
            "entity_id":       entity_id,
            "entity_type":     entity_type,
            "name":            name,
            "normalized_name": normalized,
            "aliases":         aliases,
            # ── ABAC (진단 FAIL 수정: sensitivity/owner 저장 보장) ──
            "sensitivity":     self._default_sensitivity(entity_type),
            "owner":           "system",
            # ── 메타 ──
            "attributes":      attributes,
            "created_at":      datetime.now().isoformat(),
            "updated_at":      datetime.now().isoformat(),
            "version":         1,
            "sources":         [filename],
            "trusted":         True,
            # [P4.5-2] source_type: prod / test 구분
            "source_type":     self.source_type,
            "confidence":      confidence,
            "verified":        False,
            "embedding_refs":  chunk_ids,
            # ✅ 핵심 수정: relations를 frontmatter에 포함
            # (_read_frontmatter()가 읽을 수 있도록)
            "relations":       relations,
        }

        # 본문 관계 섹션은 사람이 읽기 쉬운 요약만
        rel_summary = "\n".join([
            f"- {r.get('label','관련')}: {r.get('target','')} "
            f"(conf={r.get('confidence',0):.2f})"
            for r in relations
        ]) or "- (관계 없음)"

        md = (
            "---\n"
            + yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
            + "---\n\n"
            f"## 요약\n"
            # [U-1] summary 우선, 없으면 description
            f"{entity.get('summary', '') or entity.get('description', '')}\n\n"
            f"## 관계\n{rel_summary}\n"
        )

        path.write_text(md, encoding="utf-8")

        self._register_entity_id(entity_id, path)

        return str(path)

    # =========================
    # SENSITIVITY DEFAULT (ABAC)
    # =========================

    @staticmethod
    def _default_sensitivity(entity_type: str) -> str:
        """entity_type별 기본 민감도 등급 반환"""
        mapping = {
            "person":   "confidential",  # 개인정보 → 기밀
            "org":      "internal",      # 조직정보 → 내부
            "document": "confidential",  # 문서 → 기밀
            "concept":  "public",        # 개념/지식 → 공개
        }
        return mapping.get(entity_type, "internal")

    # =========================
    # DUPLICATE CHECK
    # =========================

    def find_duplicate_entities(self, entity: Dict) -> Optional[str]:

        name = entity.get("name", "")
        normalized = self._normalize_name(name)

        t = entity.get("type", "concept")
        d = self.entity_path / t

        if not d.exists():
            return None

        for f in d.glob("*.md"):
            fm = self._read_frontmatter(f)
            if not fm:
                continue

            if fm.get("normalized_name") == normalized:
                return str(f)

        return None

    # =========================
    # INDEX
    # =========================

    def update_index(self):

        total = 0
        lines = ["# INDEX\n"]

        for t in self.entity_types:
            d = self.entity_path / t
            count = len(list(d.glob("*.md"))) if d.exists() else 0
            total += count

            lines.append(f"\n## {t} ({count})")

        self.index_path.write_text("\n".join(lines), encoding="utf-8")

    # =========================
    # RESOLVE (SAFE YAML 방식)
    # =========================

    def resolve_pending_relations(self):

        resolved = 0

        for t in self.entity_types:
            d = self.entity_path / t
            if not d.exists():
                continue

            for f in d.glob("*.md"):

                content = f.read_text(encoding="utf-8")

                if "UNRESOLVED" not in content:
                    continue

                end = content.find("---", 3)
                fm = yaml.safe_load(content[3:end])
                body = content[end+4:]

                try:
                    parts = body.split("## 관계")
                    if len(parts) < 2:
                        continue

                    rel_yaml = parts[1]
                    relations = yaml.safe_load(rel_yaml)

                    changed = False

                    for r in relations:
                        if r.get("target_id") == "UNRESOLVED":

                            found = self._find_existing_entity_id(
                                r["target"],
                                r["target_type"]
                            )

                            if not found:
                                found = self._find_existing_entity_id(r["target"], None)

                            if found:
                                r["target_id"] = found
                                changed = True

                    if changed:
                        new_body = "## 관계\n" + yaml.dump(relations, allow_unicode=True)

                        new_content = (
                            "---\n"
                            + yaml.dump(fm, allow_unicode=True)
                            + "---\n\n"
                            + parts[0]
                            + new_body
                        )

                        f.write_text(new_content, encoding="utf-8")
                        resolved += 1

                except Exception as e:
                    print("[RESOLVE ERROR]", e)

        print(f"[RESOLVE] {resolved} fixed")
        return resolved

    # =========================
    # STATS
    # =========================

    def get_entity_statistics(self):
        stats = {}
        total = 0

        for t in self.entity_types:
            d = self.entity_path / t
            c = len(list(d.glob("*.md"))) if d.exists() else 0
            stats[t] = c
            total += c

        stats["total"] = total
        return stats