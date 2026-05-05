"""
PROJECT JAMES - Ontology (Phase 4)

Phase 3.5: weight, sensitive, compute_graph_score 추가
Phase 4:   [P4-ONT-1] allowed_head/tail 타입 제약
           validate_relation_types(), is_valid_relation_triple()
"""

from typing import Dict, List, Optional, Set, Tuple

RELATION_TYPES: Dict[str, Dict] = {
    "STUDIES":     {"label":"공부",  "inverse":"STUDIED_BY",   "transitive":False, "weight":1.0, "sensitive":False, "allowed_head":{"person"},         "allowed_tail":{"concept"}},
    "RESEARCHES":  {"label":"연구",  "inverse":"RESEARCHED_BY","transitive":False, "weight":1.0, "sensitive":False, "allowed_head":{"person","org"},    "allowed_tail":{"concept"}},
    "TEACHES":     {"label":"가르침","inverse":"TAUGHT_BY",    "transitive":False, "weight":0.9, "sensitive":False, "allowed_head":{"person"},         "allowed_tail":{"concept","person"}},
    "BELONGS_TO":  {"label":"소속",  "inverse":"HAS_MEMBER",   "transitive":True,  "weight":1.2, "sensitive":False, "allowed_head":{"person","org"},    "allowed_tail":{"org"}},
    "WORKS_AT":    {"label":"근무",  "inverse":"EMPLOYS",      "transitive":False, "weight":1.1, "sensitive":False, "allowed_head":{"person"},         "allowed_tail":{"org"}},
    "FOUNDED_BY":  {"label":"설립됨","inverse":"FOUNDED",      "transitive":False, "weight":1.0, "sensitive":False, "allowed_head":{"org"},            "allowed_tail":{"person"}},
    "IS_A":        {"label":"분류",  "inverse":"HAS_SUBTYPE",  "transitive":True,  "weight":1.1, "sensitive":False, "allowed_head":{"concept"},        "allowed_tail":{"concept"}},
    "PART_OF":     {"label":"구성",  "inverse":"HAS_PART",     "transitive":True,  "weight":1.0, "sensitive":False, "allowed_head":None,               "allowed_tail":None},
    "RELATED_TO":  {"label":"관련",  "inverse":"RELATED_TO",   "transitive":False, "weight":0.7, "sensitive":False, "allowed_head":None,               "allowed_tail":None},
    "PRODUCES":    {"label":"생산",  "inverse":"PRODUCED_BY",  "transitive":False, "weight":1.0, "sensitive":False, "allowed_head":{"org"},            "allowed_tail":{"concept","document"}},
    "OPERATES_IN": {"label":"산업",  "inverse":"HAS_PLAYER",   "transitive":False, "weight":0.8, "sensitive":False, "allowed_head":{"org"},            "allowed_tail":{"concept"}},
    "BELONGS_TO_INDUSTRY": {"label":"분야","inverse":"INDUSTRY_OF","transitive":False,"weight":0.8,"sensitive":False,"allowed_head":{"org","concept"},  "allowed_tail":{"concept"}},
    # 고위험 sensitive
    "HAS_SECRET":     {"label":"비밀보유","inverse":"SECRET_OF",    "transitive":False,"weight":0.0,"sensitive":True, "allowed_head":None,"allowed_tail":None},
    "KNOWS_PASSWORD": {"label":"암호보유","inverse":"PASSWORD_OF",  "transitive":False,"weight":0.0,"sensitive":True, "allowed_head":None,"allowed_tail":None},
    "HAS_CREDENTIAL": {"label":"자격증명","inverse":"CREDENTIAL_OF","transitive":False,"weight":0.0,"sensitive":True, "allowed_head":None,"allowed_tail":None},
    "OWNS_PRIVATE":   {"label":"비공개소유","inverse":"PRIVATE_OF", "transitive":False,"weight":0.0,"sensitive":True, "allowed_head":None,"allowed_tail":None},
}

LABEL_TO_TYPE: Dict[str, str] = {
    "공부":"STUDIES","연구":"RESEARCHES","가르침":"TEACHES","소속":"BELONGS_TO",
    "근무":"WORKS_AT","분류":"IS_A","구성":"PART_OF","관련":"RELATED_TO",
    "생산":"PRODUCES","산업":"OPERATES_IN","분야":"BELONGS_TO_INDUSTRY","설립됨":"FOUNDED_BY",
    "비밀보유":"HAS_SECRET","암호보유":"KNOWS_PASSWORD","관계":"RELATED_TO","연결":"RELATED_TO",
}

ALLOWED_RELATIONS: Dict[str, Set[str]] = {
    "person":   {"STUDIES","RESEARCHES","TEACHES","BELONGS_TO","WORKS_AT","RELATED_TO","HAS_SECRET","HAS_CREDENTIAL"},
    "org":      {"BELONGS_TO","OPERATES_IN","PRODUCES","RELATED_TO","FOUNDED_BY"},
    "concept":  {"IS_A","PART_OF","RELATED_TO","BELONGS_TO_INDUSTRY"},
    "document": {"RELATED_TO","BELONGS_TO","OWNS_PRIVATE"},
}

CONCEPT_HIERARCHY: Dict[str, Optional[str]] = {
    "경제학":"사회과학","법학":"사회과학","심리학":"사회과학","사회학":"사회과학",
    "사회과학":"학문","물리학":"자연과학","화학":"자연과학","생물학":"자연과학",
    "자연과학":"학문","컴퓨터공학":"공학","전자공학":"공학","공학":"학문","학문":None,
    "인공지능":"IT","머신러닝":"인공지능","딥러닝":"머신러닝",
    "IT":"산업","전자":"산업","제조":"산업","금융":"산업","산업":None,
}

