from pydantic import SerializerFunctionWrapHandler

def SecureString(value: str, handler: SerializerFunctionWrapHandler) -> str:
    """When serialising models, secure strings' presence is marked rather than
    exposing the actual content"""
    return 'PRESENT' if value else 'ABSENT'
