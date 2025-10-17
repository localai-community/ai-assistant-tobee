# Database Cleanup Script

This script helps clean up conversations in the database by removing:
1. Conversations related to guest users (user_id = '00000000-0000-0000-0000-000000000001')
2. Conversations that are not related to any user (user_id = NULL)

## Usage

### Prerequisites
- Activate the virtual environment: `source venv/bin/activate`
- Ensure the database is accessible

### Commands

#### Dry Run (Recommended First)
```bash
python cleanup_conversations.py --dry-run
```
This shows what would be deleted without actually deleting anything.

#### Actual Deletion
```bash
python cleanup_conversations.py --confirm
```
This permanently deletes the conversations and all related data.

## What Gets Deleted

The script deletes:
- **Conversations**: Guest user conversations and orphaned conversations
- **Messages**: All messages belonging to those conversations
- **Documents**: All documents uploaded to those conversations
- **Document Chunks**: All document chunks (embeddings) for those documents

## Safety Features

- **Dry run mode**: Always test with `--dry-run` first
- **Confirmation required**: Must use `--confirm` flag to actually delete
- **Detailed reporting**: Shows exactly what will be deleted before proceeding
- **Transaction safety**: Uses database transactions for atomic operations

## Example Output

```
🔍 Connecting to database: sqlite:///./localai_community.db

📊 Found conversations to delete:
   Guest user conversations: 5
   Orphaned conversations (no user): 0
   Total conversations: 5

📋 Conversations to be deleted:
   - 470627be... (Guest) - 'Conversation 2025-10-16 20:30' - deepseek-r1:8b
   - 263b6c20... (Guest) - 'Conversation 2025-10-16 20:55' - llama3.2
   ...

📈 Related data to be deleted:
   Messages: 8
   Documents: 0
   Document chunks: 0

✅ Deletion completed successfully!
   Deleted conversations: 5
   Deleted messages: 8
   Deleted documents: 0
   Deleted document chunks: 0
```

## Notes

- The script automatically handles foreign key relationships
- Deletion order: chunks → documents → messages → conversations
- All operations are wrapped in a database transaction
- The script is safe to run multiple times (idempotent)
