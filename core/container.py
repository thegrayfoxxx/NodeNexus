from dishka import Provider, Scope, make_container, provide

from core.models import ProtocolType
from core.registry import PluginRegistry
from plugins.protocols.ssh import SSHProtocol


class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def get_registry(self) -> PluginRegistry:
        registry = PluginRegistry()
        registry.register_protocol(ProtocolType.SSH, SSHProtocol)
        return registry


def create_container():
    return make_container(AppProvider())
