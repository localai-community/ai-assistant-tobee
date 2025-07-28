"""
Output formatting utilities for the reasoning system.

This module provides comprehensive formatting capabilities for reasoning results
with support for multiple output formats and flexible format definitions.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

from ..core.base import ReasoningStep, ReasoningResult, ReasoningType, StepStatus, ValidationResult


def format_reasoning_output(result: ReasoningResult, format_type: str = "text") -> str:
    """
    Format a reasoning result using the specified format.
    
    Args:
        result: The reasoning result to format
        format_type: The desired output format ("text", "json", "markdown", "html")
        
    Returns:
        Formatted string representation
    """
    if format_type == "json":
        formatter = JSONFormatter()
    elif format_type == "markdown":
        formatter = MarkdownFormatter()
    elif format_type == "html":
        formatter = HTMLFormatter()
    else:  # Default to text
        formatter = TextFormatter()
    
    return formatter.format(result)


class OutputFormat(Enum):
    """Supported output formats."""
    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"
    MARKDOWN = "markdown"
    HTML = "html"
    XML = "xml"


@dataclass
class FormatConfig:
    """Configuration for output formatting."""
    include_metadata: bool = True
    include_validation: bool = True
    include_timestamps: bool = True
    pretty_print: bool = True
    max_step_length: Optional[int] = None
    include_confidence: bool = True
    include_reasoning: bool = True
    custom_fields: Dict[str, Any] = field(default_factory=dict)


class BaseFormatter(ABC):
    """Abstract base class for formatters."""

    def __init__(self, format_type: OutputFormat):
        self.format_type = format_type
        self.config = FormatConfig()

    @abstractmethod
    def format(self, result: ReasoningResult) -> str:
        """
        Format a reasoning result.
        
        Args:
            result: The reasoning result to format
            
        Returns:
            Formatted string representation
        """
        pass

    def set_config(self, config: FormatConfig) -> None:
        """Set formatting configuration."""
        self.config = config

    def get_config(self) -> FormatConfig:
        """Get current configuration."""
        return self.config


class JSONFormatter(BaseFormatter):
    """JSON formatter for reasoning results."""

    def __init__(self):
        super().__init__(OutputFormat.JSON)

    def format(self, result: ReasoningResult) -> str:
        """Format reasoning result as JSON."""
        output_data = self._build_output_dict(result)
        
        if self.config.pretty_print:
            return json.dumps(output_data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(output_data, ensure_ascii=False)

    def _build_output_dict(self, result: ReasoningResult) -> Dict[str, Any]:
        """Build the output dictionary."""
        output = {
            "id": result.id,
            "problem_statement": result.problem_statement,
            "reasoning_type": result.reasoning_type.value,
            "final_answer": result.final_answer,
            "confidence": result.confidence,
            "steps": []
        }

        # Add steps
        for step in result.steps:
            step_data = {
                "step_number": step.step_number,
                "description": step.description,
                "status": step.status.value,
                "confidence": step.confidence
            }

            if self.config.include_reasoning:
                step_data["reasoning"] = step.reasoning

            if step.input_data:
                step_data["input_data"] = step.input_data

            if step.output_data:
                step_data["output_data"] = step.output_data

            if self.config.include_validation and step.validation_results:
                step_data["validation"] = [
                    {
                        "is_valid": vr.is_valid,
                        "level": vr.level.value,
                        "message": vr.message,
                        "details": vr.details
                    }
                    for vr in step.validation_results
                ]

            if self.config.include_timestamps:
                step_data["created_at"] = step.created_at.isoformat()
                if step.completed_at:
                    step_data["completed_at"] = step.completed_at.isoformat()

            output["steps"].append(step_data)

        # Add validation results
        if self.config.include_validation and result.validation_results:
            output["validation"] = [
                {
                    "is_valid": vr.is_valid,
                    "level": vr.level.value,
                    "message": vr.message,
                    "details": vr.details
                }
                for vr in result.validation_results
            ]

        # Add metadata
        if self.config.include_metadata:
            output["metadata"] = result.metadata

        # Add timestamps
        if self.config.include_timestamps:
            output["created_at"] = result.created_at.isoformat()
            if result.completed_at:
                output["completed_at"] = result.completed_at.isoformat()
            if result.execution_time:
                output["execution_time"] = result.execution_time

        # Add custom fields
        output.update(self.config.custom_fields)

        return output


class TextFormatter(BaseFormatter):
    """Text formatter for reasoning results."""

    def __init__(self):
        super().__init__(OutputFormat.TEXT)

    def format(self, result: ReasoningResult) -> str:
        """Format reasoning result as plain text."""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("REASONING RESULT")
        lines.append("=" * 60)
        lines.append(f"Problem: {result.problem_statement}")
        lines.append(f"Type: {result.reasoning_type.value}")
        lines.append(f"Confidence: {result.confidence:.3f}")
        lines.append("")

        # Steps
        lines.append("REASONING STEPS:")
        lines.append("-" * 40)
        
        for step in result.steps:
            lines.append(f"Step {step.step_number}: {step.description}")
            lines.append(f"Status: {step.status.value}")
            
            if self.config.include_confidence:
                lines.append(f"Confidence: {step.confidence:.3f}")
            
            if self.config.include_reasoning and step.reasoning:
                reasoning_text = step.reasoning
                if self.config.max_step_length:
                    reasoning_text = self._truncate_text(reasoning_text, self.config.max_step_length)
                lines.append(f"Reasoning: {reasoning_text}")
            
            if self.config.include_validation and step.validation_results:
                failed_validations = [vr for vr in step.validation_results if not vr.is_valid]
                if failed_validations:
                    lines.append("Validation Issues:")
                    for vr in failed_validations:
                        lines.append(f"  - {vr.level.value.upper()}: {vr.message}")
            
            lines.append("")

        # Final answer
        if result.final_answer is not None:
            lines.append("FINAL ANSWER:")
            lines.append("-" * 40)
            lines.append(str(result.final_answer))
            lines.append("")

        # Overall validation
        if self.config.include_validation and result.validation_results:
            lines.append("OVERALL VALIDATION:")
            lines.append("-" * 40)
            failed_validations = [vr for vr in result.validation_results if not vr.is_valid]
            if failed_validations:
                for vr in failed_validations:
                    lines.append(f"- {vr.level.value.upper()}: {vr.message}")
            else:
                lines.append("All validations passed")
            lines.append("")

        # Metadata
        if self.config.include_metadata and result.metadata:
            lines.append("METADATA:")
            lines.append("-" * 40)
            for key, value in result.metadata.items():
                lines.append(f"{key}: {value}")
            lines.append("")

        # Timestamps
        if self.config.include_timestamps:
            lines.append("TIMESTAMPS:")
            lines.append("-" * 40)
            lines.append(f"Created: {result.created_at}")
            if result.completed_at:
                lines.append(f"Completed: {result.completed_at}")
            if result.execution_time:
                lines.append(f"Execution time: {result.execution_time:.3f}s")
            lines.append("")

        lines.append("=" * 60)
        
        return "\n".join(lines)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."


class MarkdownFormatter(BaseFormatter):
    """Markdown formatter for reasoning results."""

    def __init__(self):
        super().__init__(OutputFormat.MARKDOWN)

    def format(self, result: ReasoningResult) -> str:
        """Format reasoning result as Markdown."""
        lines = []
        
        # Header
        lines.append("# Reasoning Result")
        lines.append("")
        lines.append(f"**Problem:** {result.problem_statement}")
        lines.append(f"**Type:** {result.reasoning_type.value}")
        lines.append(f"**Confidence:** {result.confidence:.3f}")
        lines.append("")

        # Steps
        lines.append("## Reasoning Steps")
        lines.append("")
        
        for step in result.steps:
            lines.append(f"### Step {step.step_number}: {step.description}")
            lines.append("")
            lines.append(f"- **Status:** {step.status.value}")
            
            if self.config.include_confidence:
                lines.append(f"- **Confidence:** {step.confidence:.3f}")
            
            if self.config.include_reasoning and step.reasoning:
                reasoning_text = step.reasoning
                if self.config.max_step_length:
                    reasoning_text = self._truncate_text(reasoning_text, self.config.max_step_length)
                lines.append(f"- **Reasoning:** {reasoning_text}")
            
            if self.config.include_validation and step.validation_results:
                failed_validations = [vr for vr in step.validation_results if not vr.is_valid]
                if failed_validations:
                    lines.append("- **Validation Issues:**")
                    for vr in failed_validations:
                        lines.append(f"  - {vr.level.value.upper()}: {vr.message}")
            
            lines.append("")

        # Final answer
        if result.final_answer is not None:
            lines.append("## Final Answer")
            lines.append("")
            lines.append(f"```")
            lines.append(str(result.final_answer))
            lines.append("```")
            lines.append("")

        # Overall validation
        if self.config.include_validation and result.validation_results:
            lines.append("## Overall Validation")
            lines.append("")
            failed_validations = [vr for vr in result.validation_results if not vr.is_valid]
            if failed_validations:
                for vr in failed_validations:
                    lines.append(f"- **{vr.level.value.upper()}:** {vr.message}")
            else:
                lines.append("✅ All validations passed")
            lines.append("")

        # Metadata
        if self.config.include_metadata and result.metadata:
            lines.append("## Metadata")
            lines.append("")
            for key, value in result.metadata.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        # Timestamps
        if self.config.include_timestamps:
            lines.append("## Timestamps")
            lines.append("")
            lines.append(f"- **Created:** {result.created_at}")
            if result.completed_at:
                lines.append(f"- **Completed:** {result.completed_at}")
            if result.execution_time:
                lines.append(f"- **Execution time:** {result.execution_time:.3f}s")
            lines.append("")

        return "\n".join(lines)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."


class HTMLFormatter(BaseFormatter):
    """HTML formatter for reasoning results."""

    def __init__(self):
        super().__init__(OutputFormat.HTML)

    def format(self, result: ReasoningResult) -> str:
        """Format reasoning result as HTML."""
        html_parts = []
        
        # Start HTML
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html>")
        html_parts.append("<head>")
        html_parts.append("<title>Reasoning Result</title>")
        html_parts.append("<style>")
        html_parts.append(self._get_css_styles())
        html_parts.append("</style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        # Header
        html_parts.append("<div class='header'>")
        html_parts.append("<h1>Reasoning Result</h1>")
        html_parts.append(f"<p><strong>Problem:</strong> {result.problem_statement}</p>")
        html_parts.append(f"<p><strong>Type:</strong> {result.reasoning_type.value}</p>")
        html_parts.append(f"<p><strong>Confidence:</strong> {result.confidence:.3f}</p>")
        html_parts.append("</div>")
        
        # Steps
        html_parts.append("<div class='section'>")
        html_parts.append("<h2>Reasoning Steps</h2>")
        
        for step in result.steps:
            html_parts.append("<div class='step'>")
            html_parts.append(f"<h3>Step {step.step_number}: {step.description}</h3>")
            html_parts.append(f"<p><strong>Status:</strong> {step.status.value}</p>")
            
            if self.config.include_confidence:
                html_parts.append(f"<p><strong>Confidence:</strong> {step.confidence:.3f}</p>")
            
            if self.config.include_reasoning and step.reasoning:
                reasoning_text = step.reasoning
                if self.config.max_step_length:
                    reasoning_text = self._truncate_text(reasoning_text, self.config.max_step_length)
                html_parts.append(f"<p><strong>Reasoning:</strong> {reasoning_text}</p>")
            
            if self.config.include_validation and step.validation_results:
                failed_validations = [vr for vr in step.validation_results if not vr.is_valid]
                if failed_validations:
                    html_parts.append("<p><strong>Validation Issues:</strong></p>")
                    html_parts.append("<ul>")
                    for vr in failed_validations:
                        html_parts.append(f"<li class='{vr.level.value}'>{vr.level.value.upper()}: {vr.message}</li>")
                    html_parts.append("</ul>")
            
            html_parts.append("</div>")
        
        html_parts.append("</div>")
        
        # Final answer
        if result.final_answer is not None:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>Final Answer</h2>")
            html_parts.append(f"<pre>{str(result.final_answer)}</pre>")
            html_parts.append("</div>")
        
        # Overall validation
        if self.config.include_validation and result.validation_results:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>Overall Validation</h2>")
            failed_validations = [vr for vr in result.validation_results if not vr.is_valid]
            if failed_validations:
                html_parts.append("<ul>")
                for vr in failed_validations:
                    html_parts.append(f"<li class='{vr.level.value}'><strong>{vr.level.value.upper()}:</strong> {vr.message}</li>")
                html_parts.append("</ul>")
            else:
                html_parts.append("<p class='success'>✅ All validations passed</p>")
            html_parts.append("</div>")
        
        # Metadata
        if self.config.include_metadata and result.metadata:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>Metadata</h2>")
            html_parts.append("<ul>")
            for key, value in result.metadata.items():
                html_parts.append(f"<li><strong>{key}:</strong> {value}</li>")
            html_parts.append("</ul>")
            html_parts.append("</div>")
        
        # Timestamps
        if self.config.include_timestamps:
            html_parts.append("<div class='section'>")
            html_parts.append("<h2>Timestamps</h2>")
            html_parts.append("<ul>")
            html_parts.append(f"<li><strong>Created:</strong> {result.created_at}</li>")
            if result.completed_at:
                html_parts.append(f"<li><strong>Completed:</strong> {result.completed_at}</li>")
            if result.execution_time:
                html_parts.append(f"<li><strong>Execution time:</strong> {result.execution_time:.3f}s</li>")
            html_parts.append("</ul>")
            html_parts.append("</div>")
        
        # End HTML
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)

    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML formatting."""
        return """
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .step { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .error { color: #d32f2f; }
        .warning { color: #f57c00; }
        .info { color: #1976d2; }
        .success { color: #388e3c; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 3px; }
        """

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."


