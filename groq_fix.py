import litellm

_original_completion = litellm.completion


def _clean_completion(*args, **kwargs):
    msgs = kwargs.get("messages")
    if msgs:
        kwargs["messages"] = [
            {k: v for k, v in m.items() if k != "cache_breakpoint"}
            if isinstance(m, dict) else m
            for m in msgs
        ]
    return _original_completion(*args, **kwargs)


litellm.completion = _clean_completion