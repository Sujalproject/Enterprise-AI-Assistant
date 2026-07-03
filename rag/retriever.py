from typing import Annotated, Any, Dict, Optional

_THREAD_VECTORSTORE: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def _get_retriever(thread_id: Optional[str]):
    """Fetch the retriever for a thread if available."""

    if not thread_id:
        return None

    vectorstore = _THREAD_VECTORSTORE.get(thread_id)

    if vectorstore is None:
        return None

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )  
    

