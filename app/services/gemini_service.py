"""
Google Gemini AI service for ScholarGrid Backend API

Provides AI chatbot functionality with academic context awareness.
"""

from typing import Optional, List, Dict, AsyncIterator
from app.core.config import settings

SYSTEM_PROMPT = """You are ScholarGrid Assistant, an AI helper for the ScholarGrid academic note-sharing platform.

Your role is to:
- Help students with academic questions and provide educational explanations
- Guide students in finding and using notes on the platform
- Answer questions about platform features and how to use them
- Encourage critical thinking rather than giving direct homework answers
- Be helpful, clear, and student-friendly

Platform context:
- Students can upload and download educational notes (PDF, PPT, DOC)
- Notes are rated 1-5 stars and organized by subject
- Students earn scores: 1 point per upload + 1 point per download
- Tiers: Bronze (0-999), Silver (1000-1999), Gold (2000-2999), Elite (3000+)
- Real-time chat groups are available for study collaboration
- All notes go through admin moderation before being visible

Limitations:
- Stay focused on academic and platform-related topics
- Do not answer questions unrelated to studying, education, or the platform
- Do not provide direct answers to homework assignments — guide critical thinking instead
"""


def get_gemini_client():
    """Initialize and return the Gemini generative model."""
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )


async def send_message(
    message: str,
    history: List[Dict] = None,
    context: str = "",
) -> str:
    """
    Send a message to Gemini and get a response.

    Args:
        message: User's message
        history: List of previous messages in format [{"role": ..., "parts": [...]}]
        context: Additional context string to prepend to the message

    Returns:
        str: AI response text

    Raises:
        Exception: If Gemini API call fails
    """
    try:
        model = get_gemini_client()
        chat = model.start_chat(history=history or [])
        full_message = f"{context}\n\n{message}" if context else message
        response = await _run_sync(chat.send_message, full_message)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


async def send_message_stream(
    message: str,
    history: List[Dict] = None,
    context: str = "",
) -> AsyncIterator[str]:
    """Stream Gemini response chunks."""
    try:
        model = get_gemini_client()
        chat = model.start_chat(history=history or [])
        full_message = f"{context}\n\n{message}" if context else message

        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: chat.send_message(full_message, stream=True)
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        raise Exception(f"Gemini streaming error: {str(e)}")


async def _run_sync(func, *args):
    """Run a synchronous function in a thread pool executor."""
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


def build_conversation_history(messages) -> List[Dict]:
    """Convert AIMessage ORM objects to Gemini chat history format."""
    history = []
    for msg in messages:
        history.append({
            "role": "user" if msg.role == "user" else "model",
            "parts": [msg.content],
        })
    return history
