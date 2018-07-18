from typing import Optional, List

from lruttl import LRUCache

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem


DEFAULT_SIZE = 5000
DEFAULT_TTL = None


class CachedFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, store: AbstractFeatureFlagStore, **cache_options):
        self._cache = LRUCache(cache_options.get('size', DEFAULT_SIZE))
        self._store = store
        self._cache_options = {
            'ttl': None,
            **cache_options,
        }

    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        item = self._store.create(
            feature_name, is_enabled=is_enabled, client_data=client_data
        )
        self._cache.set(feature_name, item, **self._cache_options)
        return item

    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        if feature_name in self._cache:
            return self._cache[feature_name]

        item = self._store.get(feature_name)
        self._cache.set(feature_name, item, **self._cache_options)

        return item

    def set(
        self,
        feature_name: str,
        is_enabled: bool,
    ):
        self._store.set(feature_name, is_enabled)
        self._cache.set(
            feature_name,
            self._store.get(feature_name),
            **self._cache_options,
        )

    def delete(self, feature_name: str):
        self._store.delete(feature_name)
        self._cache.set(feature_name, None, -1)

    def set_client_data(
        self,
        feature_name: str,
        client_data: dict,
    ):
        self._store.set_client_data(feature_name, client_data)
        self._cache.set(
            feature_name,
            self._store.get(feature_name),
            self._cache_options,
        )
