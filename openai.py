"""Lightweight stub for the openai package to enable tests without installing heavy deps.
Tests patch openai.OpenAI, so this stub only needs to provide the symbol and api_key attr.
"""
class OpenAI:
    def __init__(self, *args, **kwargs):
        # Real calls should be mocked in tests; raise if used unexpectedly
        raise RuntimeError("OpenAI stub invoked without patching in tests.")

# allow code to set openai.api_key = ...
api_key = None
