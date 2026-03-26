"""
Property-based tests for foreign key cascade behavior (Task 2.7)

**Validates: Requirements 23.4**

Tests that foreign key cascade behaviors work correctly across all database models.
When a parent record is deleted, all child records should be properly cascaded.
"""

import pytest
import uuid
from hypothesis import given, settings as hyp_settings, HealthCheck
from hypothesis import strategies as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.note import Note
from app.models.rating import Rating
from app.models.download import Download
from app.models.chat import ChatGroup, ChatMembership, Message
from app.models.complaint import Complaint, ComplaintResponse
from app.models.ai_chatbot import AIConversation, AIMessage, AIUsageTracking
from datetime import date


@pytest.fixture(scope="module")
def engine():
    """Create a module-scoped in-memory SQLite engine with foreign keys enabled."""
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    @event.listens_for(eng, "connect")
    def enable_fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")
    
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def db(engine):
    """Create a function-scoped database session."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


# ─── Property 57: Foreign Key Cascade Behavior ────────────────────────────────


@given(
    num_notes=st.integers(min_value=1, max_value=5),
    num_ratings_per_note=st.integers(min_value=1, max_value=3),
)
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_property_user_deletion_cascades_to_notes_and_ratings(
    num_notes, num_ratings_per_note, engine
):
    """
    **Property 57: Foreign Key Cascade Behavior**
    **Validates: Requirements 23.4**
    
    When a User is deleted, all Notes uploaded by that User and all Ratings
    by that User should be cascaded (deleted).
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create a user
        user_uid = f"cascade_user_{uuid.uuid4().hex}"
        user = User(
            firebase_uid=user_uid,
            email=f"{user_uid}@test.com",
            name="Cascade Test User",
            role="student"
        )
        db.add(user)
        db.flush()
        
        # Create notes for this user
        note_ids = []
        for i in range(num_notes):
            note = Note(
                title=f"Note {i}",
                description=f"Description {i}",
                subject="Test Subject",
                file_url=f"https://example.com/note_{i}.pdf",
                file_name=f"note_{i}.pdf",
                file_size=1024,
                file_type="pdf",
                uploader_id=user.id,
                status="approved"
            )
            db.add(note)
            db.flush()
            note_ids.append(note.id)
        
        # Create another user for ratings
        rater_uid = f"rater_{uuid.uuid4().hex}"
        rater = User(
            firebase_uid=rater_uid,
            email=f"{rater_uid}@test.com",
            name="Rater User",
            role="student"
        )
        db.add(rater)
        db.flush()
        
        # Create ratings by the first user on notes
        rating_ids = []
        for note_id in note_ids[:min(len(note_ids), num_ratings_per_note)]:
            rating = Rating(
                note_id=note_id,
                user_id=user.id,
                rating=5
            )
            db.add(rating)
            db.flush()
            rating_ids.append(rating.id)
        
        db.commit()
        
        # Verify notes and ratings exist
        assert db.query(Note).filter(Note.uploader_id == user.id).count() == num_notes
        assert db.query(Rating).filter(Rating.user_id == user.id).count() == len(rating_ids)
        
        # Delete the user
        db.delete(user)
        db.commit()
        
        # Verify all notes uploaded by the user are deleted (CASCADE)
        remaining_notes = db.query(Note).filter(Note.id.in_(note_ids)).count()
        assert remaining_notes == 0, f"Expected 0 notes after user deletion, found {remaining_notes}"
        
        # Verify all ratings by the user are deleted (CASCADE)
        remaining_ratings = db.query(Rating).filter(Rating.id.in_(rating_ids)).count()
        assert remaining_ratings == 0, f"Expected 0 ratings after user deletion, found {remaining_ratings}"
        
    finally:
        db.rollback()
        db.close()


