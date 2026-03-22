"""
Pydantic schemas for ScholarGrid Backend API

All request/response schemas for users, notes, chat, complaints, leaderboard,
activity feed, AI chatbot, and admin endpoints.
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator


# ─── User Schemas ──────────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    about: Optional[str] = None


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    about: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    avatar_url: Optional[str] = None
    about: Optional[str] = None
    status: str
    score: int
    tier: str
    uploads_count: int
    downloads_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    id: UUID
    name: str
    role: str
    avatar_url: Optional[str] = None
    tier: str
    score: int
    uploads_count: int
    downloads_count: int

    model_config = {"from_attributes": True}


# ─── Note Schemas ──────────────────────────────────────────────────────────────

class NoteResponse(BaseModel):
    id: UUID
    title: str
    description: str
    subject: str
    tags: Optional[List[str]] = None
    file_url: str
    file_name: str
    file_size: int
    file_type: Optional[str] = None
    uploader_id: Optional[UUID] = None
    uploader_name: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    download_count: int
    average_rating: Optional[float] = None
    rating_count: int
    upload_date: datetime

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    items: List[NoteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class NoteRejectRequest(BaseModel):
    reason: str = Field(..., min_length=1)


class NoteDownloadResponse(BaseModel):
    download_url: str
    note_id: UUID
    title: str


class RatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)


class RatingResponse(BaseModel):
    note_id: UUID
    user_id: UUID
    rating: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Leaderboard Schemas ───────────────────────────────────────────────────────

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    name: str
    avatar_url: Optional[str] = None
    score: int
    tier: str
    uploads_count: int
    downloads_count: int


class LeaderboardResponse(BaseModel):
    rankings: List[LeaderboardEntry]
    total: int
    page: int
    page_size: int


# ─── Chat Schemas ──────────────────────────────────────────────────────────────

class ChatGroupCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class JoinGroupRequest(BaseModel):
    join_code: str = Field(..., min_length=8, max_length=8)


class ChatGroupResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    join_code: str
    creator_id: UUID
    member_count: int
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatGroupListResponse(BaseModel):
    groups: List[ChatGroupResponse]


class MessageResponse(BaseModel):
    id: UUID
    sender_id: Optional[UUID] = None
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    content: str
    type: str
    file_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    page: int
    page_size: int


# ─── Complaint Schemas ─────────────────────────────────────────────────────────

VALID_CATEGORIES = {"technical", "content", "account", "feature_request", "other"}
VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}


class ComplaintResponse(BaseModel):
    id: UUID
    title: str
    description: str
    category: str
    status: str
    priority: str
    screenshot_url: Optional[str] = None
    submitter_id: Optional[UUID] = None
    submitter_name: Optional[str] = None
    resolution_note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplaintUpdateRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    resolution_note: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        if v is not None and v not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {VALID_PRIORITIES}")
        return v


class ComplaintResponseCreate(BaseModel):
    text: str = Field(..., min_length=1)


class ComplaintResponseItem(BaseModel):
    id: UUID
    text: str
    admin_id: Optional[UUID] = None
    admin_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ComplaintDetailResponse(BaseModel):
    id: UUID
    title: str
    description: str
    category: str
    status: str
    priority: str
    screenshot_url: Optional[str] = None
    submitter_id: Optional[UUID] = None
    submitter_name: Optional[str] = None
    resolution_note: Optional[str] = None
    created_at: datetime
    responses: List[ComplaintResponseItem] = []

    model_config = {"from_attributes": True}


class ComplaintListResponse(BaseModel):
    items: List[ComplaintResponse]
    total: int
    page: int
    page_size: int


# ─── Activity Schemas ──────────────────────────────────────────────────────────

class ActivityResponse(BaseModel):
    id: UUID
    type: str
    user_id: Optional[UUID] = None
    user_name: Optional[str] = None
    entity_id: Optional[UUID] = None
    entity_title: Optional[str] = None
    metadata: Optional[Any] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityListResponse(BaseModel):
    activities: List[ActivityResponse]
    total: int
    page: int
    page_size: int


# ─── Analytics Schemas ─────────────────────────────────────────────────────────

class AnalyticsTotals(BaseModel):
    users: int
    students: int
    admins: int
    notes: int
    approved_notes: int
    pending_notes: int
    total_downloads: int
    chat_groups: int
    complaints: int


class MonthlyCount(BaseModel):
    month: str
    count: int


class SubjectCount(BaseModel):
    subject: str
    count: int


class ComplaintStats(BaseModel):
    open: int
    in_progress: int
    resolved: int
    closed: int


class AnalyticsResponse(BaseModel):
    totals: AnalyticsTotals
    trends: dict
    top_subjects: List[SubjectCount]
    complaint_stats: ComplaintStats


# ─── AI Chatbot Schemas ────────────────────────────────────────────────────────

class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None


class AIChatResponse(BaseModel):
    conversation_id: UUID
    message: str
    response: str
    timestamp: datetime
    remaining_messages: int


class AIConversationSummary(BaseModel):
    id: UUID
    title: Optional[str] = None
    message_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIMessageItem(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AIConversationDetail(BaseModel):
    id: UUID
    user_id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[AIMessageItem]

    model_config = {"from_attributes": True}


class AIConversationListResponse(BaseModel):
    conversations: List[AIConversationSummary]
    total: int
    page: int
    page_size: int


class AIUsageResponse(BaseModel):
    daily_limit: int
    messages_today: int
    remaining_today: int
    total_conversations: int
    total_messages: int
    reset_at: datetime


# ─── Health Schemas ────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    timestamp: datetime


# ─── Generic Pagination ────────────────────────────────────────────────────────

class PaginatedUsers(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
