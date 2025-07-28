"""
Result Synthesis for the Simplified Hybrid Multi-Agent System.

This module provides tools for synthesizing results from multiple agents,
combining local and A2A agent outputs into coherent final results.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from .base import AgentResult

logger = logging.getLogger(__name__)


class ResultSynthesizer:
    """
    Base class for synthesizing agent results.
    
    This class provides the foundation for combining results from
    multiple agents into coherent final results.
    """
    
    def __init__(self):
        self.synthesis_strategies = {
            "weighted_average": self._weighted_average_synthesis,
            "consensus": self._consensus_synthesis,
            "best_result": self._best_result_synthesis,
            "hybrid": self._hybrid_synthesis
        }
    
    async def synthesize_results(self, results: List[AgentResult], strategy: str = "hybrid") -> Dict[str, Any]:
        """
        Synthesize results from multiple agents.
        
        Args:
            results: List of agent results
            strategy: Synthesis strategy to use
            
        Returns:
            Synthesized result dictionary
        """
        if not results:
            return self._create_empty_result()
        
        if strategy not in self.synthesis_strategies:
            logger.warning(f"Unknown synthesis strategy: {strategy}, using hybrid")
            strategy = "hybrid"
        
        try:
            return await self.synthesis_strategies[strategy](results)
        except Exception as e:
            logger.error(f"Synthesis failed with strategy {strategy}: {e}")
            return self._create_error_result(str(e))
    
    async def _weighted_average_synthesis(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Synthesize results using weighted average based on confidence.
        
        Args:
            results: List of agent results
            
        Returns:
            Weighted average synthesis result
        """
        valid_results = [r for r in results if r.confidence > 0.0 and r.result is not None]
        
        if not valid_results:
            return self._create_empty_result()
        
        # Calculate weighted average confidence
        total_weight = sum(r.confidence for r in valid_results)
        weighted_confidence = sum(r.confidence * r.confidence for r in valid_results) / total_weight
        
        # Combine results based on confidence
        combined_result = self._combine_results_by_confidence(valid_results)
        
        return {
            "result": combined_result,
            "confidence": weighted_confidence,
            "strategy": "weighted_average",
            "agents_used": [r.agent_id for r in valid_results],
            "total_agents": len(valid_results),
            "metadata": {
                "synthesis_method": "weighted_average",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    async def _consensus_synthesis(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Synthesize results using consensus building.
        
        Args:
            results: List of agent results
            
        Returns:
            Consensus synthesis result
        """
        valid_results = [r for r in results if r.confidence > 0.0 and r.result is not None]
        
        if not valid_results:
            return self._create_empty_result()
        
        # Find consensus among results
        consensus_result = self._find_consensus(valid_results)
        
        # Calculate consensus confidence
        consensus_confidence = sum(r.confidence for r in valid_results) / len(valid_results)
        
        return {
            "result": consensus_result,
            "confidence": consensus_confidence,
            "strategy": "consensus",
            "agents_used": [r.agent_id for r in valid_results],
            "total_agents": len(valid_results),
            "metadata": {
                "synthesis_method": "consensus",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    async def _best_result_synthesis(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Synthesize results by selecting the best result.
        
        Args:
            results: List of agent results
            
        Returns:
            Best result synthesis
        """
        valid_results = [r for r in results if r.confidence > 0.0 and r.result is not None]
        
        if not valid_results:
            return self._create_empty_result()
        
        # Select the result with highest confidence
        best_result = max(valid_results, key=lambda r: r.confidence)
        
        return {
            "result": best_result.result,
            "confidence": best_result.confidence,
            "strategy": "best_result",
            "agents_used": [best_result.agent_id],
            "total_agents": len(valid_results),
            "metadata": {
                "synthesis_method": "best_result",
                "selected_agent": best_result.agent_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    async def _hybrid_synthesis(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Synthesize results using hybrid approach (local + A2A).
        
        Args:
            results: List of agent results
            
        Returns:
            Hybrid synthesis result
        """
        local_results = [r for r in results if r.metadata.get("agent_type") == "local"]
        a2a_results = [r for r in results if r.metadata.get("agent_type") == "a2a"]
        
        if not local_results and not a2a_results:
            return self._create_empty_result()
        
        # If we have both local and A2A results, use hybrid approach
        if local_results and a2a_results:
            return await self._combine_local_and_a2a(local_results, a2a_results)
        
        # If only local results, use best result
        if local_results:
            return await self._best_result_synthesis(local_results)
        
        # If only A2A results, use best result
        if a2a_results:
            return await self._best_result_synthesis(a2a_results)
    
    async def _combine_local_and_a2a(self, local_results: List[AgentResult], a2a_results: List[AgentResult]) -> Dict[str, Any]:
        """
        Combine local and A2A results intelligently.
        
        Args:
            local_results: Results from local agents
            a2a_results: Results from A2A agents
            
        Returns:
            Combined result
        """
        # Get best results from each type
        best_local = max(local_results, key=lambda r: r.confidence) if local_results else None
        best_a2a = max(a2a_results, key=lambda r: r.confidence) if a2a_results else None
        
        # Determine which result to use as primary
        if best_local and best_a2a:
            # Compare confidence and quality
            if best_a2a.confidence > best_local.confidence + 0.1:  # A2A significantly better
                primary_result = best_a2a
                secondary_result = best_local
                strategy = "a2a_enhanced"
            elif best_local.confidence > best_a2a.confidence + 0.1:  # Local significantly better
                primary_result = best_local
                secondary_result = best_a2a
                strategy = "local_enhanced"
            else:
                # Similar confidence, combine them
                combined_result = self._combine_two_results(best_local, best_a2a)
                return {
                    "result": combined_result,
                    "confidence": (best_local.confidence + best_a2a.confidence) / 2,
                    "strategy": "combined",
                    "agents_used": [best_local.agent_id, best_a2a.agent_id],
                    "total_agents": len(local_results) + len(a2a_results),
                    "metadata": {
                        "synthesis_method": "combined_local_a2a",
                        "local_confidence": best_local.confidence,
                        "a2a_confidence": best_a2a.confidence,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
        elif best_local:
            primary_result = best_local
            secondary_result = None
            strategy = "local_only"
        elif best_a2a:
            primary_result = best_a2a
            secondary_result = None
            strategy = "a2a_only"
        else:
            return self._create_empty_result()
        
        # Create enhanced result
        enhanced_result = self._enhance_with_secondary(primary_result, secondary_result)
        
        return {
            "result": enhanced_result,
            "confidence": primary_result.confidence,
            "strategy": strategy,
            "agents_used": [r.agent_id for r in local_results + a2a_results],
            "total_agents": len(local_results) + len(a2a_results),
            "metadata": {
                "synthesis_method": strategy,
                "primary_agent": primary_result.agent_id,
                "secondary_agent": secondary_result.agent_id if secondary_result else None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _combine_results_by_confidence(self, results: List[AgentResult]) -> str:
        """Combine multiple results based on confidence weights."""
        if not results:
            return ""
        
        # Sort by confidence (highest first)
        sorted_results = sorted(results, key=lambda r: r.confidence, reverse=True)
        
        # Take the highest confidence result as primary
        primary = sorted_results[0]
        
        # If we have multiple high-confidence results, combine them
        if len(sorted_results) > 1 and sorted_results[1].confidence > 0.8:
            secondary = sorted_results[1]
            return self._combine_two_results(primary, secondary)
        
        return str(primary.result)
    
    def _combine_two_results(self, result1: AgentResult, result2: AgentResult) -> str:
        """Combine two results intelligently."""
        r1_str = str(result1.result)
        r2_str = str(result2.result)
        
        # If results are similar, return the better one
        if self._are_results_similar(r1_str, r2_str):
            return r1_str if result1.confidence > result2.confidence else r2_str
        
        # If results are complementary, combine them
        if len(r1_str) > 100 and len(r2_str) > 100:
            return f"{r1_str}\n\nAdditional perspective: {r2_str}"
        
        # Otherwise, return the better result
        return r1_str if result1.confidence > result2.confidence else r2_str
    
    def _are_results_similar(self, result1: str, result2: str) -> bool:
        """Check if two results are similar."""
        # Simple similarity check - can be enhanced with more sophisticated algorithms
        r1_words = set(result1.lower().split())
        r2_words = set(result2.lower().split())
        
        if not r1_words or not r2_words:
            return False
        
        intersection = len(r1_words.intersection(r2_words))
        union = len(r1_words.union(r2_words))
        
        return intersection / union > 0.7  # 70% similarity threshold
    
    def _find_consensus(self, results: List[AgentResult]) -> str:
        """Find consensus among multiple results."""
        if not results:
            return ""
        
        # For now, return the highest confidence result
        # In a more sophisticated implementation, this would analyze content similarity
        best_result = max(results, key=lambda r: r.confidence)
        return str(best_result.result)
    
    def _enhance_with_secondary(self, primary: AgentResult, secondary: Optional[AgentResult]) -> str:
        """Enhance primary result with secondary result."""
        primary_str = str(primary.result)
        
        if not secondary:
            return primary_str
        
        secondary_str = str(secondary.result)
        
        # Add secondary result as additional insight
        return f"{primary_str}\n\nAdditional insight: {secondary_str}"
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create an empty result when no valid results are available."""
        return {
            "result": "No agents were able to process this problem.",
            "confidence": 0.0,
            "strategy": "empty",
            "agents_used": [],
            "total_agents": 0,
            "metadata": {
                "synthesis_method": "empty",
                "error": "No valid results available",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _create_error_result(self, error: str) -> Dict[str, Any]:
        """Create an error result when synthesis fails."""
        return {
            "result": f"Synthesis failed: {error}",
            "confidence": 0.0,
            "strategy": "error",
            "agents_used": [],
            "total_agents": 0,
            "metadata": {
                "synthesis_method": "error",
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }


class LocalResultProcessor:
    """Processor for local agent results."""
    
    @staticmethod
    def process_local_results(results: List[AgentResult]) -> Dict[str, Any]:
        """Process results from local agents."""
        valid_results = [r for r in results if r.confidence > 0.0 and r.result is not None]
        
        if not valid_results:
            return {"result": "No valid local results", "confidence": 0.0}
        
        # Select best local result
        best_result = max(valid_results, key=lambda r: r.confidence)
        
        return {
            "result": str(best_result.result),
            "confidence": best_result.confidence,
            "agent_id": best_result.agent_id
        }


class A2AResultProcessor:
    """Processor for A2A agent results."""
    
    @staticmethod
    def process_a2a_results(results: List[AgentResult]) -> Dict[str, Any]:
        """Process results from A2A agents."""
        valid_results = [r for r in results if r.confidence > 0.0 and r.result is not None]
        
        if not valid_results:
            return {"result": "No valid A2A results", "confidence": 0.0}
        
        # Select best A2A result
        best_result = max(valid_results, key=lambda r: r.confidence)
        
        return {
            "result": str(best_result.result),
            "confidence": best_result.confidence,
            "agent_id": best_result.agent_id
        }


class HybridResultProcessor:
    """Processor for hybrid (local + A2A) results."""
    
    def __init__(self):
        self.synthesizer = ResultSynthesizer()
        self.local_processor = LocalResultProcessor()
        self.a2a_processor = A2AResultProcessor()
    
    async def process_hybrid_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Process hybrid results using the synthesizer."""
        return await self.synthesizer.synthesize_results(results, strategy="hybrid") 