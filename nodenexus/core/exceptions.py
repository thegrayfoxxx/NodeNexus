class NodeNexusError(Exception):
    """Base exception for NodeNexus."""
    pass

class ConnectionError(NodeNexusError):
    """Connection to server failed."""
    pass

class CommandError(NodeNexusError):
    """Command execution failed."""
    pass

class PluginNotFoundError(NodeNexusError):
    """Requested plugin not found in registry."""
    pass