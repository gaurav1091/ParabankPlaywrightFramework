class ScenarioContext:
    def __init__(self) -> None:
        self._data: dict[str, object] = {}

    def set(self, key: str, value: object) -> None:
        self._data[key] = value

    def get(self, key: str, default: object = None) -> object:
        return self._data.get(key, default)

    def contains(self, key: str) -> bool:
        return key in self._data

    def clear(self) -> None:
        self._data.clear()