from src_v3.memory.schema import GraphState

# Global state cache for persistence between runs
_state_cache = {}

def save_state(state_id: str, state: GraphState):
    """Save a state to the cache"""
    _state_cache[state_id] = state.copy()

def load_state(state_id: str) -> GraphState:
    """Load a state from the cache"""
    if state_id in _state_cache:
        return _state_cache[state_id].copy()
    return GraphState()

def clear_state(state_id: str):
    """Clear a state from the cache"""
    if state_id in _state_cache:
        del _state_cache[state_id]