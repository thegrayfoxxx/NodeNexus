from typing import Type

from core.exceptions import PluginNotFoundError
from core.models import ProtocolType


class PluginRegistry:
    def __init__(self):
        self._protocols: dict[ProtocolType, Type] = {}
        self._interfaces: dict[str, Type] = {}

    def register_protocol(self, protocol_type: ProtocolType, cls: Type) -> None:
        self._protocols[protocol_type] = cls

    def get_protocol(self, protocol_type: ProtocolType) -> Type:
        if protocol_type not in self._protocols:
            raise PluginNotFoundError(f"Протокол {protocol_type} не зарегистрирован")
        return self._protocols[protocol_type]

    def register_interface(self, name: str, cls: Type) -> None:
        self._interfaces[name] = cls

    def get_interface(self, name: str) -> Type:
        if name not in self._interfaces:
            raise PluginNotFoundError(f"Интерфейс {name} не зарегистрирован")
        return self._interfaces[name]
