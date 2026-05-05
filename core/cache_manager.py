"""
PROJECT JAMES - Cache Manager (Phase 4)

수정:
  [CACHE-BUG-FIX] 에러 응답 캐시 금지
    기존: set() 시 검증 없음 → [Gemma 응답 없음] 등 에러도 저장
    수정: is_cacheable() 검증 → 에러 응답 저장 거부
         get() 시에도 재검증 → 기존에 저장된 에러 자동 제거

  [CACHE-STAT] hit/miss/error 통계 카운터
"""

import hashlib
import time
from collections import OrderedDict

# 에러 응답 식별자
_ERROR_PREFIXES = (
    "[Gemma 응답 없음]",
    "[Gemma 오류]",
    "[Gemma Vision 오류]",
    "[Gemma Vision 응답 없음]",
)

def is_cacheable(value) -> bool:
    """[CACHE-BUG-FIX] 캐시 저장 가능 여부"""
    if not value or not isinstance(value, str):
        return False
    if value.startswith(_ERROR_PREFIXES):
        return False
    if len(value.strip()) < 5:
        return False
    return True


class CacheManager:
    def __init__(self, max_size: int = 100, ttl: int = 600):
        self.cache      = OrderedDict()
        self.timestamps = {}
        self.max_size   = max_size
        self.ttl        = ttl
        # [CACHE-STAT]
        self._hits   = 0
        self._misses = 0
        self._errors = 0   # 에러 응답으로 저장 거부된 횟수

    def get(self, key):
        """
        [CACHE-BUG-FIX] 조회 시점에도 에러 응답 재검증.
        이전에 저장된 에러 응답 자동 제거 → 재호출 유도.
        """
        if key in self.cache:
            age = time.time() - self.timestamps.get(key, 0)
            if age < self.ttl:
                value = self.cache[key]
                # 기존에 잘못 저장된 에러 응답 제거
                if not is_cacheable(value):
                    print(f"[CACHE] 🧹 오래된 에러 응답 제거: '{value[:40]}'")
                    self.cache.pop(key, None)
                    self.timestamps.pop(key, None)
                    self._errors += 1
                    self._misses += 1
                    return None
                self.cache.move_to_end(key)
                self._hits += 1
                return value
            else:
                self.cache.pop(key, None)
                self.timestamps.pop(key, None)

        self._misses += 1
        return None

    def set(self, key, value):
        """[CACHE-BUG-FIX] 에러 응답 저장 거부"""
        if not is_cacheable(value):
            self._errors += 1
            print(f"[CACHE] 에러 응답 저장 거부: '{str(value)[:40]}'")
            return

        while len(self.cache) >= self.max_size:
            oldest_key, _ = self.cache.popitem(last=False)
            self.timestamps.pop(oldest_key, None)

        self.cache[key] = value
        self.cache.move_to_end(key)
        self.timestamps[key] = time.time()

    def generate_key(self, content) -> str:
        return hashlib.sha256(str(content).strip().lower().encode()).hexdigest()

    def get_stats(self) -> dict:
        """[CACHE-STAT] 히트율 통계"""
        total    = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            "hits":       self._hits,
            "misses":     self._misses,
            "errors":     self._errors,
            "total":      total,
            "hit_rate":   round(hit_rate, 3),
            "hit_rate_%": f"{hit_rate * 100:.1f}%",
            "cache_size": len(self.cache),
            "ttl":        self.ttl,
        }

    def reset_stats(self):
        self._hits = self._misses = self._errors = 0

    def clear_expired(self):
        current_time = time.time()
        expired = [k for k, t in self.timestamps.items()
                   if current_time - t >= self.ttl]
        for key in expired:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
        if expired:
            print(f"[CACHE] 만료 {len(expired)}개 제거")
