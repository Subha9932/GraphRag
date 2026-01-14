import operator
from typing import List, Any

# While LangGraph's built-in `operator.add` usually suffices for lists,
# we can define custom reducers here if we need more complex logic (e.g., deduplication).

def deduce_append(current: List[Any], new: List[Any]) -> List[Any]:
    """
    Custom reducer to append new items to a list while removing duplicates.
    Currently just using simple addition for performance, but ready for logic.
    """
    return current + new

def replace_strategy(current: Any, new: Any) -> Any:
    """
    Always replace the old value with the new one.
    """
    return new