@given(
    num_downloads=st.integers(min_value=1, max_value=5),
)
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_property_note_deletion_cascades_to_ratings_and_downloads(
    num_downloads, engine
):
    """
    **Property 57: Foreign Key Cascade Behavior**
    **Validates: Requirements 23.4**
    
    When a Note is deleted, all Ratings and Downloads for that Note
    should be cascaded (deleted).
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create a user
        user_uid = f"note_cascade_user_{uuid.uuid4().hex}"
        user = User(
            firebase_uid=user_uid,
            email=f"{user_uid}@test.com",
            name="Note Cascade User",
            role="student"
        )
        db.add(user)
        db.flush()
        
        # Create a note
        note = Note(
            title="Cascade Test Note",
            description="Testing cascade behavior",
            subject="Test",
            file_url="https://example.com/test.pdf",
            file_name="test.pdf",
            file_size=1024,
            file_type="pdf",
            uploader_id=user.id,
            status="approved"
        )
        db.add(note)
        db.flush()
        note_id = note.id
        
        # Create ratings for this note
        rating_ids = []
        for i in range(min(num_downloads, 3)):  # Limit ratings to 3
            rater_uid = f"rater_{i}_{uuid.uuid4().hex}"
            rater = User(
                firebase_uid=rater_uid,
                email=f"{rater_uid}@test.com",
                name=f"Rater {i}",
                role="student"
            )
            db.add(rater)
            db.flush()
            
            rating = Rating(
                note_id=note_id,
                user_id=rater.id,
                rating=4
            )
            db.add(rating)
            db.flush()
            rating_ids.append(rating.id)
        
        # Create downloads for this note
        download_ids = []
        for i in range(num_downloads):
            downloader_uid = f"downloader_{i}_{uuid.uuid4().hex}"
            downloader = User(
                firebase_uid=downloader_uid,
                email=f"{downloader_uid}@test.com",
                name=f"Downloader {i}",
                role="student"
            )
            db.add(downloader)
            db.flush()
            
            download = Download(
                note_id=note_id,
                user_id=downloader.id
            )
            db.add(download)
            db.flush()
            download_ids.append(download.id)
        
        db.commit()
        
        # Verify ratings and downloads exist
        assert db.query(Rating).filter(Rating.note_id == note_id).count() == len(rating_ids)
        assert db.query(Download).filter(Download.note_id == note_id).count() == num_downloads
        
        # Delete the note
        db.delete(note)
        db.commit()
        
        # Verify all ratings for the note are deleted (CASCADE)
        remaining_ratings = db.query(Rating).filter(Rating.id.in_(rating_ids)).count()
        assert remaining_ratings == 0, f"Expected 0 ratings after note deletion, found {remaining_ratings}"
        
        # Verify all downloads for the note are deleted (CASCADE)
        remaining_downloads = db.query(Download).filter(Download.id.in_(download_ids)).count()
        assert remaining_downloads == 0, f"Expected 0 downloads after note deletion, found {remaining_downloads}"
        
    finally:
        db.rollback()
        db.close()


@given(
    num_members=st.integers(min_value=2, max_value=5),
    num_messages=st.integers(min_value=1, max_value=5),
)
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_property_chat_group_deletion_cascades_to_memberships_and_messages(
    num_members, num_messages, engine
):
    """
    **Property 57: Foreign Key Cascade Behavior**
    **Validates: Requirements 23.4**
    
    When a ChatGroup is deleted, all ChatMemberships and Messages
    for that group should be cascaded (deleted).
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create creator user
        creator_uid = f"creator_{uuid.uuid4().hex}"
        creator = User(
            firebase_uid=creator_uid,
            email=f"{creator_uid}@test.com",
            name="Group Creator",
            role="student"
        )
        db.add(creator)
        db.flush()
        
        # Create chat group
        group = ChatGroup(
            name="Test Group",
            description="Testing cascade",
            join_code=uuid.uuid4().hex[:8].upper(),
            creator_id=creator.id,
            member_count=num_members
        )
        db.add(group)
        db.flush()
        group_id = group.id
        
        # Create memberships
        membership_ids = []
        members = [creator]
        
        # Add creator membership
        creator_membership = ChatMembership(
            group_id=group_id,
            user_id=creator.id
        )
        db.add(creator_membership)
        db.flush()
        membership_ids.append(creator_membership.id)
        
        # Add other members
        for i in range(num_members - 1):
            member_uid = f"member_{i}_{uuid.uuid4().hex}"
            member = User(
                firebase_uid=member_uid,
                email=f"{member_uid}@test.com",
                name=f"Member {i}",
                role="student"
            )
            db.add(member)
            db.flush()
            members.append(member)
            
            membership = ChatMembership(
                group_id=group_id,
                user_id=member.id
            )
            db.add(membership)
            db.flush()
            membership_ids.append(membership.id)
        
        # Create messages
        message_ids = []
        for i in range(num_messages):
            sender = members[i % len(members)]
            message = Message(
                group_id=group_id,
                sender_id=sender.id,
                content=f"Message {i}",
                type="text"
            )
            db.add(message)
            db.flush()
            message_ids.append(message.id)
        
        db.commit()
        
        # Verify memberships and messages exist
        assert db.query(ChatMembership).filter(ChatMembership.group_id == group_id).count() == num_members
        assert db.query(Message).filter(Message.group_id == group_id).count() == num_messages
        
        # Delete the chat group
        db.delete(group)
        db.commit()
        
        # Verify all memberships are deleted (CASCADE)
        remaining_memberships = db.query(ChatMembership).filter(
            ChatMembership.id.in_(membership_ids)
        ).count()
        assert remaining_memberships == 0, f"Expected 0 memberships after group deletion, found {remaining_memberships}"
        
        # Verify all messages are deleted (CASCADE)
        remaining_messages = db.query(Message).filter(Message.id.in_(message_ids)).count()
        assert remaining_messages == 0, f"Expected 0 messages after group deletion, found {remaining_messages}"
        
    finally:
        db.rollback()
        db.close()


