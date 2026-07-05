from dishka import make_container, Provider, Scope, provide
from nodenexus.core.registry import PluginRegistry
from nodenexus.core.models import ProtocolType
from nodenexus.plugins.protocols.ssh import SSHProtocol

class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def get_registry(self) -> PluginRegistry:
        registry = PluginRegistry()
        registry.register_protocol(ProtocolType.SSH, SSHProtocol)
        return registry

def create_container():
    return make_container(AppProvider())
