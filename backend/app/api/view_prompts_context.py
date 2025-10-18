"""
LocalAI Community - View Prompts Context API Endpoints
API routes for viewing prompts and context data used in AI interactions.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from ..core.database import get_db
from ..services.repository import UserQuestionRepository, AIPromptRepository, ContextAwarenessRepository
from ..models.schemas import (
    UserQuestion, AIPrompt, ContextAwarenessData, QuestionDetails,
    UserQuestionCreate, AIPromptCreate, ContextAwarenessDataCreate
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/view-prompts-context", tags=["view-prompts-context"])

@router.get("/questions/{question_id}/prompt", response_model=AIPrompt)
async def get_question_prompt(
    question_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the AI prompt for a specific question.
    
    Args:
        question_id: The ID of the question
        db: Database session
        
    Returns:
        AIPrompt: The prompt data for the question
        
    Raises:
        HTTPException: If question or prompt not found
    """
    try:
        prompt_repo = AIPromptRepository(db)
        prompt = prompt_repo.get_prompt_by_question(question_id)
        
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt not found for question ID: {question_id}"
            )
        
        return prompt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving prompt for question {question_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving prompt"
        )

@router.get("/questions/{question_id}/context", response_model=List[ContextAwarenessData])
async def get_question_context(
    question_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the context awareness data for a specific question.
    
    Args:
        question_id: The ID of the question
        db: Database session
        
    Returns:
        List[ContextAwarenessData]: List of context data for the question
        
    Raises:
        HTTPException: If question not found or error occurs
    """
    try:
        context_repo = ContextAwarenessRepository(db)
        context_data = context_repo.get_context_by_question(question_id)
        
        return context_data
        
    except Exception as e:
        logger.error(f"Error retrieving context for question {question_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving context data"
        )

@router.get("/questions/{question_id}/details", response_model=QuestionDetails)
async def get_question_details(
    question_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete details for a specific question including prompt and context.
    
    Args:
        question_id: The ID of the question
        db: Database session
        
    Returns:
        QuestionDetails: Complete question details with prompt and context
        
    Raises:
        HTTPException: If question not found or error occurs
    """
    try:
        question_repo = UserQuestionRepository(db)
        prompt_repo = AIPromptRepository(db)
        context_repo = ContextAwarenessRepository(db)
        
        # Get the question
        question = question_repo.get_question(question_id)
        if not question:
            raise HTTPException(
                status_code=404,
                detail=f"Question not found with ID: {question_id}"
            )
        
        # Get the prompt (optional)
        prompt = prompt_repo.get_prompt_by_question(question_id)
        
        # Get the context data
        context_data = context_repo.get_context_by_question(question_id)
        
        return QuestionDetails(
            question=question,
            prompt=prompt,
            context_data=context_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving details for question {question_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving question details"
        )

@router.get("/conversations/{conversation_id}/questions", response_model=List[UserQuestion])
async def get_conversation_questions(
    conversation_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all questions for a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        limit: Maximum number of questions to return
        db: Database session
        
    Returns:
        List[UserQuestion]: List of questions for the conversation
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        question_repo = UserQuestionRepository(db)
        questions = question_repo.get_questions_by_conversation(conversation_id, limit)
        
        return questions
        
    except Exception as e:
        logger.error(f"Error retrieving questions for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving conversation questions"
        )

@router.get("/conversations/{conversation_id}/prompts", response_model=List[AIPrompt])
async def get_conversation_prompts(
    conversation_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all prompts for a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        limit: Maximum number of prompts to return
        db: Database session
        
    Returns:
        List[AIPrompt]: List of prompts for the conversation
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        prompt_repo = AIPromptRepository(db)
        prompts = prompt_repo.get_prompts_by_conversation(conversation_id, limit)
        
        return prompts
        
    except Exception as e:
        logger.error(f"Error retrieving prompts for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving conversation prompts"
        )

@router.get("/conversations/{conversation_id}/context", response_model=List[ContextAwarenessData])
async def get_conversation_context(
    conversation_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all context data for a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        limit: Maximum number of context entries to return
        db: Database session
        
    Returns:
        List[ContextAwarenessData]: List of context data for the conversation
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        context_repo = ContextAwarenessRepository(db)
        context_data = context_repo.get_context_by_conversation(conversation_id, limit)
        
        return context_data
        
    except Exception as e:
        logger.error(f"Error retrieving context for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving conversation context"
        )

@router.get("/users/{user_id}/questions", response_model=List[UserQuestion])
async def get_user_questions(
    user_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all questions for a specific user.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of questions to return
        db: Database session
        
    Returns:
        List[UserQuestion]: List of questions for the user
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        question_repo = UserQuestionRepository(db)
        questions = question_repo.get_questions_by_user(user_id, limit)
        
        return questions
        
    except Exception as e:
        logger.error(f"Error retrieving questions for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving user questions"
        )

@router.get("/users/{user_id}/prompts", response_model=List[AIPrompt])
async def get_user_prompts(
    user_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all prompts for a specific user.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of prompts to return
        db: Database session
        
    Returns:
        List[AIPrompt]: List of prompts for the user
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        prompt_repo = AIPromptRepository(db)
        prompts = prompt_repo.get_prompts_by_user(user_id, limit)
        
        return prompts
        
    except Exception as e:
        logger.error(f"Error retrieving prompts for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving user prompts"
        )

@router.get("/users/{user_id}/context", response_model=List[ContextAwarenessData])
async def get_user_context(
    user_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all context data for a specific user.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of context entries to return
        db: Database session
        
    Returns:
        List[ContextAwarenessData]: List of context data for the user
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        context_repo = ContextAwarenessRepository(db)
        context_data = context_repo.get_context_by_user(user_id, limit)
        
        return context_data
        
    except Exception as e:
        logger.error(f"Error retrieving context for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving user context"
        )
