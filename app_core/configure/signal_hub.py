from typing import Callable, List, Optional, Union

from app_core.task.taskcfg import SignMsg


class _HeadlessSignal:
    def __init__(self) -> None:
        self._subscribers: List[Callable[[str, object], None]] = []

    def connect(self, callback: Callable[[str, object], None]) -> None:
        self._subscribers.append(callback)

    def emit(self, uuid: Union[str, None], data: SignMsg = None) -> None:
        for callback in list(self._subscribers):
            callback(uuid or "", data)


class SignalHub:
    _instance: Optional["SignalHub"] = None

    def __init__(self, parent=None) -> None:
        self.new_message = _HeadlessSignal()

    @classmethod
    def instance(cls) -> "SignalHub":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def post(self, uuid: Union[str, None] = None, data: SignMsg = None) -> None:
        self.new_message.emit(uuid, data)
