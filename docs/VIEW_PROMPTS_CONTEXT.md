# VIEW_PROMPTS_CONTEXT Feature Implementation Plan

## Overview
This feature will add the ability for users to view the finalized prompts sent to AI models and the context awareness data used for each question in the chat interface. This will provide transparency into how the AI processes user queries and what context information is being utilized.

## Feature Requirements

### 1. User Interface Components
- **View Prompt Button**: Toggle button under each user question to view the final prompt sent to the AI model
- **View Context Button**: Toggle button under each user question to view context awareness data (if available)
- **Tabbed Interface**: Both buttons will be placed side-by-side below user questions as tabs
- **Expandable Sections**: Clicking buttons will expand/collapse relevant information sections

### 2. Data Storage Requirements
- Store each user question with associated metadata
- Store the final prompt that was sent to the AI model
- Store context awareness data used for the question
- Link all data to user ID, conversation ID, and question ID
- Maintain referential integrity with existing database structure

### 3. Data Retrieval
- API endpoints to fetch prompt data for specific questions
- API endpoints to fetch context awareness data for specific questions
- Efficient querying with proper indexing

## Current Architecture Analysis

### Frontend (NextJS)
- **ChatInterface.tsx**: Main chat component with message handling
- **MessageList.tsx**: Renders list of messages with auto-scroll
- **MessageItem.tsx**: Individual message component with role-based rendering
- **useChat.ts**: Hook for chat functionality and SSE streaming
- **API Integration**: Uses `/api/chat/stream` for real-time communication

### Backend (FastAPI)
- **Chat Service**: Handles message processing and AI model communication
- **Context Awareness Service**: Manages context data and memory
- **Database Models**: User, Conversation, Message, ChatDocument tables
- **Repository Pattern**: Data access layer for database operations

### Current Database Schema
```sql
-- Users table
users (id, username, created_at, updated_at)

-- Conversations table  
conversations (id, title, model, user_id, is_active, created_at, updated_at)

-- Messages table
messages (id, conversation_id, role, content, tokens_used, model_used, created_at)

-- Chat Documents table
chat_documents (id, conversation_id, user_id, filename, file_type, file_size, file_path, upload_timestamp, summary_text, summary_type, processing_status, created_at, updated_at)
```

## Database Design

### New Tables Required

#### 1. User Questions Table
```sql
CREATE TABLE user_questions (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    conversation_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    question_text TEXT NOT NULL,
    question_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_questions_conversation (conversation_id),
    INDEX idx_user_questions_user (user_id),
    INDEX idx_user_questions_timestamp (question_timestamp)
);
```

#### 2. AI Prompts Table
```sql
CREATE TABLE ai_prompts (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    question_id VARCHAR(36) NOT NULL,
    conversation_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    final_prompt TEXT NOT NULL,
    model_used VARCHAR(50) NOT NULL,
    temperature DECIMAL(3,2),
    max_tokens INTEGER,
    prompt_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (question_id) REFERENCES user_questions(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_ai_prompts_question (question_id),
    INDEX idx_ai_prompts_conversation (conversation_id),
    INDEX idx_ai_prompts_user (user_id)
);
```

#### 3. Context Awareness Data Table
```sql
CREATE TABLE context_awareness_data (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    question_id VARCHAR(36) NOT NULL,
    conversation_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    context_type VARCHAR(50) NOT NULL, -- 'conversation_history', 'document_context', 'user_memory', 'rag_context'
    context_data JSON NOT NULL,
    context_metadata JSON,
    context_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (question_id) REFERENCES user_questions(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_context_question (question_id),
    INDEX idx_context_conversation (conversation_id),
    INDEX idx_context_user (user_id),
    INDEX idx_context_type (context_type)
);
```

## Backend Implementation Plan

### 1. Database Models (SQLAlchemy)

#### UserQuestion Model
```python
class UserQuestion(Base):
    __tablename__ = "user_questions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    conversation = relationship("Conversation")
    user = relationship("User")
    ai_prompts = relationship("AIPrompt", back_populates="question", cascade="all, delete-orphan")
    context_data = relationship("ContextAwarenessData", back_populates="question", cascade="all, delete-orphan")
```

#### AIPrompt Model
```python
class AIPrompt(Base):
    __tablename__ = "ai_prompts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("user_questions.id"), nullable=False)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    final_prompt = Column(Text, nullable=False)
    model_used = Column(String(50), nullable=False)
    temperature = Column(Float)
    max_tokens = Column(Integer)
    prompt_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    question = relationship("UserQuestion", back_populates="ai_prompts")
    conversation = relationship("Conversation")
    user = relationship("User")
```

#### ContextAwarenessData Model
```python
class ContextAwarenessData(Base):
    __tablename__ = "context_awareness_data"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("user_questions.id"), nullable=False)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    context_type = Column(String(50), nullable=False)
    context_data = Column(JSON, nullable=False)
    context_metadata = Column(JSON)
    context_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    question = relationship("UserQuestion", back_populates="context_data")
    conversation = relationship("Conversation")
    user = relationship("User")
```

### 2. Repository Layer

#### UserQuestionRepository
```python
class UserQuestionRepository:
    def create_question(self, question_data: UserQuestionCreate) -> UserQuestion
    def get_question(self, question_id: str) -> Optional[UserQuestion]
    def get_questions_by_conversation(self, conversation_id: str) -> List[UserQuestion]
    def get_questions_by_user(self, user_id: str) -> List[UserQuestion]
```

#### AIPromptRepository
```python
class AIPromptRepository:
    def create_prompt(self, prompt_data: AIPromptCreate) -> AIPrompt
    def get_prompt_by_question(self, question_id: str) -> Optional[AIPrompt]
    def get_prompts_by_conversation(self, conversation_id: str) -> List[AIPrompt]
```

