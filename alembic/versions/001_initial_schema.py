"""initial_schema

Revision ID: 001
Revises: 
Create Date: 2025-01-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial database tables for ScholarGrid Backend API."""
    
    # ═══════════════════════════════════════════════════════════════════════
    # Users Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('firebase_uid', sa.String(length=128), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='student'),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('about', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tier', sa.String(length=20), nullable=False, server_default='bronze'),
        sa.Column('uploads_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('downloads_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("role IN ('student', 'admin')", name='check_user_role'),
        sa.CheckConstraint("status IN ('active', 'suspended')", name='check_user_status'),
        sa.CheckConstraint("tier IN ('bronze', 'silver', 'gold', 'elite')", name='check_user_tier'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_firebase_uid', 'users', ['firebase_uid'], unique=True)
    op.create_index('idx_users_score', 'users', [sa.text('score DESC')])
    op.create_index('idx_users_tier', 'users', ['tier'])
    op.create_index('idx_users_role', 'users', ['role'])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Notes Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('uploader_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_rating', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('rating_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('upload_date', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('status_updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name='check_note_status'),
        sa.ForeignKeyConstraint(['uploader_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notes_uploader_id', 'notes', ['uploader_id'])
    op.create_index('idx_notes_subject', 'notes', ['subject'])
    op.create_index('idx_notes_status', 'notes', ['status'])
    op.create_index('idx_notes_upload_date', 'notes', [sa.text('upload_date DESC')])
    op.create_index('idx_notes_average_rating', 'notes', [sa.text('average_rating DESC')])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Ratings Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'ratings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_value'),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('note_id', 'user_id', name='uq_rating_note_user')
    )
    op.create_index('idx_ratings_note_id', 'ratings', ['note_id'])
    op.create_index('idx_ratings_user_id', 'ratings', ['user_id'])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Downloads Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'downloads',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('downloaded_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_downloads_note_id', 'downloads', ['note_id'])
    op.create_index('idx_downloads_user_id', 'downloads', ['user_id'])
    op.create_index('idx_downloads_downloaded_at', 'downloads', [sa.text('downloaded_at DESC')])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Chat Groups Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'chat_groups',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('join_code', sa.String(length=8), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('member_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('last_message', sa.Text(), nullable=True),
        sa.Column('last_message_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_chat_groups_join_code', 'chat_groups', ['join_code'], unique=True)
    op.create_index('idx_chat_groups_creator_id', 'chat_groups', ['creator_id'])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Chat Memberships Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'chat_memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('joined_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['group_id'], ['chat_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'user_id', name='uq_membership_group_user')
    )
    op.create_index('idx_chat_memberships_group_id', 'chat_memberships', ['group_id'])
    op.create_index('idx_chat_memberships_user_id', 'chat_memberships', ['user_id'])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Messages Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False, server_default='text'),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("type IN ('text', 'file')", name='check_message_type'),
        sa.ForeignKeyConstraint(['group_id'], ['chat_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_group_id', 'messages', ['group_id'])
    op.create_index('idx_messages_sender_id', 'messages', ['sender_id'])
    op.create_index('idx_messages_created_at', 'messages', [sa.text('created_at DESC')])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Complaints Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'complaints',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='open'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('screenshot_url', sa.String(length=500), nullable=True),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('submitter_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("category IN ('technical', 'content', 'account', 'feature_request', 'other')", name='check_complaint_category'),
        sa.CheckConstraint("status IN ('open', 'in_progress', 'resolved', 'closed')", name='check_complaint_status'),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')", name='check_complaint_priority'),
        sa.ForeignKeyConstraint(['submitter_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_complaints_category', 'complaints', ['category'])
    op.create_index('idx_complaints_status', 'complaints', ['status'])
    op.create_index('idx_complaints_priority', 'complaints', ['priority'])
    op.create_index('idx_complaints_submitter_id', 'complaints', ['submitter_id'])
    op.create_index('idx_complaints_created_at', 'complaints', [sa.text('created_at DESC')])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Complaint Responses Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'complaint_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_complaint_responses_complaint_id', 'complaint_responses', ['complaint_id'])
    op.create_index('idx_complaint_responses_admin_id', 'complaint_responses', ['admin_id'])
    
    # ═══════════════════════════════════════════════════════════════════════
    # Activities Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("type IN ('note_upload', 'user_registration', 'high_rating')", name='check_activity_type'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_activities_type', 'activities', ['type'])
    op.create_index('idx_activities_user_id', 'activities', ['user_id'])
    op.create_index('idx_activities_created_at', 'activities', [sa.text('created_at DESC')])
    op.create_index('idx_activities_metadata', 'activities', ['metadata'], postgresql_using='gin')
    
    # ═══════════════════════════════════════════════════════════════════════
    # AI Conversations Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'ai_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_conversations_user_id', 'ai_conversations', ['user_id'])
    
    # ═══════════════════════════════════════════════════════════════════════
    # AI Messages Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'ai_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_ai_message_role'),
        sa.ForeignKeyConstraint(['conversation_id'], ['ai_conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_messages_conversation_id', 'ai_messages', ['conversation_id'])
    op.create_index('idx_ai_messages_created_at', 'ai_messages', [sa.text('created_at DESC')])
    
    # ═══════════════════════════════════════════════════════════════════════
    # AI Usage Tracking Table
    # ═══════════════════════════════════════════════════════════════════════
    op.create_table(
        'ai_usage_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='uq_ai_usage_user_date')
    )
    op.create_index('idx_ai_usage_tracking_user_id', 'ai_usage_tracking', ['user_id'])
    op.create_index('idx_ai_usage_user_date', 'ai_usage_tracking', ['user_id', 'date'])


def downgrade() -> None:
    """Drop all tables in reverse order to respect foreign key constraints."""
    
    # Drop tables in reverse order of creation
    op.drop_table('ai_usage_tracking')
    op.drop_table('ai_messages')
    op.drop_table('ai_conversations')
    op.drop_table('activities')
    op.drop_table('complaint_responses')
    op.drop_table('complaints')
    op.drop_table('messages')
    op.drop_table('chat_memberships')
    op.drop_table('chat_groups')
    op.drop_table('downloads')
    op.drop_table('ratings')
    op.drop_table('notes')
    op.drop_table('users')
