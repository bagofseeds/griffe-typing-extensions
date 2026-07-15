"""Template smoke tests."""

import importlib


def test_template_submodule_is_importable() -> None:
    """The template package should be importable after installation."""
    module = importlib.import_module("griffe_typing_extensions")
    assert module is not None