#### ContextAwarenessRepository
```python
class ContextAwarenessRepository:
    def create_context_data(self, context_data: ContextAwarenessCreate) -> ContextAwarenessData
    def get_context_by_question(self, question_id: str) -> List[ContextAwarenessData]
    def get_context_by_type(self, question_id: str, context_type: str) -> Optional[ContextAwarenessData]
```

### 3. API Endpoints

#### New API Routes
```python
# Get prompt data for a specific question
@router.get("/questions/{question_id}/prompt")
async def get_question_prompt(question_id: str, db: Session = Depends(get_db))

# Get context data for a specific question  
@router.get("/questions/{question_id}/context")
async def get_question_context(question_id: str, db: Session = Depends(get_db))

# Get all data for a specific question
@router.get("/questions/{question_id}/details")
async def get_question_details(question_id: str, db: Session = Depends(get_db))
```

### 4. Service Layer Integration

#### ChatService Modifications
- Modify `generate_streaming_response` to store question and prompt data
- Integrate with UserQuestionRepository to create question records
- Store final prompts in AIPromptRepository
- Store context awareness data in ContextAwarenessRepository

#### ContextAwarenessService Integration
- Modify context gathering to store context data
- Create structured context data for storage
- Link context data to specific questions

## Frontend Implementation Plan

### 1. New Components

#### PromptViewer Component
```typescript
interface PromptViewerProps {
  questionId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function PromptViewer({ questionId, isOpen, onClose }: PromptViewerProps) {
  // Component to display the final prompt sent to AI
}
```

#### ContextViewer Component
```typescript
interface ContextViewerProps {
  questionId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function ContextViewer({ questionId, isOpen, onClose }: ContextViewerProps) {
  // Component to display context awareness data
}
```

#### QuestionDetails Component
```typescript
interface QuestionDetailsProps {
  questionId: string;
  questionText: string;
}

export default function QuestionDetails({ questionId, questionText }: QuestionDetailsProps) {
  // Component containing both prompt and context viewers as tabs
}
```

### 2. MessageItem Component Modifications

#### Enhanced MessageItem
- Add question ID tracking for user messages
- Add toggle buttons for prompt and context viewing
- Integrate QuestionDetails component
- Handle expand/collapse functionality

### 3. API Integration

#### New API Functions
```typescript
// lib/api.ts additions
export async function getQuestionPrompt(questionId: string): Promise<AIPrompt>
export async function getQuestionContext(questionId: string): Promise<ContextAwarenessData[]>
export async function getQuestionDetails(questionId: string): Promise<QuestionDetails>
```

#### New Types
```typescript
// lib/types.ts additions
interface UserQuestion {
  id: string;
  conversation_id: string;
  user_id: string;
  question_text: string;
  question_timestamp: string;
  created_at: string;
  updated_at: string;
}

interface AIPrompt {
  id: string;
  question_id: string;
  conversation_id: string;
  user_id: string;
  final_prompt: string;
  model_used: string;
  temperature?: number;
  max_tokens?: number;
  prompt_timestamp: string;
  created_at: string;
}

interface ContextAwarenessData {
  id: string;
  question_id: string;
  conversation_id: string;
  user_id: string;
  context_type: string;
  context_data: any;
  context_metadata?: any;
  context_timestamp: string;
  created_at: string;
}

interface QuestionDetails {
  question: UserQuestion;
  prompt?: AIPrompt;
  context_data: ContextAwarenessData[];
}
```

### 4. Styling and UX

#### CSS Modules
- Create styles for toggle buttons
- Design expandable sections
- Implement tabbed interface styling
- Add loading states and error handling

#### User Experience
- Smooth animations for expand/collapse
- Clear visual indicators for available data
- Responsive design for mobile devices
- Accessibility considerations (ARIA labels, keyboard navigation)

## Implementation Phases

### Phase 1: Database Setup
1. Create database migration files
2. Implement new SQLAlchemy models
3. Create repository classes
4. Add database indexes for performance

### Phase 2: Backend API
1. Implement new API endpoints
2. Integrate with existing ChatService
3. Modify context awareness service
4. Add data validation and error handling

### Phase 3: Frontend Components
1. Create new React components
2. Implement API integration
3. Add styling and animations
4. Integrate with existing MessageItem component

### Phase 4: Testing and Optimization
1. Unit tests for new components
2. Integration tests for API endpoints
3. Performance testing and optimization
4. User acceptance testing

## Technical Considerations

### Performance
- Database indexing for efficient queries
- Lazy loading of prompt and context data
- Caching strategies for frequently accessed data
- Pagination for large datasets

### Security
- User authorization for data access
- Input validation and sanitization
- Rate limiting for API endpoints
- Data privacy considerations

### Scalability
- Database partitioning strategies
- API response optimization
- Frontend state management
- Error handling and recovery

## Future Enhancements

### Potential Features
- Export prompt and context data
- Search functionality across prompts
- Analytics on prompt effectiveness
- A/B testing for different prompt strategies
- Integration with external prompt management tools

### Monitoring and Analytics
- Track usage of prompt viewing feature
- Monitor API performance
- User engagement metrics
- Error tracking and alerting

## Conclusion

This feature will significantly enhance the transparency and debuggability of the AI assistant by allowing users to inspect the exact prompts sent to AI models and the context data used for each question. The implementation follows the existing architecture patterns and maintains data integrity while providing a smooth user experience.

The phased approach ensures minimal disruption to existing functionality while gradually introducing the new capabilities. The design is extensible and can accommodate future enhancements as the system evolves.
