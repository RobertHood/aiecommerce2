import importlib


rag_chain = None
rag_module = None


def get_chain():
    global rag_chain, rag_module
    if rag_chain is None:
        try:
            rag_module = importlib.import_module("rag_chat")
            rag_chain = rag_module.setup_rag()
        except ImportError:
            return None, None
    return rag_chain, rag_module
