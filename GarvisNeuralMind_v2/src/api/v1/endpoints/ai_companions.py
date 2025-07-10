"""
AI Companions endpoints for community features.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from src.core.database import AsyncSessionLocal, AICompanion, User
from src.api.v1.endpoints.auth import get_current_user
from sqlalchemy import select, update

router = APIRouter()


# Request/Response models
class AICompanionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    personality_traits: Optional[Dict[str, Any]] = {}
    voice_settings: Optional[Dict[str, Any]] = {}
    avatar_config: Optional[Dict[str, Any]] = {}
    model_type: Optional[str] = "gpt-3.5-turbo"
    model_settings: Optional[Dict[str, Any]] = {}
    is_public: Optional[bool] = False


class AICompanionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    personality_traits: Optional[Dict[str, Any]] = None
    voice_settings: Optional[Dict[str, Any]] = None
    avatar_config: Optional[Dict[str, Any]] = None
    model_type: Optional[str] = None
    model_settings: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class AICompanionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    personality_traits: Dict[str, Any]
    voice_settings: Dict[str, Any]
    avatar_config: Dict[str, Any]
    model_type: str
    model_settings: Dict[str, Any]
    owner_id: Optional[int]
    is_public: bool
    interaction_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AICompanionInteraction(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}


class AICompanionInteractionResponse(BaseModel):
    response: str
    companion_id: int
    interaction_id: str
    timestamp: datetime


# Helper function to convert database model to response model
def companion_to_response(companion: AICompanion) -> AICompanionResponse:
    """Convert AICompanion database model to response model."""
    return AICompanionResponse.from_orm(companion)


# AI Companions endpoints

@router.get("/", response_model=List[AICompanionResponse])
async def list_ai_companions(
    skip: int = 0,
    limit: int = 100,
    public_only: bool = True,
    current_user: User = Depends(get_current_user)
):
    """List AI companions."""
    async with AsyncSessionLocal() as session:
        query = select(AICompanion)

        if public_only:
            query = query.where(AICompanion.is_public)
        else:
            # Show public companions and user's own companions
            query = query.where(
                (AICompanion.is_public) |
                (AICompanion.owner_id == current_user.id)
            )

        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        companions = result.scalars().all()

        return [companion_to_response(companion) for companion in companions]


@router.post("/", response_model=AICompanionResponse)
async def create_ai_companion(
    companion_data: AICompanionCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new AI companion."""
    async with AsyncSessionLocal() as session:
        # Check if user already has a companion with this name
        existing = await session.execute(
            select(AICompanion).where(
                AICompanion.owner_id == current_user.id,
                AICompanion.name == companion_data.name
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a companion with this name"
            )

        # Create new companion
        new_companion = AICompanion(
            name=companion_data.name,
            description=companion_data.description,
            personality_traits=companion_data.personality_traits,
            voice_settings=companion_data.voice_settings,
            avatar_config=companion_data.avatar_config,
            model_type=companion_data.model_type,
            model_settings=companion_data.model_settings,
            owner_id=current_user.id,
            is_public=companion_data.is_public,
            created_at=datetime.utcnow()
        )

        session.add(new_companion)
        await session.commit()
        await session.refresh(new_companion)

        return companion_to_response(new_companion)


@router.get("/{companion_id}", response_model=AICompanionResponse)
async def get_ai_companion(
    companion_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific AI companion."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AICompanion).where(AICompanion.id == companion_id)
        )
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI companion not found"
            )

        # Check if user can access this companion
        if (not companion.is_public and  # type: ignore
                companion.owner_id != current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this AI companion"
            )

        return companion_to_response(companion)


@router.put("/{companion_id}", response_model=AICompanionResponse)
async def update_ai_companion(
    companion_id: int,
    companion_data: AICompanionUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update an AI companion."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AICompanion).where(AICompanion.id == companion_id)
        )
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI companion not found"
            )

        # Check if user owns this companion
        if companion.owner_id != current_user.id:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own AI companions"
            )

        # Update fields
        update_data = companion_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(companion, field, value)

        # Update timestamp will be handled by SQLAlchemy onupdate
        await session.commit()
        await session.refresh(companion)

        return companion_to_response(companion)


@router.delete("/{companion_id}")
async def delete_ai_companion(
    companion_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete an AI companion."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AICompanion).where(AICompanion.id == companion_id)
        )
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI companion not found"
            )

        # Check if user owns this companion
        if companion.owner_id != current_user.id:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own AI companions"
            )

        await session.delete(companion)
        await session.commit()

        return {"message": "AI companion deleted successfully"}


@router.post(
    "/{companion_id}/interact",
    response_model=AICompanionInteractionResponse
)
async def interact_with_companion(
    companion_id: int,
    interaction: AICompanionInteraction,
    current_user: User = Depends(get_current_user)
):
    """Interact with an AI companion."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AICompanion).where(AICompanion.id == companion_id)
        )
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI companion not found"
            )

        # Check if user can interact with this companion
        if (not companion.is_public and  # type: ignore
                companion.owner_id != current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this AI companion"
            )

        # TODO: Implement actual AI interaction logic here
        # For now, return a simple response
        response_text = (
            f"Hello {current_user.username}! I'm {companion.name}. "
            f"You said: {interaction.message}"
        )

        # Update interaction count using SQLAlchemy update
        await session.execute(
            update(AICompanion)
            .where(AICompanion.id == companion_id)
            .values(interaction_count=AICompanion.interaction_count + 1)
        )
        await session.commit()

        # Refresh the companion object to get updated values
        await session.refresh(companion)

        return AICompanionInteractionResponse(
            response=response_text,
            companion_id=companion.id,  # type: ignore
            interaction_id=(
                f"int_{companion.id}_{datetime.utcnow().timestamp()}"
            ),
            timestamp=datetime.utcnow()
        )


@router.get("/{companion_id}/stats")
async def get_companion_stats(
    companion_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get AI companion statistics."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AICompanion).where(AICompanion.id == companion_id)
        )
        companion = result.scalar_one_or_none()

        if not companion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI companion not found"
            )

        # Check if user can access this companion
        if (not companion.is_public and  # type: ignore
                companion.owner_id != current_user.id):  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this AI companion"
            )

        return {
            "companion_id": companion.id,
            "name": companion.name,
            "total_interactions": companion.interaction_count,
            "created_at": companion.created_at,
            "is_public": companion.is_public,
            "model_type": companion.model_type
        }
