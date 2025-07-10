"""
Database configuration and models for GarvisNeuralMind Community System.
"""

import asyncio
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime, ForeignKey, 
    JSON, Float, UniqueConstraint, Index, create_engine
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
import redis.asyncio as redis

from src.core.config import get_settings

# Database base
Base = declarative_base()

# Async engine and session
settings = get_settings()
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=0
)

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL)


# Database Models

class User(Base):
    """Community user model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    display_name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(500))
    banner_url = Column(String(500))
    
    # Community stats
    reputation_score = Column(Integer, default=0)
    level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    privacy_settings = Column(JSON, default=lambda: {})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True))
    
    # Relationships
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")


class Community(Base):
    """Community/Group model."""
    __tablename__ = "communities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    avatar_url = Column(String(500))
    banner_url = Column(String(500))
    
    # Community settings
    is_public = Column(Boolean, default=True)
    member_count = Column(Integer, default=0)
    max_members = Column(Integer, default=1000)
    category = Column(String(50))
    tags = Column(JSON, default=list)
    
    # Creator and moderation
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    posts = relationship("Post", back_populates="community")
    members = relationship("CommunityMember", back_populates="community")


class CommunityMember(Base):
    """Community membership model."""
    __tablename__ = "community_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)
    
    # Membership details
    role = Column(String(20), default="member")  # member, moderator, admin
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    community = relationship("Community", back_populates="members")
    
    __table_args__ = (UniqueConstraint('user_id', 'community_id', name='unique_user_community'),)


class Post(Base):
    """Community post model."""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(String(20), default="text")  # text, image, video, poll
    
    # Author and community
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    community_id = Column(Integer, ForeignKey("communities.id"))
    
    # Engagement
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    
    # Content metadata
    attachments = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    
    # Moderation
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="posts")
    community = relationship("Community", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    """Comment model for posts."""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    # Author and post
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"))  # For nested comments
    
    # Engagement
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    
    # Moderation
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id])


class Message(Base):
    """Direct message model."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, image, file
    
    # Sender and receiver
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message metadata
    attachments = Column(JSON, default=list)
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    
    # Indexes for message queries
    __table_args__ = (
        Index('ix_messages_conversation', 'sender_id', 'receiver_id', 'created_at'),
    )


class AICompanion(Base):
    """AI Companion/VTuber model."""
    __tablename__ = "ai_companions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Companion personality
    personality_traits = Column(JSON, default=dict)
    voice_settings = Column(JSON, default=dict)
    avatar_config = Column(JSON, default=dict)
    
    # AI Model configuration
    model_type = Column(String(50), default="gpt-3.5-turbo")
    model_settings = Column(JSON, default=dict)
    
    # Community integration
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    interaction_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User")


# Database management functions

async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Create some initial data if needed
    await create_initial_data()


async def create_initial_data():
    """Create initial community data."""
    async with AsyncSessionLocal() as session:
        # Check if we already have data
        result = await session.execute("SELECT COUNT(*) FROM users")
        user_count = result.scalar()
        
        if user_count == 0:
            # Create default community
            default_community = Community(
                name="general",
                description="Általános beszélgetések a GarvisNeuralMind community-ben",
                is_public=True,
                creator_id=1  # Will be created by first user
            )
            session.add(default_community)
            await session.commit()


# Redis operations for caching and real-time features

async def cache_user_online_status(user_id: int, is_online: bool):
    """Cache user online status in Redis."""
    await redis_client.set(f"user:{user_id}:online", int(is_online), ex=300)  # 5 min expiry


async def get_online_users() -> List[int]:
    """Get list of online user IDs."""
    pattern = "user:*:online"
    keys = await redis_client.keys(pattern)
    online_users = []
    
    for key in keys:
        value = await redis_client.get(key)
        if value and int(value) == 1:
            user_id = int(key.decode().split(':')[1])
            online_users.append(user_id)
    
    return online_users


async def cache_community_stats(community_id: int, stats: dict):
    """Cache community statistics."""
    await redis_client.set(
        f"community:{community_id}:stats", 
        str(stats), 
        ex=3600  # 1 hour expiry
    )