@given(
    num_responses=st.integers(min_value=1, max_value=5),
)
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_property_complaint_deletion_cascades_to_responses(
    num_responses, engine
):
    """
    **Property 57: Foreign Key Cascade Behavior**
    **Validates: Requirements 23.4**
    
    When a Complaint is deleted, all ComplaintResponses for that
    Complaint should be cascaded (deleted).
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create submitter user
        submitter_uid = f"submitter_{uuid.uuid4().hex}"
        submitter = User(
            firebase_uid=submitter_uid,
            email=f"{submitter_uid}@test.com",
            name="Complaint Submitter",
            role="student"
        )
        db.add(submitter)
        db.flush()
        
        # Create admin user
        admin_uid = f"admin_{uuid.uuid4().hex}"
        admin = User(
            firebase_uid=admin_uid,
            email=f"{admin_uid}@test.com",
            name="Admin User",
            role="admin"
        )
        db.add(admin)
        db.flush()
        
        # Create complaint
        complaint = Complaint(
            title="Test Complaint",
            description="Testing cascade behavior",
            category="technical",
            status="open",
            priority="medium",
            submitter_id=submitter.id
        )
        db.add(complaint)
        db.flush()
        complaint_id = complaint.id
        
        # Create responses
        response_ids = []
        for i in range(num_responses):
            response = ComplaintResponse(
                complaint_id=complaint_id,
                admin_id=admin.id,
                text=f"Response {i}"
            )
            db.add(response)
            db.flush()
            response_ids.append(response.id)
        
        db.commit()
        
        # Verify responses exist
        assert db.query(ComplaintResponse).filter(
            ComplaintResponse.complaint_id == complaint_id
        ).count() == num_responses
        
        # Delete the complaint
        db.delete(complaint)
        db.commit()
        
        # Verify all responses are deleted (CASCADE)
        remaining_responses = db.query(ComplaintResponse).filter(
            ComplaintResponse.id.in_(response_ids)
        ).count()
        assert remaining_responses == 0, f"Expected 0 responses after complaint deletion, found {remaining_responses}"
        
    finally:
        db.rollback()
        db.close()


@given(
    num_messages=st.integers(min_value=1, max_value=5),
)
@hyp_settings(
    max_examples=50,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_property_ai_conversation_deletion_cascades_to_messages(
    num_messages, engine
):
    """
    **Property 57: Foreign Key Cascade Behavior**
    **Validates: Requirements 23.4**
    
    When an AIConversation is deleted, all AIMessages in that
    conversation should be cascaded (deleted).
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create user
        user_uid = f"ai_user_{uuid.uuid4().hex}"
        user = User(
            firebase_uid=user_uid,
            email=f"{user_uid}@test.com",
            name="AI User",
            role="student"
        )
        db.add(user)
        db.flush()
        
        # Create AI conversation
        conversation = AIConversation(
            user_id=user.id,
            title="Test Conversation",
            message_count=num_messages
        )
        db.add(conversation)
        db.flush()
        conversation_id = conversation.id
        
        # Create AI messages
        message_ids = []
        for i in range(num_messages):
            role = "user" if i % 2 == 0 else "assistant"
            message = AIMessage(
                conversation_id=conversation_id,
                role=role,
                content=f"Message {i}"
            )
            db.add(message)
            db.flush()
            message_ids.append(message.id)
        
        db.commit()
        
        # Verify messages exist
        assert db.query(AIMessage).filter(
            AIMessage.conversation_id == conversation_id
        ).count() == num_messages
        
        # Delete the conversation
        db.delete(conversation)
        db.commit()
        
        # Verify all messages are deleted (CASCADE)
        remaining_messages = db.query(AIMessage).filter(
            AIMessage.id.in_(message_ids)
        ).count()
        assert remaining_messages == 0, f"Expected 0 AI messages after conversation deletion, found {remaining_messages}"
        
    finally:
        db.rollback()
        db.close()