class StructuredFormatter(BaseFormatter):
    """Structured formatter for programmatic access."""

    def __init__(self):
        super().__init__(OutputFormat.STRUCTURED)

    def format(self, result: ReasoningResult) -> Dict[str, Any]:
        """Format reasoning result as structured data."""
        structured_data = {
            "summary": {
                "id": result.id,
                "problem_statement": result.problem_statement,
                "reasoning_type": result.reasoning_type.value,
                "final_answer": result.final_answer,
                "confidence": result.confidence,
                "total_steps": len(result.steps),
                "completed_steps": len([s for s in result.steps if s.status == StepStatus.COMPLETED])
            },
            "steps": []
        }

        # Add steps
        for step in result.steps:
            step_data = {
                "step_number": step.step_number,
                "description": step.description,
                "status": step.status.value,
                "confidence": step.confidence
            }

            if self.config.include_reasoning:
                step_data["reasoning"] = step.reasoning

            if step.input_data:
                step_data["input_data"] = step.input_data

            if step.output_data:
                step_data["output_data"] = step.output_data

            if self.config.include_validation and step.validation_results:
                step_data["validation"] = [
                    {
                        "is_valid": vr.is_valid,
                        "level": vr.level.value,
                        "message": vr.message,
                        "details": vr.details
                    }
                    for vr in step.validation_results
                ]

            if self.config.include_timestamps:
                step_data["created_at"] = step.created_at.isoformat()
                if step.completed_at:
                    step_data["completed_at"] = step.completed_at.isoformat()

            structured_data["steps"].append(step_data)

        # Add validation summary
        if self.config.include_validation and result.validation_results:
            structured_data["validation"] = {
                "total": len(result.validation_results),
                "passed": len([vr for vr in result.validation_results if vr.is_valid]),
                "failed": len([vr for vr in result.validation_results if not vr.is_valid]),
                "by_level": {}
            }
            
            for level in ["info", "warning", "error", "critical"]:
                structured_data["validation"]["by_level"][level] = len([
                    vr for vr in result.validation_results if vr.level.value == level
                ])

        # Add metadata
        if self.config.include_metadata:
            structured_data["metadata"] = result.metadata

        # Add timestamps
        if self.config.include_timestamps:
            structured_data["timestamps"] = {
                "created_at": result.created_at.isoformat(),
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                "execution_time": result.execution_time
            }

        # Add custom fields
        structured_data.update(self.config.custom_fields)

        return structured_data


