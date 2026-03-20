# New file: global registry to store non-serializable objects
# This keeps them out of GraphState so checkpointer doesn't try to serialize them

_registry = {}

def set_service(key: str, obj):
    _registry[key] = obj

def get_service(key: str):
    return _registry.get(key)