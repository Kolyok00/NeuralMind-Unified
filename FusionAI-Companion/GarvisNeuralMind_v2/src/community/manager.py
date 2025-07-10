"""
Community Manager - Core community operations and orchestration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import (
    AsyncSessionLocal, User, Community, Post, Comment, 
    cache_user_online_status, get_online_users, cache_community_stats
)
from src.core.config import get_settings, get_community_features

logger = logging.getLogger(__name__)


class CommunityManager:
    """Manages community operations, user interactions, and social features."""
    
    def __init__(self):
        self.settings = get_settings()
        self.features = get_community_features()
        self.active_users: Dict[int, datetime] = {}
        self.community_stats_cache: Dict[int, Dict] = {}
        self._running = False
        
    async def start(self):
        """Start the community manager."""
        self._running = True
        logger.info("🚀 Community Manager started")
        
        # Start background tasks
        asyncio.create_task(self._update_user_activity())
        asyncio.create_task(self._update_community_stats())
        asyncio.create_task(self._cleanup_inactive_users())
        
    async def stop(self):
        """Stop the community manager."""
        self._running = False
        logger.info("🛑 Community Manager stopped")
    
    # User Management
    
    async def register_user_activity(self, user_id: int):
        """Register user activity for online status tracking."""
        self.active_users[user_id] = datetime.utcnow()
        await cache_user_online_status(user_id, True)
        
    async def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get comprehensive user profile with community stats."""
        async with AsyncSessionLocal() as session:
            # Get user data
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Get user statistics
            stats = await self._get_user_statistics(session, user_id)
            
            return {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "bio": user.bio,
                "avatar_url": user.avatar_url,
                "banner_url": user.banner_url,
                "reputation_score": user.reputation_score,
                "level": user.level,
                "experience_points": user.experience_points,
                "is_verified": user.is_verified,
                "is_premium": user.is_premium,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,
                "statistics": stats,
                "is_online": user_id in self.active_users
            }
    
    async def update_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Update user profile information."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Update allowed fields
            allowed_fields = ['display_name', 'bio', 'avatar_url', 'banner_url']
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user, field, profile_data[field])
            
            user.updated_at = datetime.utcnow()
            await session.commit()
            return True
    
    # Community Management
    
    async def create_community(self, creator_id: int, community_data: Dict) -> Optional[int]:
        """Create a new community."""
        async with AsyncSessionLocal() as session:
            community = Community(
                name=community_data['name'],
                description=community_data.get('description', ''),
                creator_id=creator_id,
                is_public=community_data.get('is_public', True),
                category=community_data.get('category', 'general'),
                tags=community_data.get('tags', [])
            )
            
            session.add(community)
            await session.commit()
            await session.refresh(community)
            
            logger.info(f"📊 New community created: {community.name} by user {creator_id}")
            return community.id
    
    async def get_community_list(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get list of public communities."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Community)
                .where(Community.is_public == True)
                .order_by(Community.member_count.desc())
                .limit(limit)
                .offset(offset)
            )
            communities = result.scalars().all()
            
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "avatar_url": c.avatar_url,
                    "member_count": c.member_count,
                    "category": c.category,
                    "tags": c.tags,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in communities
            ]
    
    async def join_community(self, user_id: int, community_id: int) -> bool:
        """Add user to community."""
        async with AsyncSessionLocal() as session:
            from src.core.database import CommunityMember
            
            # Check if already a member
            existing = await session.execute(
                select(CommunityMember)
                .where(
                    CommunityMember.user_id == user_id,
                    CommunityMember.community_id == community_id
                )
            )
            
            if existing.scalar_one_or_none():
                return False  # Already a member
            
            # Add membership
            member = CommunityMember(
                user_id=user_id,
                community_id=community_id
            )
            session.add(member)
            
            # Update community member count
            result = await session.execute(
                select(Community).where(Community.id == community_id)
            )
            community = result.scalar_one_or_none()
            
            if community:
                community.member_count += 1
                await session.commit()
                
                logger.info(f"👥 User {user_id} joined community {community_id}")
                return True
            
            return False
    
    # Content Management
    
    async def create_post(self, author_id: int, post_data: Dict) -> Optional[int]:
        """Create a new community post."""
        async with AsyncSessionLocal() as session:
            post = Post(
                title=post_data['title'],
                content=post_data['content'],
                author_id=author_id,
                community_id=post_data.get('community_id'),
                post_type=post_data.get('post_type', 'text'),
                tags=post_data.get('tags', [])
            )
            
            session.add(post)
            await session.commit()
            await session.refresh(post)
            
            # Award experience points to author
            await self._award_experience(author_id, 10, "post_creation")
            
            logger.info(f"📝 New post created: {post.title} by user {author_id}")
            return post.id
    
    async def get_community_feed(self, community_id: Optional[int] = None, 
                                limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get community feed posts."""
        async with AsyncSessionLocal() as session:
            query = select(Post).join(User, Post.author_id == User.id)
            
            if community_id:
                query = query.where(Post.community_id == community_id)
            
            query = query.where(Post.is_deleted == False).order_by(Post.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            result = await session.execute(query)
            posts = result.scalars().all()
            
            feed_items = []
            for post in posts:
                author = await session.get(User, post.author_id)
                feed_items.append({
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "post_type": post.post_type,
                    "upvotes": post.upvotes,
                    "downvotes": post.downvotes,
                    "comment_count": post.comment_count,
                    "tags": post.tags,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "author": {
                        "id": author.id,
                        "username": author.username,
                        "display_name": author.display_name,
                        "avatar_url": author.avatar_url,
                        "reputation_score": author.reputation_score
                    } if author else None
                })
            
            return feed_items
    
    # Engagement and Gamification
    
    async def vote_on_post(self, user_id: int, post_id: int, vote_type: str) -> bool:
        """Vote on a post (upvote/downvote)."""
        if vote_type not in ['upvote', 'downvote']:
            return False
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Post).where(Post.id == post_id)
            )
            post = result.scalar_one_or_none()
            
            if not post:
                return False
            
            # Update vote count
            if vote_type == 'upvote':
                post.upvotes += 1
                await self._award_experience(post.author_id, 5, "post_upvoted")
            else:
                post.downvotes += 1
            
            await session.commit()
            return True
    
    async def _award_experience(self, user_id: int, points: int, reason: str):
        """Award experience points to user."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.experience_points += points
                
                # Check for level up
                new_level = (user.experience_points // 100) + 1
                if new_level > user.level:
                    user.level = new_level
                    logger.info(f"🎉 User {user_id} leveled up to level {new_level}!")
                
                await session.commit()
    
    # Statistics and Analytics
    
    async def get_community_stats(self) -> Dict[str, Any]:
        """Get overall community statistics."""
        async with AsyncSessionLocal() as session:
            # User stats
            total_users = await session.scalar(select(func.count(User.id)))
            active_users_count = len(self.active_users)
            
            # Content stats
            total_posts = await session.scalar(select(func.count(Post.id)))
            total_comments = await session.scalar(select(func.count(Comment.id)))
            total_communities = await session.scalar(select(func.count(Community.id)))
            
            return {
                "users": {
                    "total": total_users or 0,
                    "online": active_users_count,
                    "active_today": len([
                        uid for uid, last_seen in self.active_users.items()
                        if last_seen > datetime.utcnow() - timedelta(days=1)
                    ])
                },
                "content": {
                    "total_posts": total_posts or 0,
                    "total_comments": total_comments or 0,
                    "total_communities": total_communities or 0
                },
                "engagement": {
                    "average_posts_per_user": (total_posts / max(total_users, 1)) if total_users else 0,
                    "active_community_ratio": active_users_count / max(total_users, 1) if total_users else 0
                }
            }
    
    async def _get_user_statistics(self, session: AsyncSession, user_id: int) -> Dict:
        """Get detailed user statistics."""
        post_count = await session.scalar(
            select(func.count(Post.id)).where(Post.author_id == user_id)
        )
        comment_count = await session.scalar(
            select(func.count(Comment.id)).where(Comment.author_id == user_id)
        )
        
        return {
            "posts_created": post_count or 0,
            "comments_made": comment_count or 0
        }
    
    async def get_health_status(self) -> str:
        """Get community health status."""
        stats = await self.get_community_stats()
        
        if stats["users"]["online"] > 10:
            return "excellent"
        elif stats["users"]["online"] > 5:
            return "good"
        elif stats["users"]["online"] > 0:
            return "moderate"
        else:
            return "low"
    
    # Background Tasks
    
    async def _update_user_activity(self):
        """Background task to update user activity."""
        while self._running:
            try:
                # Clean up inactive users (older than 5 minutes)
                cutoff = datetime.utcnow() - timedelta(minutes=5)
                inactive_users = [
                    uid for uid, last_seen in self.active_users.items()
                    if last_seen < cutoff
                ]
                
                for user_id in inactive_users:
                    del self.active_users[user_id]
                    await cache_user_online_status(user_id, False)
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Error in user activity update: {e}")
                await asyncio.sleep(60)
    
    async def _update_community_stats(self):
        """Background task to update community statistics."""
        while self._running:
            try:
                # Update global stats
                stats = await self.get_community_stats()
                
                # Cache individual community stats
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(Community.id))
                    community_ids = [row[0] for row in result.fetchall()]
                    
                    for community_id in community_ids:
                        community_stats = await self._get_community_specific_stats(community_id)
                        await cache_community_stats(community_id, community_stats)
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in community stats update: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_inactive_users(self):
        """Background task to clean up inactive users."""
        while self._running:
            try:
                # Update last_active_at for active users
                async with AsyncSessionLocal() as session:
                    for user_id in list(self.active_users.keys()):
                        result = await session.execute(
                            select(User).where(User.id == user_id)
                        )
                        user = result.scalar_one_or_none()
                        if user:
                            user.last_active_at = datetime.utcnow()
                    
                    await session.commit()
                
                await asyncio.sleep(600)  # Run every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(600)
    
    async def _get_community_specific_stats(self, community_id: int) -> Dict:
        """Get statistics for a specific community."""
        async with AsyncSessionLocal() as session:
            from src.core.database import CommunityMember
            
            member_count = await session.scalar(
                select(func.count(CommunityMember.id))
                .where(CommunityMember.community_id == community_id)
            )
            
            post_count = await session.scalar(
                select(func.count(Post.id))
                .where(Post.community_id == community_id)
            )
            
            return {
                "member_count": member_count or 0,
                "post_count": post_count or 0,
                "activity_score": (member_count or 0) + (post_count or 0) * 2
            }