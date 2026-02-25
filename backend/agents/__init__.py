from importlib import import_module
def load_agent(name: str):
    try:
        mod = import_module(f"backend.agents.{name}")
        fn = getattr(mod, "run", None) or getattr(mod, "main", None)
    except Exception:
        fn = None
    if fn is None:
        def _stub(payload): return {"agent": name, "status": "ok", "echo": payload}
        return _stub
    return fn
