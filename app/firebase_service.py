"""
Backward-compatible module alias for Firebase service.

This keeps the historical ``app.firebase_service`` import path pointing at
the actual implementation module in ``app.services.firebase_service``.
"""

import sys

from app.services import firebase_service as _firebase_service_module

sys.modules[__name__] = _firebase_service_module