class FormatterFactory:
    """Factory for creating formatters."""

    _formatters = {
        OutputFormat.JSON: JSONFormatter,
        OutputFormat.TEXT: TextFormatter,
        OutputFormat.MARKDOWN: MarkdownFormatter,
        OutputFormat.HTML: HTMLFormatter,
        OutputFormat.STRUCTURED: StructuredFormatter
    }

    @classmethod
    def create_formatter(cls, format_type: OutputFormat) -> Optional[BaseFormatter]:
        """Create a formatter of the specified type."""
        formatter_class = cls._formatters.get(format_type)
        if formatter_class:
            return formatter_class()
        return None

    @classmethod
    def get_available_formats(cls) -> List[OutputFormat]:
        """Get list of available format types."""
        return list(cls._formatters.keys())

    @classmethod
    def register_formatter(cls, format_type: OutputFormat, formatter_class: type) -> None:
        """Register a new formatter type."""
        cls._formatters[format_type] = formatter_class


class FormatConverter:
    """Utility for converting between different output formats."""

    def __init__(self):
        self.factory = FormatterFactory()

    def convert(self, result: ReasoningResult, from_format: OutputFormat, 
                to_format: OutputFormat, config: Optional[FormatConfig] = None) -> Union[str, Dict[str, Any]]:
        """Convert a result from one format to another."""
        # For structured format, we can convert directly
        if from_format == OutputFormat.STRUCTURED and to_format == OutputFormat.STRUCTURED:
            formatter = self.factory.create_formatter(to_format)
            if config:
                formatter.set_config(config)
            return formatter.format(result)

        # For other formats, we need to go through structured format
        structured_formatter = self.factory.create_formatter(OutputFormat.STRUCTURED)
        if config:
            structured_formatter.set_config(config)
        
        structured_data = structured_formatter.format(result)
        
        # Now convert to target format
        target_formatter = self.factory.create_formatter(to_format)
        if config:
            target_formatter.set_config(config)
        
        # For structured output, return the data directly
        if to_format == OutputFormat.STRUCTURED:
            return structured_data
        
        # For other formats, we need to reconstruct the result and format it
        # This is a simplified approach - in practice, you might want more sophisticated conversion
        return target_formatter.format(result) 