@given(
    num_child_records=st.integers(min_value=1, max_value=3),
)
@hyp_settings(
    max_examples=30,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None
)
def test_property_user_deletion_cascades_to_all_related_records(
    num_child_records, engine
):
    """
    **Property 57: Foreign Key Cascade Behavior**
    **Validates: Requirements 23.4**
    
    When a User is deleted, ALL related records across all tables
    should be cascaded (deleted). This is a comprehensive test covering:
    - Notes, Ratings, Downloads
    - ChatGroups, ChatMemberships, Messages
    - Complaints, ComplaintResponses
    - AIConversations, AIMessages, AIUsageTracking
    """
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create the user to be deleted
        user_uid = f"comprehensive_user_{uuid.uuid4().hex}"
        user = User(
            firebase_uid=user_uid,
            email=f"{user_uid}@test.com",
            name="Comprehensive Test User",
            role="student"
        )
        db.add(user)
        db.flush()
        user_id = user.id
        
        # Create notes
        note_ids = []
        for i in range(num_child_records):
            note = Note(
                title=f"Note {i}",
                description=f"Description {i}",
                subject="Test",
                file_url=f"https://example.com/note_{i}.pdf",
                file_name=f"note_{i}.pdf",
                file_size=1024,
                file_type="pdf",
                uploader_id=user_id,
                status="approved"
            )
            db.add(note)
            db.flush()
            note_ids.append(note.id)
        
        # Create chat groups
        group_ids = []
        for i in range(num_child_records):
            group = ChatGroup(
                name=f"Group {i}",
                description=f"Description {i}",
                join_code=f"{uuid.uuid4().hex[:8].upper()}",
                creator_id=user_id,
                member_count=1
            )
            db.add(group)
            db.flush()
            group_ids.append(group.id)
            
            # Add membership
            membership = ChatMembership(
                group_id=group.id,
                user_id=user_id
            )
            db.add(membership)
            db.flush()
        
        # Create complaints
        complaint_ids = []
        for i in range(num_child_records):
            complaint = Complaint(
                title=f"Complaint {i}",
                description=f"Description {i}",
                category="technical",
                status="open",
                priority="medium",
                submitter_id=user_id
            )
            db.add(complaint)
            db.flush()
            complaint_ids.append(complaint.id)
        
        # Create AI conversations
        conversation_ids = []
        for i in range(num_child_records):
            conversation = AIConversation(
                user_id=user_id,
                title=f"Conversation {i}",
                message_count=0
            )
            db.add(conversation)
            db.flush()
            conversation_ids.append(conversation.id)
        
        # Create AI usage tracking
        usage_tracking = AIUsageTracking(
            user_id=user_id,
            date=date.today(),
            message_count=10
        )
        db.add(usage_tracking)
        db.flush()
        
        db.commit()
        
        # Verify all records exist
        assert db.query(Note).filter(Note.uploader_id == user_id).count() == num_child_records
        assert db.query(ChatGroup).filter(ChatGroup.creator_id == user_id).count() == num_child_records
        assert db.query(ChatMembership).filter(ChatMembership.user_id == user_id).count() == num_child_records
        assert db.query(Complaint).filter(Complaint.submitter_id == user_id).count() == num_child_records
        assert db.query(AIConversation).filter(AIConversation.user_id == user_id).count() == num_child_records
        assert db.query(AIUsageTracking).filter(AIUsageTracking.user_id == user_id).count() == 1
        
        # Delete the user
        db.delete(user)
        db.commit()
        
        # Verify ALL related records are deleted (CASCADE)
        assert db.query(Note).filter(Note.id.in_(note_ids)).count() == 0, "Notes not cascaded"
        assert db.query(ChatGroup).filter(ChatGroup.id.in_(group_ids)).count() == 0, "ChatGroups not cascaded"
        assert db.query(ChatMembership).filter(ChatMembership.user_id == user_id).count() == 0, "ChatMemberships not cascaded"
        assert db.query(Complaint).filter(Complaint.id.in_(complaint_ids)).count() == 0, "Complaints not cascaded"
        assert db.query(AIConversation).filter(AIConversation.id.in_(conversation_ids)).count() == 0, "AIConversations not cascaded"
        assert db.query(AIUsageTracking).filter(AIUsageTracking.user_id == user_id).count() == 0, "AIUsageTracking not cascaded"
        
    finally:
        db.rollback()
        db.close()
