"""Racine pytest — assure que `src` est importable depuis les tests."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def pytest_configure(config):
    """Enregistre les markers custom utilisés dans les ADTs."""
    config.addinivalue_line(
        "markers",
        "slow: test long (> 30s) — désactivable via -m 'not slow'",
    )
