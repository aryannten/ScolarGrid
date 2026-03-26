"""
Socket.io real-time chat server for ScholarGrid Backend API

Handles WebSocket connections, room management, and message broadcasting.
Firebase token authentication is required on connection.
"""

import socketio
from datetime import datetime, timezone

# Create async Socket.io server with Redis adapter support
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",  # Restricted by FastAPI CORS middleware
    logger=False,
    engineio_logger=False,
)

# ASGI app to be mounted in main.py
socket_app = socketio.ASGIApp(sio, socketio_path="/socket.io")


async def _verify_token_from_sid(sid: str, environ: dict):
    """
    Verify Firebase token from Socket.io connection query params or auth.

    Returns decoded token dict or None if verification fails.
    """
    token = None

    # Try query string first: ?token=...
    query_string = environ.get("QUERY_STRING", "")
    for part in query_string.split("&"):
        if part.startswith("token="):
            token = part[6:]
            break

    # Try HTTP_AUTHORIZATION header
    if not token:
        auth_header = environ.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        return None

    try:
        from app.services.firebase_service import verify_firebase_token
        decoded = await verify_firebase_token(token)
        return decoded
    except Exception:
        return None


# ─── Connection Events ────────────────────────────────────────────────────────

@sio.event
async def connect(sid, environ, auth):
    """Authenticate user on WebSocket connection."""
    decoded = await _verify_token_from_sid(sid, environ)
    if not decoded:
        # Also try auth dict from Socket.io client
        if auth and isinstance(auth, dict):
            token = auth.get("token")
            if token:
                try:
                    from app.services.firebase_service import verify_firebase_token
                    decoded = await verify_firebase_token(token)
                except Exception:
                    pass

    if not decoded:
        await sio.disconnect(sid)
        return False

    # Store user identity in session
    await sio.save_session(sid, {
        "firebase_uid": decoded.get("uid"),
        "email": decoded.get("email"),
        "name": decoded.get("name"),
    })

    print(f"Socket connected: sid={sid}, uid={decoded.get('uid')}")


@sio.event
async def disconnect(sid):
    """Clean up on disconnect."""
    session = await sio.get_session(sid)
    print(f"Socket disconnected: sid={sid}, uid={session.get('firebase_uid')}")


# ─── Room Events ──────────────────────────────────────────────────────────────

@sio.event
async def join_group(sid, data):
    """
    Client joins a chat group room.
    data: {"group_id": "uuid"}
    """
    session = await sio.get_session(sid)
    group_id = data.get("group_id")
    if not group_id:
        return

    # Validate membership via DB
    try:
        from app.core.database import SessionLocal
        from app.models.user import User
        from app.models.chat import ChatGroup, ChatMembership

        db = SessionLocal()
        user = db.query(User).filter(User.firebase_uid == session["firebase_uid"]).first()
        if not user:
            db.close()
            return

        membership = db.query(ChatMembership).filter(
            ChatMembership.group_id == group_id,
            ChatMembership.user_id == user.id,
        ).first()
        db.close()

        if not membership:
            await sio.emit("error", {"message": "Not a member of this group."}, to=sid)
            return
    except Exception:
        return

    room = f"group:{group_id}"
    sio.enter_room(sid, room)
    await sio.emit("user_joined", {"user_id": str(user.id), "name": user.name, "group_id": group_id}, room=room, skip_sid=sid)


@sio.event
async def leave_group(sid, data):
    """Client leaves a chat group room. data: {"group_id": "uuid"}"""
    group_id = data.get("group_id")
    if group_id:
        room = f"group:{group_id}"
        sio.leave_room(sid, room)
        await sio.emit("user_left", {"group_id": group_id}, room=room, skip_sid=sid)


# ─── Message Events ───────────────────────────────────────────────────────────

@sio.event
async def send_message(sid, data):
    """
    Client sends a message to a group.
    data: {"group_id": "uuid", "content": "...", "type": "text|file", "file_url": "..."}
    """
    session = await sio.get_session(sid)
    group_id = data.get("group_id")
    content = data.get("content", "").strip()
    msg_type = data.get("type", "text")

    if not group_id or not content:
        return

    try:
        from app.core.database import SessionLocal
        from app.models.user import User
        from app.models.chat import ChatGroup, ChatMembership, Message

        db = SessionLocal()
        user = db.query(User).filter(User.firebase_uid == session["firebase_uid"]).first()
        if not user:
            db.close()
            return

        # Verify membership
        membership = db.query(ChatMembership).filter(
            ChatMembership.group_id == group_id,
            ChatMembership.user_id == user.id,
        ).first()
        if not membership:
            db.close()
            return

        # Persist message
        msg = Message(
            group_id=group_id,
            sender_id=user.id,
            content=content,
            type=msg_type,
            file_url=data.get("file_url"),
        )
        db.add(msg)

        # Update group's last message
        group = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
        if group:
            group.last_message = content[:200]
            group.last_message_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(msg)

        payload = {
            "id": str(msg.id),
            "group_id": group_id,
            "sender_id": str(user.id),
            "sender_name": user.name,
            "sender_avatar": user.avatar_url,
            "content": content,
            "type": msg_type,
            "file_url": msg.file_url,
            "created_at": msg.created_at.isoformat(),
        }
        db.close()

        room = f"group:{group_id}"
        await sio.emit("message_received", payload, room=room)

    except Exception as e:
        await sio.emit("error", {"message": f"Message delivery failed: {str(e)}"}, to=sid)


@sio.event
async def typing(sid, data):
    """Broadcast typing indicator. data: {"group_id": "uuid"}"""
    session = await sio.get_session(sid)
    group_id = data.get("group_id")
    if group_id:
        room = f"group:{group_id}"
        await sio.emit(
            "typing_indicator",
            {"group_id": group_id, "name": session.get("name", "Someone")},
            room=room,
            skip_sid=sid,
        )
