import json
import os
from typing import Any, Dict

import numpy as np


class ParsedCacheManager:
    def __init__(self, cache_path="data/parsed_data_cache.json"):
        self.cache_path = cache_path
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Повреждённый кэш — создаём новый.")
                return {}
        return {}

    def is_already_parsed(self, timestamp: str) -> bool:
        return timestamp in self.cache

    def add_parsed_entry(self, timestamp: str, parsed_data: Dict[str, Any]):
        self.cache[timestamp] = parsed_data

    def convert(self, obj):
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, dict):
            return {k: self.convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.convert(v) for v in obj]
        return obj

    def save(self):
        with open(self.cache_path, "w", encoding="utf-8") as f:
            clean_cache = {k: self.convert(v) for k, v in self.cache.items()}
            json.dump(clean_cache, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list:
        return list(self.cache.values())
