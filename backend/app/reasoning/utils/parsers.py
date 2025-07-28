"""
Parsing utilities for the reasoning system.

This module provides flexible parsing capabilities for problem statements,
step-by-step outputs, and input sanitization with comprehensive error handling.
"""

import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
import logging

from ..core.base import ReasoningStep, ReasoningResult, ReasoningType, StepStatus

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """Result of a parsing operation."""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


def parse_problem_statement(problem_statement: str) -> Dict[str, Any]:
    """
    Parse a problem statement to extract type and content.
    
    Args:
        problem_statement: The problem statement to parse
        
    Returns:
        Dictionary containing parsed information
    """
    if not problem_statement or not problem_statement.strip():
        return {
            "type": "general",
            "content": "",
            "length": 0,
            "word_count": 0
        }
    
    # Clean the input
    cleaned_statement = problem_statement.strip()
    
    # Detect problem type
    problem_type = "general"
    input_lower = cleaned_statement.lower()
    
    # Mathematical problem detection
    math_patterns = [
        r'\b(solve|calculate|compute|find|evaluate)\b',
        r'[\+\-\*/=\^√∫∑∏∞≤≥≠≈]',
        r'\b(equation|formula|function|derivative|integral)\b',
        r'\b(number|sum|product|average|mean|median)\b',
        r'\b(what is|how much|calculate)\b'
    ]
    
    for pattern in math_patterns:
        if re.search(pattern, input_lower):
            problem_type = "mathematical"
            break
    
    # Logical problem detection
    if problem_type == "general":
        logic_patterns = [
            r'\b(logic|logical|deduce|infer|conclude)\b',
            r'\b(if|then|else|and|or|not)\b',
            r'\b(premise|conclusion|argument|valid|invalid)\b',
            r'\b(truth|false|true|boolean)\b'
        ]
        
        for pattern in logic_patterns:
            if re.search(pattern, input_lower):
                problem_type = "logical"
                break
    
    # Causal problem detection
    if problem_type == "general":
        causal_patterns = [
            r'\b(cause|effect|because|therefore|since)\b',
            r'\b(leads to|results in|due to|as a result)\b',
            r'\b(correlation|causation|relationship)\b',
            r'\b(why|how|what causes)\b'
        ]
        
        for pattern in causal_patterns:
            if re.search(pattern, input_lower):
                problem_type = "causal"
                break
    
    return {
        "type": problem_type,
        "content": cleaned_statement,
        "length": len(cleaned_statement),
        "word_count": len(cleaned_statement.split())
    }


