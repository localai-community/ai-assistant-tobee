#!/usr/bin/env python3
"""
Script to clean up conversations in the database.

This script will:
1. Delete conversations related to guest users (user_id = '00000000-0000-0000-0000-000000000001')
2. Delete conversations that are not related to any user (user_id = NULL)
3. Also delete associated messages and documents for these conversations

Usage:
    python cleanup_conversations.py [--dry-run] [--confirm]
    
Options:
    --dry-run    Show what would be deleted without actually deleting
    --confirm    Actually perform the deletion (required for safety)
"""

import sys
import os
import argparse
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models.database import Conversation, Message, ChatDocument, DocumentChunk, User
from app.core.config import settings

# Guest user ID constant
GUEST_USER_ID = '00000000-0000-0000-0000-000000000001'

def get_conversations_to_delete(db: Session) -> Tuple[List[Conversation], List[Conversation]]:
    """
    Get conversations that should be deleted.
    
    Returns:
        Tuple of (guest_conversations, orphaned_conversations)
    """
    # Get conversations related to guest users
    guest_conversations = db.query(Conversation).filter(
        Conversation.user_id == GUEST_USER_ID,
        Conversation.is_active == True
    ).all()
    
    # Get conversations not related to any user (user_id is NULL)
    orphaned_conversations = db.query(Conversation).filter(
        Conversation.user_id.is_(None),
        Conversation.is_active == True
    ).all()
    
    return guest_conversations, orphaned_conversations

def get_related_data(db: Session, conversation_ids: List[str]) -> dict:
    """
    Get related data (messages, documents, chunks) for the given conversation IDs.
    
    Returns:
        Dictionary with counts of related data
    """
    if not conversation_ids:
        return {
            'messages': 0,
            'documents': 0,
            'chunks': 0
        }
    
    # Count messages
    message_count = db.query(Message).filter(
        Message.conversation_id.in_(conversation_ids)
    ).count()
    
    # Count documents
    document_count = db.query(ChatDocument).filter(
        ChatDocument.conversation_id.in_(conversation_ids)
    ).count()
    
    # Count document chunks (through documents)
    chunk_count = db.query(DocumentChunk).join(
        ChatDocument, DocumentChunk.document_id == ChatDocument.id
    ).filter(
        ChatDocument.conversation_id.in_(conversation_ids)
    ).count()
    
    return {
        'messages': message_count,
        'documents': document_count,
        'chunks': chunk_count
    }

def delete_conversations_and_related_data(db: Session, conversations: List[Conversation]) -> dict:
    """
    Delete conversations and all their related data.
    
    Returns:
        Dictionary with counts of deleted items
    """
    if not conversations:
        return {
            'conversations': 0,
            'messages': 0,
            'documents': 0,
            'chunks': 0
        }
    
    conversation_ids = [conv.id for conv in conversations]
    
    # Get document IDs first to delete chunks
    document_ids = db.query(ChatDocument.id).filter(
        ChatDocument.conversation_id.in_(conversation_ids)
    ).all()
    document_id_list = [doc_id[0] for doc_id in document_ids]
    
    # Delete document chunks first (they reference documents)
    chunk_count = 0
    if document_id_list:
        chunk_count = db.query(DocumentChunk).filter(
            DocumentChunk.document_id.in_(document_id_list)
        ).delete(synchronize_session=False)
    
    # Delete documents
    document_count = db.query(ChatDocument).filter(
        ChatDocument.conversation_id.in_(conversation_ids)
    ).delete(synchronize_session=False)
    
    # Delete messages
    message_count = db.query(Message).filter(
        Message.conversation_id.in_(conversation_ids)
    ).delete(synchronize_session=False)
    
    # Finally delete conversations
    conversation_count = db.query(Conversation).filter(
        Conversation.id.in_(conversation_ids)
    ).delete(synchronize_session=False)
    
    # Commit the transaction
    db.commit()
    
    return {
        'conversations': conversation_count,
        'messages': message_count,
        'documents': document_count,
        'chunks': chunk_count
    }

def main():
    parser = argparse.ArgumentParser(description='Clean up conversations in the database')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--confirm', action='store_true',
                       help='Actually perform the deletion (required for safety)')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.confirm:
        print("❌ Error: You must use either --dry-run or --confirm")
        print("   Use --dry-run to see what would be deleted")
        print("   Use --confirm to actually perform the deletion")
        sys.exit(1)
    
    print(f"🔍 Connecting to database: {settings.database_url}")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get conversations to delete
        guest_conversations, orphaned_conversations = get_conversations_to_delete(db)
        
        print(f"\n📊 Found conversations to delete:")
        print(f"   Guest user conversations: {len(guest_conversations)}")
        print(f"   Orphaned conversations (no user): {len(orphaned_conversations)}")
        print(f"   Total conversations: {len(guest_conversations) + len(orphaned_conversations)}")
        
        if not guest_conversations and not orphaned_conversations:
            print("✅ No conversations found to delete. Database is clean!")
            return
        
        # Show details of conversations to be deleted
        all_conversations = guest_conversations + orphaned_conversations
        conversation_ids = [conv.id for conv in all_conversations]
        
        print(f"\n📋 Conversations to be deleted:")
        for conv in all_conversations:
            user_type = "Guest" if conv.user_id == GUEST_USER_ID else "Orphaned"
            print(f"   - {conv.id[:8]}... ({user_type}) - '{conv.title or 'Untitled'}' - {conv.model}")
        
        # Get related data counts
        related_data = get_related_data(db, conversation_ids)
        
        print(f"\n📈 Related data to be deleted:")
        print(f"   Messages: {related_data['messages']}")
        print(f"   Documents: {related_data['documents']}")
        print(f"   Document chunks: {related_data['chunks']}")
        
        if args.dry_run:
            print(f"\n🔍 DRY RUN - No data was actually deleted")
            print(f"   To perform the actual deletion, run with --confirm")
        else:
            print(f"\n⚠️  WARNING: This will permanently delete the data shown above!")
            print(f"   Proceeding with deletion...")
            
            # Perform the deletion
            deleted_counts = delete_conversations_and_related_data(db, all_conversations)
            
            print(f"\n✅ Deletion completed successfully!")
            print(f"   Deleted conversations: {deleted_counts['conversations']}")
            print(f"   Deleted messages: {deleted_counts['messages']}")
            print(f"   Deleted documents: {deleted_counts['documents']}")
            print(f"   Deleted document chunks: {deleted_counts['chunks']}")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