# ─── 기본 함수 ───────────────────────────────────────────────

def normalize_relation(label: str) -> str:
    if label in LABEL_TO_TYPE: return LABEL_TO_TYPE[label]
    if label in RELATION_TYPES: return label
    print(f"[ONTOLOGY] 미등록 relation '{label}' → RELATED_TO")
    return "RELATED_TO"

def get_relation_label(rel_type: str) -> str:
    return RELATION_TYPES.get(rel_type, {}).get("label", rel_type)

def get_relation_weight(rel_type: str) -> float:
    return float(RELATION_TYPES.get(normalize_relation(rel_type), {}).get("weight", 0.7))

def is_sensitive_relation(rel_type: str) -> bool:
    return bool(RELATION_TYPES.get(normalize_relation(rel_type), {}).get("sensitive", False))

def compute_graph_score(relations: List[Dict], depth: int = 1) -> float:
    """score = Σ(weight × confidence) / depth"""
    if not relations or depth < 1: return 0.0
    total = 0.0
    for rel in relations:
        if not isinstance(rel, dict): continue
        raw = rel.get("type") or rel.get("label") or "RELATED_TO"
        if is_sensitive_relation(raw): continue
        total += get_relation_weight(raw) * float(rel.get("confidence", 0.0))
    return round(total / max(depth, 1), 4)

# ─── [P4-ONT-1] 타입 제약 ────────────────────────────────────

def validate_relation_types(
    head_type: str,
    rel_type:  str,
    tail_type: str,
    strict:    bool = False,
) -> Tuple[bool, str]:
    """
    [P4-ONT-1] head/tail entity type이 relation 제약에 부합하는지 검증.

    Returns: (is_valid, reason)
    strict=True → 위반 시 차단 / False → 경고만
    """
    std  = normalize_relation(rel_type)
    info = RELATION_TYPES.get(std, {})
    ah   = info.get("allowed_head")
    at_  = info.get("allowed_tail")

    violations = []
    if ah is not None and head_type not in ah:
        violations.append(f"head '{head_type}' 불허 (허용:{ah})")
    if at_ is not None and tail_type not in at_:
        violations.append(f"tail '{tail_type}' 불허 (허용:{at_})")

    if violations:
        reason = f"[ONT-TYPE] {std}: {' | '.join(violations)}"
        if strict:
            print(f"{reason} → 차단"); return False, reason
        else:
            print(f"{reason} → 경고")
    return True, ""

def is_valid_relation_triple(head: dict, rel_type: str, tail: dict, strict: bool = False) -> bool:
    """entity dict 직접 받아 타입 제약 검증 (DFS 내 사용)"""
    ht = head.get("entity_type", head.get("type", "concept"))
    tt = tail.get("entity_type", tail.get("type", "concept"))
    valid, _ = validate_relation_types(ht, rel_type, tt, strict=strict)
    return valid

# ─── 기타 ────────────────────────────────────────────────────

def validate_relation(entity_type: str, rel_type: str, strict: bool = False) -> bool:
    allowed = ALLOWED_RELATIONS.get(entity_type, set())
    if rel_type not in allowed:
        msg = f"[ONTOLOGY] '{entity_type}' → '{rel_type}' 비표준"
        if strict: print(f"{msg} → 차단"); return False
        else: print(f"{msg} → 경고")
    return True

def get_ancestors(concept: str, max_depth: int = 3) -> List[str]:
    ancestors, current = [], concept
    for _ in range(max_depth):
        parent = CONCEPT_HIERARCHY.get(current)
        if parent is None: break
        ancestors.append(parent); current = parent
    return ancestors

def is_transitive(rel_type: str) -> bool:
    return RELATION_TYPES.get(rel_type, {}).get("transitive", False)

def infer_relations(entity_name: str, entity_type: str) -> List[Dict]:
    if entity_type == "concept" and entity_name in CONCEPT_HIERARCHY:
        parent = CONCEPT_HIERARCHY[entity_name]
        if parent:
            return [{"target":parent,"target_type":"concept","type":"IS_A",
                     "label":"분류","confidence":1.0,"inferred":True}]
    return []

def validate_entity_schema(entity: dict) -> List[str]:
    issues = []
    name = entity.get("name",""); entity_type = entity.get("entity_type",entity.get("type",""))
    if not name: issues.append("name 없음")
    if entity_type not in ALLOWED_RELATIONS: issues.append(f"미등록 entity_type: {entity_type}")
    if not entity.get("entity_id"): issues.append("entity_id 없음")
    for rel in entity.get("relations",[]):
        if not isinstance(rel, dict): continue
        conf = float(rel.get("confidence",0))
        if conf <= 0 or conf > 1: issues.append(f"confidence 범위 오류: {conf}")
    return issues


if __name__ == "__main__":
    print("=== Ontology Phase 4 자가 테스트 ===\n")
    for rtype in ["BELONGS_TO","STUDIES","RELATED_TO","HAS_SECRET"]:
        print(f"  {rtype:20s} weight={get_relation_weight(rtype):.1f}  sensitive={is_sensitive_relation(rtype)}")
    print()
    cases = [
        ("person","STUDIES","concept",True),
        ("org","STUDIES","concept",False),
        ("person","BELONGS_TO","org",True),
        ("concept","IS_A","concept",True),
        ("person","IS_A","concept",False),
    ]
    for head,rel,tail,exp in cases:
        ok,_ = validate_relation_types(head,rel,tail,strict=False)
        icon = "✅" if ok==exp else "❌"
        print(f"  {icon} {head:8s} -[{rel:12s}]→ {tail:8s} valid={ok} (기대={exp})")
    print("\n✅ 완료")
