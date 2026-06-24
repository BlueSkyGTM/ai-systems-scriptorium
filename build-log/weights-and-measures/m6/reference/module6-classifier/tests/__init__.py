"""Test package for the tuned text classifier (Module 6 artifact).

This package marker exists so pytest can collect the suite via
``tests/test_classifier.py`` and so callers can import shared fixtures
without namespace tricks. Keep it intentionally side-effect free: importing
this module must NOT train a model, touch the filesystem, or call MLflow.

Fixed seeds are applied at the top of each test module that exercises the
training or eval path, not here.
"""

__all__: list[str] = []
