from sqlalchemy import Column, String, Boolean, Float, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(String(255), primary_key=True, index=True)
    enable_context_awareness = Column(Boolean, default=True)
    include_memory = Column(Boolean, default=False)
    context_strategy = Column(String(50), default="conversation_only")
    selected_model = Column(String(100), default="deepseek-r1:8b")
    use_streaming = Column(Boolean, default=True)
    use_rag = Column(Boolean, default=False)
    use_advanced_rag = Column(Boolean, default=False)
    use_phase2_reasoning = Column(Boolean, default=False)
    use_reasoning_chat = Column(Boolean, default=False)
    use_phase3_reasoning = Column(Boolean, default=False)
    selected_phase2_engine = Column(String(50), default="auto")
    selected_phase3_strategy = Column(String(50), default="auto")
    use_unified_reasoning = Column(Boolean, default=False)
    selected_reasoning_mode = Column(String(50), default="auto")
    temperature = Column(Float, default=0.7)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "user_id": self.user_id,
            "enable_context_awareness": self.enable_context_awareness,
            "include_memory": self.include_memory,
            "context_strategy": self.context_strategy,
            "selected_model": self.selected_model,
            "use_streaming": self.use_streaming,
            "use_rag": self.use_rag,
            "use_advanced_rag": self.use_advanced_rag,
            "use_phase2_reasoning": self.use_phase2_reasoning,
            "use_reasoning_chat": self.use_reasoning_chat,
            "use_phase3_reasoning": self.use_phase3_reasoning,
            "selected_phase2_engine": self.selected_phase2_engine,
            "selected_phase3_strategy": self.selected_phase3_strategy,
            "use_unified_reasoning": self.use_unified_reasoning,
            "selected_reasoning_mode": self.selected_reasoning_mode,
            "temperature": self.temperature,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
