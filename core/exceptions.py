class NodeNexusError(Exception):
    pass


class ServerConnectionError(NodeNexusError):
    pass


class CommandError(NodeNexusError):
    pass


class PluginNotFoundError(NodeNexusError):
    pass
