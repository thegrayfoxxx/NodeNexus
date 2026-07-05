from typing import Type, TypeVar
from nodenexus.core.models import ProtocolType
from nodenexus.core.exceptions import PluginNotFoundError

T = TypeVar("T")


class PluginRegistry:
    def __init__(self):
        self._protocols: dict[ProtocolType, Type] = {}
        self._interfaces: dict[str, Type] = {}

    def register_protocol(self, protocol_type: ProtocolType, cls: Type) -> None:
        self._protocols[protocol_type] = cls

    def get_protocol(self, protocol_type: ProtocolType) -> Type:
        if protocol_type not in self._protocols:
            raise PluginNotFoundError(f"Protocol {protocol_type} not registered")
        return self._protocols[protocol_type]

    def register_interface(self, name: str, cls: Type) -> None:
        self._interfaces[name] = cls

    def get_interface(self, name: str) -> Type:
        if name not in self._interfaces:
            raise PluginNotFoundError(f"Interface {name} not registered")
        return self._interfaces[name]
