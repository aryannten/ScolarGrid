"""
Google Gemini AI service for ScholarGrid Backend API

Provides AI chatbot functionality with academic context awareness.
"""

import logging
from typing import Optional, List, Dict, AsyncIterator
from app.core.config import settings

logger = logging.getLogger(__name__)

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
    """
    Initialize and return the Gemini generative model.
    
    Returns:
        GenerativeModel: Configured Gemini model instance
        
    Raises:
        ValueError: If GEMINI_API_KEY is not configured
        Exception: If model initialization fails
    """
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. Please set it in your environment variables."
        )
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )
    except ImportError as e:
        logger.error(f"Failed to import google.generativeai: {e}")
        raise Exception(
            "Google Generative AI library not installed. "
            "Please install it with: pip install google-generativeai"
        )
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        raise Exception(f"Failed to initialize Gemini client: {str(e)}")


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
        ValueError: If message is empty or invalid
        Exception: If Gemini API call fails
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    
    if len(message) > 10000:
        raise ValueError("Message is too long (max 10000 characters)")
    
    try:
        model = get_gemini_client()
        chat = model.start_chat(history=history or [])
        full_message = f"{context}\n\n{message}" if context else message
        
        logger.info(f"Sending message to Gemini API (length: {len(full_message)})")
        response = await _run_sync(chat.send_message, full_message)
        
        if not response or not response.text:
            logger.error("Gemini API returned empty response")
            raise Exception("AI service returned an empty response")
        
        logger.info(f"Received response from Gemini API (length: {len(response.text)})")
        return response.text
        
    except ValueError as e:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}", exc_info=True)
        # Provide user-friendly error message
        if "quota" in str(e).lower():
            raise Exception(
                "AI service quota exceeded. Please try again later."
            )
        elif "api key" in str(e).lower():
            raise Exception(
                "AI service authentication failed. Please contact support."
            )
        elif "timeout" in str(e).lower():
            raise Exception(
                "AI service request timed out. Please try again."
            )
        else:
            raise Exception(
                f"AI service is temporarily unavailable. Please try again later."
            )


async def send_message_stream(
    message: str,
    history: List[Dict] = None,
    context: str = "",
) -> AsyncIterator[str]:
    """
    Stream Gemini response chunks.
    
    Args:
        message: User's message
        history: List of previous messages in format [{"role": ..., "parts": [...]}]
        context: Additional context string to prepend to the message
        
    Yields:
        str: Response text chunks as they arrive
        
    Raises:
        ValueError: If message is empty or invalid
        Exception: If Gemini API streaming fails
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    
    if len(message) > 10000:
        raise ValueError("Message is too long (max 10000 characters)")
    
    try:
        model = get_gemini_client()
        chat = model.start_chat(history=history or [])
        full_message = f"{context}\n\n{message}" if context else message

        logger.info(f"Starting streaming response from Gemini API (length: {len(full_message)})")
        
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: chat.send_message(full_message, stream=True)
        )
        
        chunk_count = 0
        for chunk in response:
            if chunk.text:
                chunk_count += 1
                yield chunk.text
        
        logger.info(f"Streaming completed with {chunk_count} chunks")
        
    except ValueError as e:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Gemini streaming error: {str(e)}", exc_info=True)
        # Provide user-friendly error message
        if "quota" in str(e).lower():
            raise Exception(
                "AI service quota exceeded. Please try again later."
            )
        elif "api key" in str(e).lower():
            raise Exception(
                "AI service authentication failed. Please contact support."
            )
        elif "timeout" in str(e).lower():
            raise Exception(
                "AI service request timed out. Please try again."
            )
        else:
            raise Exception(
                f"AI service streaming is temporarily unavailable. Please try again later."
            )


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
