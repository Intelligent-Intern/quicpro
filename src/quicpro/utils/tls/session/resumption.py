"""
Session Resumption Manager

This module provides functionality for storing and resuming TLS sessions,
as well as rotating session ticket keys. The storage mechanism used here is in-memory;
in production, a persistent and secure storage should be used.
"""

import os
import pickle
import threading
from typing import Optional, Any

_SESSION_STORE: dict[str, bytes] = {}
_lock = threading.Lock()

def store_session(session: Any, session_id: Optional[str] = None) -> str:
    """
    Store a TLS session and return a session ID.
    
    :param session: The TLS session object to store.
    :param session_id: Optional session ID; if not provided, it is generated.
    :return: A session ID string.
    """
    with _lock:
        if session_id is None:
            session_id = os.urandom(16).hex()
        _SESSION_STORE[session_id] = pickle.dumps(session)
    return session_id

def resume_session(session_id: str) -> Optional[Any]:
    """
    Resume a stored TLS session given its session ID.
    
    :param session_id: The ID of the session to resume.
    :return: The TLS session object if found; otherwise, None.
    """
    with _lock:
        session_data = _SESSION_STORE.get(session_id)
        if session_data is None:
            return None
        return pickle.loads(session_data)

def rotate_ticket_key() -> bytes:
    """
    Rotate the session ticket key.
    
    :return: A new session ticket key (48 bytes).
    """
    return os.urandom(48)