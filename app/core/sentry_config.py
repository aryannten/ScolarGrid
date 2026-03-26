"""
Sentry error tracking integration for ScholarGrid Backend API.

Provides error tracking and performance monitoring in production.
"""

import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def initialize_sentry() -> Optional[object]:
    """
    Initialize Sentry error tracking if DSN is configured.
    
    Returns:
        Sentry SDK instance if initialized, None otherwise
    """
    if not settings.sentry_dsn:
        logger.info("Sentry DSN not configured - error tracking disabled")
        return None
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            release=f"{settings.app_name}@{settings.app_version}",
            traces_sample_rate=0.1 if settings.is_production else 1.0,
            profiles_sample_rate=0.1 if settings.is_production else 1.0,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
            # Filter out health check requests from traces
            before_send_transaction=lambda event, hint: (
                None if event.get("transaction", "").endswith("/health") else event
            ),
            # Add custom tags
            default_integrations=True,
            send_default_pii=False,  # Don't send PII by default
        )
        
        logger.info(f"Sentry initialized for environment: {settings.environment}")
        return sentry_sdk
    
    except ImportError:
        logger.warning(
            "Sentry SDK not installed. Install with: pip install sentry-sdk[fastapi]"
        )
        return None
    
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return None


def capture_exception(exception: Exception, context: Optional[dict] = None):
    """
    Capture an exception and send to Sentry.
    
    Args:
        exception: The exception to capture
        context: Additional context to include with the error
    """
    if not settings.sentry_dsn:
        return
    
    try:
        import sentry_sdk
        
        if context:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_context(key, value)
                sentry_sdk.capture_exception(exception)
        else:
            sentry_sdk.capture_exception(exception)
    
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {e}")


def capture_message(message: str, level: str = "info", context: Optional[dict] = None):
    """
    Capture a message and send to Sentry.
    
    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context to include with the message
    """
    if not settings.sentry_dsn:
        return
    
    try:
        import sentry_sdk
        
        if context:
            with sentry_sdk.push_scope() as scope:
                for key, value in context.items():
                    scope.set_context(key, value)
                sentry_sdk.capture_message(message, level=level)
        else:
            sentry_sdk.capture_message(message, level=level)
    
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Failed to capture message in Sentry: {e}")


def set_user_context(user_id: str, email: Optional[str] = None):
    """
    Set user context for Sentry error tracking.
    
    Args:
        user_id: User ID
        email: User email (optional)
    """
    if not settings.sentry_dsn:
        return
    
    try:
        import sentry_sdk
        
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
        })
    
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Failed to set user context in Sentry: {e}")
