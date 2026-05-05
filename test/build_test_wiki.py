from core.wiki_generator import WikiGenerator

def main():
    wg = WikiGenerator()

    # 🔥 테스트용 구조 데이터 (Graph 검증용 최소 세트)
    entities = [

        # ─────────────
        # 사람
        # ─────────────
        {
            "name": "김철수",
            "type": "person",
            "attributes": {"직업": "학생"},
            "relations": [
                {"target": "경제학", "type": "공부", "confidence": 0.9},
                {"target": "서울대학교", "type": "소속", "confidence": 0.9},
            ]
        },
        {
            "name": "이영희",
            "type": "person",
            "attributes": {"직업": "교수"},
            "relations": [
                {"target": "서울대학교", "type": "소속", "confidence": 0.9}
            ]
        },

        # ─────────────
        # 기관
        # ─────────────
        {
            "name": "서울대학교",
            "type": "org",
            "attributes": {"유형": "대학"},
            "relations": []
        },

        # ─────────────
        # 개념
        # ─────────────
        {
            "name": "경제학",
            "type": "concept",
            "attributes": {"분야": "사회과학"},
            "relations": [
                {"target": "사회과학", "type": "분류", "confidence": 0.9}
            ]
        },
        {
            "name": "사회과학",
            "type": "concept",
            "attributes": {"유형": "학문"},
            "relations": []
        }
    ]

    print("🚀 테스트 Wiki 데이터 생성 시작")

    created_ids = []

    for e in entities:
        try:
            eid = wg.create_entity_file(e, "test_source", [])
            if eid:
                created_ids.append(eid)
                print(f"  ✅ 생성됨: {e['name']} → {eid}")
            else:
                print(f"  ⚠️ 생성 실패: {e['name']}")
        except Exception as ex:
            print(f"  💥 오류 발생 ({e['name']}): {ex}")

    print("\n📊 생성 결과 요약")
    print(f"  총 생성: {len(created_ids)}개")

    # 🔥 pending 관계 해결 (중요)
    print("\n🔗 관계 resolve 실행")
    wg.resolve_pending_relations()

    print("\n✅ 완료")

if __name__ == "__main__":
    main()