class BaseParser(ABC):
    """Abstract base class for parsers."""

    def __init__(self, name: str):
        self.name = name
        self.config: Dict[str, Any] = {}

    @abstractmethod
    def parse(self, input_data: str) -> ParseResult:
        """
        Parse the input data.
        
        Args:
            input_data: The data to parse
            
        Returns:
            ParseResult containing the parsed data or error information
        """
        pass

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self.config.copy()

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set the configuration."""
        self.config.update(config)


class ProblemStatementParser(BaseParser):
    """Parser for problem statements."""

    def __init__(self):
        super().__init__("problem_statement")
        self.setup_default_config()

    def setup_default_config(self):
        """Set up default configuration."""
        self.config = {
            "max_length": 10000,
            "min_length": 1,
            "allowed_chars": None,  # None means all characters allowed
            "strip_whitespace": True,
            "normalize_whitespace": True,
            "remove_control_chars": True
        }

    def parse(self, input_data: str) -> ParseResult:
        """Parse a problem statement."""
        if not isinstance(input_data, str):
            return ParseResult(
                success=False,
                error_message="Input must be a string"
            )

        original_input = input_data
        warnings = []

        # Apply preprocessing
        processed_input = self._preprocess_input(input_data)
        
        # Validate length
        if len(processed_input) < self.config["min_length"]:
            return ParseResult(
                success=False,
                error_message=f"Problem statement too short (minimum {self.config['min_length']} characters)"
            )
        
        if len(processed_input) > self.config["max_length"]:
            return ParseResult(
                success=False,
                error_message=f"Problem statement too long (maximum {self.config['max_length']} characters)"
            )

        # Detect problem type
        problem_type = self._detect_problem_type(processed_input)
        
        # Extract key information
        extracted_info = self._extract_information(processed_input)

        result_data = {
            "original_input": original_input,
            "processed_input": processed_input,
            "problem_type": problem_type,
            "extracted_info": extracted_info,
            "length": len(processed_input),
            "word_count": len(processed_input.split())
        }

        return ParseResult(
            success=True,
            data=result_data,
            warnings=warnings,
            metadata={
                "parser": self.name,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    def _preprocess_input(self, input_data: str) -> str:
        """Preprocess the input data."""
        processed = input_data

        if self.config["strip_whitespace"]:
            processed = processed.strip()

        if self.config["normalize_whitespace"]:
            processed = re.sub(r'\s+', ' ', processed)

        if self.config["remove_control_chars"]:
            processed = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', processed)

        return processed

    def _detect_problem_type(self, input_data: str) -> str:
        """Detect the type of problem."""
        input_lower = input_data.lower()
        
        # Mathematical problem detection
        math_patterns = [
            r'\b(solve|calculate|compute|find|evaluate)\b',
            r'[\+\-\*/=\^√∫∑∏∞≤≥≠≈]',
            r'\b(equation|formula|function|derivative|integral)\b',
            r'\b(number|sum|product|average|mean|median)\b'
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, input_lower):
                return "mathematical"

        # Logical problem detection
        logic_patterns = [
            r'\b(logic|logical|deduce|infer|conclude)\b',
            r'\b(if|then|else|and|or|not)\b',
            r'\b(premise|conclusion|argument|valid|invalid)\b',
            r'\b(truth|false|true|boolean)\b'
        ]
        
        for pattern in logic_patterns:
            if re.search(pattern, input_lower):
                return "logical"

        # Causal problem detection
        causal_patterns = [
            r'\b(cause|effect|because|therefore|since)\b',
            r'\b(leads to|results in|due to|as a result)\b',
            r'\b(correlation|causation|relationship)\b',
            r'\b(why|how|what causes)\b'
        ]
        
        for pattern in causal_patterns:
            if re.search(pattern, input_lower):
                return "causal"

        return "general"

    def _extract_information(self, input_data: str) -> Dict[str, Any]:
        """Extract key information from the problem statement."""
        extracted = {
            "numbers": [],
            "variables": [],
            "units": [],
            "keywords": []
        }

        # Extract numbers
        numbers = re.findall(r'-?\d+\.?\d*', input_data)
        extracted["numbers"] = [float(num) for num in numbers]

        # Extract variables (single letters that might be variables)
        variables = re.findall(r'\b[a-zA-Z]\b', input_data)
        extracted["variables"] = list(set(variables))

        # Extract units
        units = re.findall(r'\b(kg|m|s|km|cm|mm|g|mg|L|mL|°C|°F|K|Pa|N|J|W|V|A|Ω|Hz|rad|deg)\b', input_data)
        extracted["units"] = list(set(units))

        # Extract keywords
        keywords = re.findall(r'\b\w{4,}\b', input_data.lower())
        extracted["keywords"] = list(set(keywords))

        return extracted


class StepOutputParser(BaseParser):
    """Parser for step-by-step reasoning outputs."""

    def __init__(self):
        super().__init__("step_output")
        self.setup_default_config()

    def setup_default_config(self):
        """Set up default configuration."""
        self.config = {
            "step_patterns": [
                r'^Step\s+(\d+):\s*(.+)$',
                r'^(\d+)\.\s*(.+)$',
                r'^Step\s+(\d+)\s*[-:]\s*(.+)$'
            ],
            "confidence_patterns": [
                r'confidence:\s*([0-9]*\.?[0-9]+)',
                r'confidence\s*=\s*([0-9]*\.?[0-9]+)',
                r'\(([0-9]*\.?[0-9]+)\s*confidence\)'
            ],
            "extract_reasoning": True,
            "extract_confidence": True,
            "normalize_step_numbers": True
        }

    def parse(self, input_data: str) -> ParseResult:
        """Parse step-by-step reasoning output."""
        if not isinstance(input_data, str):
            return ParseResult(
                success=False,
                error_message="Input must be a string"
            )

        lines = input_data.strip().split('\n')
        steps = []
        warnings = []
        current_step = None

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Try to match step patterns
            step_match = self._match_step_pattern(line)
            if step_match:
                # Save previous step if exists
                if current_step:
                    steps.append(current_step)

                # Create new step
                step_number, description = step_match
                current_step = {
                    "step_number": int(step_number),
                    "description": description,
                    "reasoning": "",
                    "confidence": 0.0,
                    "line_number": line_num
                }
            elif current_step:
                # This line is part of the current step
                if self.config["extract_confidence"]:
                    confidence_match = self._extract_confidence(line)
                    if confidence_match:
                        current_step["confidence"] = confidence_match

                if self.config["extract_reasoning"]:
                    current_step["reasoning"] += line + " "

        # Add the last step
        if current_step:
            steps.append(current_step)

        if not steps:
            return ParseResult(
                success=False,
                error_message="No steps found in the output"
            )

        # Normalize step numbers if requested
        if self.config["normalize_step_numbers"]:
            for i, step in enumerate(steps, 1):
                step["step_number"] = i

        # Clean up reasoning text
        for step in steps:
            step["reasoning"] = step["reasoning"].strip()

        return ParseResult(
            success=True,
            data=steps,
            warnings=warnings,
            metadata={
                "parser": self.name,
                "total_steps": len(steps),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    def _match_step_pattern(self, line: str) -> Optional[Tuple[str, str]]:
        """Match a line against step patterns."""
        for pattern in self.config["step_patterns"]:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.groups()
        return None

    def _extract_confidence(self, line: str) -> Optional[float]:
        """Extract confidence value from a line."""
        for pattern in self.config["confidence_patterns"]:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    confidence = float(match.group(1))
                    if 0.0 <= confidence <= 1.0:
                        return confidence
                except ValueError:
                    continue
        return None


class JSONParser(BaseParser):
    """Parser for JSON-formatted reasoning data."""

    def __init__(self):
        super().__init__("json")
        self.setup_default_config()

    def setup_default_config(self):
        """Set up default configuration."""
        self.config = {
            "strict": True,
            "allow_comments": False,
            "default_encoding": "utf-8"
        }

    def parse(self, input_data: str) -> ParseResult:
        """Parse JSON input data."""
        if not isinstance(input_data, str):
            return ParseResult(
                success=False,
                error_message="Input must be a string"
            )

        try:
            # Remove comments if allowed
            if self.config["allow_comments"]:
                input_data = self._remove_comments(input_data)

            # Parse JSON
            parsed_data = json.loads(input_data)
            
            return ParseResult(
                success=True,
                data=parsed_data,
                metadata={
                    "parser": self.name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error_message=f"JSON parsing error: {str(e)}"
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )

    def _remove_comments(self, json_str: str) -> str:
        """Remove comments from JSON string."""
        # Remove single-line comments
        json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
        
        # Remove multi-line comments
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str


class ParserFactory:
    """Factory for creating parsers."""

    _parsers = {
        "problem_statement": ProblemStatementParser,
        "step_output": StepOutputParser,
        "json": JSONParser
    }

    @classmethod
    def create_parser(cls, parser_type: str) -> Optional[BaseParser]:
        """Create a parser of the specified type."""
        parser_class = cls._parsers.get(parser_type)
        if parser_class:
            return parser_class()
        return None

    @classmethod
    def get_available_parsers(cls) -> List[str]:
        """Get list of available parser types."""
        return list(cls._parsers.keys())

    @classmethod
    def register_parser(cls, parser_type: str, parser_class: type) -> None:
        """Register a new parser type."""
        cls._parsers[parser_type] = parser_class


class InputSanitizer:
    """Utility for sanitizing and preprocessing input data."""

    def __init__(self):
        self.config = {
            "remove_html": True,
            "remove_script_tags": True,
            "normalize_unicode": True,
            "remove_control_chars": True,
            "max_length": 10000,
            "allowed_tags": ["p", "br", "strong", "em", "code"],
            "strip_whitespace": True
        }

    def sanitize(self, input_data: str) -> str:
        """Sanitize input data."""
        if not isinstance(input_data, str):
            raise ValueError("Input must be a string")

        sanitized = input_data

        # Remove HTML if configured
        if self.config["remove_html"]:
            sanitized = self._remove_html(sanitized)

        # Remove script tags
        if self.config["remove_script_tags"]:
            sanitized = self._remove_script_tags(sanitized)

        # Normalize Unicode
        if self.config["normalize_unicode"]:
            sanitized = self._normalize_unicode(sanitized)

        # Remove control characters
        if self.config["remove_control_chars"]:
            sanitized = self._remove_control_chars(sanitized)

        # Strip whitespace
        if self.config["strip_whitespace"]:
            sanitized = sanitized.strip()

        # Truncate if too long
        if len(sanitized) > self.config["max_length"]:
            sanitized = sanitized[:self.config["max_length"]]

        return sanitized

    def _remove_html(self, text: str) -> str:
        """Remove HTML tags while preserving allowed tags."""
        # Remove all HTML tags except allowed ones
        allowed_tags_pattern = '|'.join(self.config["allowed_tags"])
        pattern = rf'<(?!\/?(?:{allowed_tags_pattern})\b)[^>]+>'
        return re.sub(pattern, '', text)

    def _remove_script_tags(self, text: str) -> str:
        """Remove script tags and their content."""
        return re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)

    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters."""
        import unicodedata
        return unicodedata.normalize('NFKC', text)

    def _remove_control_chars(self, text: str) -> str:
        """Remove control characters."""
        return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    def set_config(self, config: Dict[str, Any]) -> None:
        """Set sanitization configuration."""
        self.config.update(config)

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy() 