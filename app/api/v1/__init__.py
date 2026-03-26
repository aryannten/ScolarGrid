"""
API v1 package — imports all routers for use in main.py
"""

from app.api.v1 import auth, notes, leaderboard, chat, complaints, admin, ai_chatbot, activity

__all__ = ["auth", "notes", "leaderboard", "chat", "complaints", "admin", "ai_chatbot", "activity"]
