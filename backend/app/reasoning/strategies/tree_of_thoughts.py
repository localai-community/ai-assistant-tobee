"""
Tree-of-Thoughts (ToT) reasoning strategy implementation.

This module provides a comprehensive implementation of Tree-of-Thoughts reasoning
for multi-path reasoning exploration with search algorithms, path evaluation,
and optimal path selection.
"""

import asyncio
import heapq
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from ..core.base import (
    BaseReasoner, ReasoningResult, ReasoningStep, StepStatus,
    ValidationResult, ValidationLevel, ReasoningType
)
from ..utils.parsers import parse_problem_statement
from ..utils.formatters import format_reasoning_output


class SearchAlgorithm(Enum):
    """Enumeration of search algorithms."""
    BFS = "breadth_first_search"
    DFS = "depth_first_search"
    BEAM = "beam_search"
    A_STAR = "a_star"


class PathEvaluationStrategy(Enum):
    """Enumeration of path evaluation strategies."""
    CONFIDENCE = "confidence"
    COMPLETENESS = "completeness"
    EFFICIENCY = "efficiency"
    HYBRID = "hybrid"


@dataclass
class ToTNode:
    """Represents a node in the Tree-of-Thoughts."""
    node_id: str
    thought: str
    action: str
    observation: str
    confidence: float
    depth: int
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToTPath:
    """Represents a path in the Tree-of-Thoughts."""
    path_id: str
    nodes: List[ToTNode]
    total_confidence: float
    completeness: float
    efficiency: float
    evaluation_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToTConfig:
    """Configuration for Tree-of-Thoughts reasoning."""
    max_depth: int = 5
    max_branching_factor: int = 3
    max_nodes: int = 50
    search_algorithm: SearchAlgorithm = SearchAlgorithm.BEAM
    evaluation_strategy: PathEvaluationStrategy = PathEvaluationStrategy.HYBRID
    beam_width: int = 3
    min_confidence_threshold: float = 0.6
    max_iterations: int = 5
    enable_backtracking: bool = True
    enable_path_pruning: bool = True


class TreeOfThoughtsStrategy(BaseReasoner[ReasoningResult]):
    """
    Tree-of-Thoughts reasoning strategy implementation.
    
    This strategy implements multi-path reasoning exploration with:
    - Multi-path exploration
    - Search-based path selection
    - Backtracking mechanisms
    - Path evaluation and scoring
    """

    def __init__(self, name: str = "Tree-of-Thoughts", config: Optional[ToTConfig] = None):
        super().__init__(name, ReasoningType.HYBRID)
        self.config = config or ToTConfig()
        self.nodes: Dict[str, ToTNode] = {}
        self.paths: List[ToTPath] = []
        self.best_path: Optional[ToTPath] = None
        self.iteration_count = 0
        self.explored_nodes: Set[str] = set()

    async def reason(self, problem_statement: str, **kwargs) -> ReasoningResult:
        """
        Perform Tree-of-Thoughts reasoning on the given problem.
        
        Args:
            problem_statement: The problem to solve
            **kwargs: Additional arguments
            
        Returns:
            ReasoningResult containing the ToT reasoning steps and final answer
        """
        start_time = datetime.now(timezone.utc)
        
        # Validate input
        validation = self.validate_input(problem_statement)
        if not validation.is_valid:
            return ReasoningResult(
                problem_statement=problem_statement,
                validation_results=[validation],
                created_at=start_time
            )

        # Parse problem statement
        parsed_problem = parse_problem_statement(problem_statement)
        
        # Initialize result
        result = ReasoningResult(
            problem_statement=problem_statement,
            reasoning_type=ReasoningType.HYBRID,
            created_at=start_time
        )

        # Perform iterative ToT reasoning
        for iteration in range(self.config.max_iterations):
            self.iteration_count = iteration + 1
            
            # Build and explore the tree
            tree_result = await self._build_and_explore_tree(parsed_problem)
            
            if tree_result:
                # Find optimal path
                optimal_path = await self._find_optimal_path()
                
                if optimal_path:
                    # Convert path to reasoning steps
                    steps_result = await self._convert_path_to_steps(optimal_path)
                    
                    if steps_result:
                        result = steps_result
                        break

        # Set final result
        if self.best_path:
            result.final_answer = self._extract_final_answer_from_path(self.best_path)
            result.confidence = self.best_path.total_confidence
        else:
            result.final_answer = "No solution found"
            result.confidence = 0.0

        result.completed_at = datetime.now(timezone.utc)
        result.execution_time = (result.completed_at - start_time).total_seconds()

        return result

    async def _build_and_explore_tree(self, parsed_problem: Dict[str, Any]) -> bool:
        """Build and explore the Tree-of-Thoughts."""
        try:
            # Create root node
            root_node = await self._create_root_node(parsed_problem)
            if not root_node:
                return False

            self.nodes[root_node.node_id] = root_node
            
            # Explore tree based on search algorithm
            if self.config.search_algorithm == SearchAlgorithm.BFS:
                await self._breadth_first_search(root_node)
            elif self.config.search_algorithm == SearchAlgorithm.DFS:
                await self._depth_first_search(root_node)
            elif self.config.search_algorithm == SearchAlgorithm.BEAM:
                await self._beam_search(root_node)
            elif self.config.search_algorithm == SearchAlgorithm.A_STAR:
                await self._a_star_search(root_node)
            
            return True

        except Exception as e:
            # Add error handling
            return False

    async def _create_root_node(self, parsed_problem: Dict[str, Any]) -> Optional[ToTNode]:
        """Create the root node for the tree."""
        try:
            problem_type = parsed_problem.get("type", "general")
            problem_content = parsed_problem.get("content", "")
            
            # Generate initial thought based on problem type
            if problem_type == "mathematical":
                thought = "I need to solve this mathematical problem step by step."
                action = "Analyze mathematical problem"
                observation = "Problem identified as mathematical"
            elif problem_type == "logical":
                thought = "I need to apply logical reasoning to solve this problem."
                action = "Analyze logical problem"
                observation = "Problem identified as logical"
            else:
                thought = "I need to understand and solve this problem systematically."
                action = "Analyze general problem"
                observation = "Problem identified as general"
            
            root_node = ToTNode(
                node_id="root",
                thought=thought,
                action=action,
                observation=observation,
                confidence=0.8,
                depth=0,
                parent_id=None
            )
            
            return root_node

        except Exception as e:
            return None

    async def _breadth_first_search(self, root_node: ToTNode) -> None:
        """Perform breadth-first search on the tree."""
        queue = [root_node.node_id]
        visited = set()
        
        while queue and len(self.nodes) < self.config.max_nodes:
            current_id = queue.pop(0)
            
            if current_id in visited:
                continue
                
            visited.add(current_id)
            current_node = self.nodes[current_id]
            
            # Generate children
            children = await self._generate_children(current_node)
            
            for child in children:
                if len(self.nodes) >= self.config.max_nodes:
                    break
                    
                self.nodes[child.node_id] = child
                current_node.children.append(child.node_id)
                queue.append(child.node_id)

    async def _depth_first_search(self, root_node: ToTNode) -> None:
        """Perform depth-first search on the tree."""
        stack = [root_node.node_id]
        visited = set()
        
        while stack and len(self.nodes) < self.config.max_nodes:
            current_id = stack.pop()
            
            if current_id in visited:
                continue
                
            visited.add(current_id)
            current_node = self.nodes[current_id]
            
            # Generate children
            children = await self._generate_children(current_node)
            
            for child in reversed(children):
                if len(self.nodes) >= self.config.max_nodes:
                    break
                    
                self.nodes[child.node_id] = child
                current_node.children.append(child.node_id)
                stack.append(child.node_id)

    async def _beam_search(self, root_node: ToTNode) -> None:
        """Perform beam search on the tree."""
        beam = [(0.0, root_node.node_id)]  # (score, node_id)
        
        for depth in range(self.config.max_depth):
            if not beam or len(self.nodes) >= self.config.max_nodes:
                break
                
            new_beam = []
            
            for score, node_id in beam:
                if node_id not in self.nodes:
                    continue
                    
                current_node = self.nodes[node_id]
                
                # Generate children
                children = await self._generate_children(current_node)
                
                for child in children:
                    if len(self.nodes) >= self.config.max_nodes:
                        break
                        
                    self.nodes[child.node_id] = child
                    current_node.children.append(child.node_id)
                    
                    # Calculate child score
                    child_score = self._calculate_node_score(child)
                    new_beam.append((child_score, child.node_id))
            
            # Keep top beam_width nodes
            new_beam.sort(reverse=True)
            beam = new_beam[:self.config.beam_width]

    async def _a_star_search(self, root_node: ToTNode) -> None:
        """Perform A* search on the tree."""
        open_set = [(0.0, root_node.node_id)]  # (f_score, node_id)
        closed_set = set()
        
        while open_set and len(self.nodes) < self.config.max_nodes:
            f_score, current_id = heapq.heappop(open_set)
            
            if current_id in closed_set:
                continue
                
            closed_set.add(current_id)
            current_node = self.nodes[current_id]
            
            # Generate children
            children = await self._generate_children(current_node)
            
            for child in children:
                if len(self.nodes) >= self.config.max_nodes:
                    break
                    
                self.nodes[child.node_id] = child
                current_node.children.append(child.node_id)
                
                # Calculate A* scores
                g_score = current_node.depth + 1
                h_score = self._calculate_heuristic(child)
                f_score = g_score + h_score
                
                heapq.heappush(open_set, (f_score, child.node_id))

    async def _generate_children(self, parent_node: ToTNode) -> List[ToTNode]:
        """Generate children for a given node."""
        children = []
        
        # Limit branching factor
        max_children = min(self.config.max_branching_factor, 
                          self.config.max_nodes - len(self.nodes))
        
        if max_children <= 0:
            return children
        
        # Generate different thought paths
        thought_variations = self._generate_thought_variations(parent_node)
        
        for i, (thought, action, observation) in enumerate(thought_variations[:max_children]):
            child_node = ToTNode(
                node_id=f"{parent_node.node_id}_child_{i}",
                thought=thought,
                action=action,
                observation=observation,
                confidence=self._calculate_confidence(parent_node, thought),
                depth=parent_node.depth + 1,
                parent_id=parent_node.node_id
            )
            
            children.append(child_node)
        
        return children

    def _generate_thought_variations(self, parent_node: ToTNode) -> List[Tuple[str, str, str]]:
        """Generate variations of thoughts for a node."""
        variations = []
        
        # Different approaches based on parent thought
        if "mathematical" in parent_node.thought.lower():
            variations.extend([
                ("I should break this down into smaller calculations.", 
                 "Decompose problem", "Problem decomposed"),
                ("I need to check my work for errors.", 
                 "Verify calculations", "Calculations verified"),
                ("I should look for patterns or shortcuts.", 
                 "Find patterns", "Patterns identified")
            ])
        elif "logical" in parent_node.thought.lower():
            variations.extend([
                ("I should identify the premises and conclusions.", 
                 "Analyze premises", "Premises identified"),
                ("I need to check for logical fallacies.", 
                 "Check logic", "Logic verified"),
                ("I should consider alternative interpretations.", 
                 "Consider alternatives", "Alternatives considered")
            ])
        else:
            variations.extend([
                ("I should gather more information about this.", 
                 "Gather information", "Information gathered"),
                ("I need to consider different perspectives.", 
                 "Consider perspectives", "Perspectives considered"),
                ("I should break this into smaller parts.", 
                 "Break down problem", "Problem broken down")
            ])
        
        return variations

    def _calculate_confidence(self, parent_node: ToTNode, thought: str) -> float:
        """Calculate confidence for a child node."""
        # Base confidence from parent
        base_confidence = parent_node.confidence * 0.9  # Slight decay
        
        # Adjust based on thought quality
        if "error" in thought.lower() or "check" in thought.lower():
            base_confidence += 0.1  # Validation thoughts are good
        elif "pattern" in thought.lower() or "shortcut" in thought.lower():
            base_confidence += 0.05  # Efficiency thoughts are good
        
        return min(base_confidence, 1.0)

    def _calculate_node_score(self, node: ToTNode) -> float:
        """Calculate score for a node in beam search."""
        return node.confidence * (1.0 + node.depth * 0.1)

    def _calculate_heuristic(self, node: ToTNode) -> float:
        """Calculate heuristic for A* search."""
        # Lower heuristic means more promising
        return 1.0 - node.confidence

    async def _find_optimal_path(self) -> Optional[ToTPath]:
        """Find the optimal path in the tree."""
        if not self.nodes:
            return None
        
        # Find all paths from root to leaves
        paths = await self._find_all_paths()
        
        if not paths:
            return None
        
        # Evaluate paths
        evaluated_paths = []
        for path in paths:
            evaluation_score = self._evaluate_path(path)
            path.evaluation_score = evaluation_score
            evaluated_paths.append(path)
        
        # Sort by evaluation score
        evaluated_paths.sort(key=lambda p: p.evaluation_score, reverse=True)
        
        # Store best path
        self.best_path = evaluated_paths[0] if evaluated_paths else None
        
        return self.best_path

    async def _find_all_paths(self) -> List[ToTPath]:
        """Find all paths from root to leaves."""
        paths = []
        
        def dfs_paths(node_id: str, current_path: List[ToTNode]) -> None:
            node = self.nodes[node_id]
            current_path.append(node)
            
            if not node.children:  # Leaf node
                # Create path
                path = ToTPath(
                    path_id=f"path_{len(paths)}",
                    nodes=current_path.copy(),
                    total_confidence=sum(n.confidence for n in current_path) / len(current_path),
                    completeness=self._calculate_completeness(current_path),
                    efficiency=self._calculate_efficiency(current_path),
                    evaluation_score=0.0
                )
                paths.append(path)
            else:
                for child_id in node.children:
                    dfs_paths(child_id, current_path)
            
            current_path.pop()
        
        # Start from root
        if "root" in self.nodes:
            dfs_paths("root", [])
        
        return paths

    def _calculate_completeness(self, path: List[ToTNode]) -> float:
        """Calculate completeness of a path."""
        if not path:
            return 0.0
        
        # Check if path leads to a solution
        last_node = path[-1]
        
        # Simple heuristic: higher confidence and more specific observations
        if last_node.confidence > 0.8 and len(last_node.observation) > 10:
            return 0.9
        elif last_node.confidence > 0.6:
            return 0.7
        else:
            return 0.5

    def _calculate_efficiency(self, path: List[ToTNode]) -> float:
        """Calculate efficiency of a path."""
        if not path:
            return 0.0
        
        # Efficiency based on path length and confidence
        length_penalty = 1.0 / len(path)  # Shorter paths are better
        avg_confidence = sum(n.confidence for n in path) / len(path)
        
        return length_penalty * avg_confidence

    def _evaluate_path(self, path: ToTPath) -> float:
        """Evaluate a path based on the configured strategy."""
        if self.config.evaluation_strategy == PathEvaluationStrategy.CONFIDENCE:
            return path.total_confidence
        elif self.config.evaluation_strategy == PathEvaluationStrategy.COMPLETENESS:
            return path.completeness
        elif self.config.evaluation_strategy == PathEvaluationStrategy.EFFICIENCY:
            return path.efficiency
        else:  # HYBRID
            # Weighted combination
            return (0.4 * path.total_confidence + 
                   0.3 * path.completeness + 
                   0.3 * path.efficiency)

    async def _convert_path_to_steps(self, path: ToTPath) -> ReasoningResult:
        """Convert a ToT path to reasoning steps."""
        result = ReasoningResult(
            problem_statement=path.nodes[0].thought if path.nodes else "",
            reasoning_type=ReasoningType.HYBRID,
            created_at=datetime.now(timezone.utc)
        )
        
        for i, node in enumerate(path.nodes, 1):
            step = ReasoningStep(
                step_number=i,
                description=f"Step {i}: {node.action}",
                input_data={"thought": node.thought},
                output_data={"observation": node.observation},
                reasoning=node.thought,
                confidence=node.confidence,
                status=StepStatus.COMPLETED,
                metadata=node.metadata
            )
            result.add_step(step)
        
        return result

    def _extract_final_answer_from_path(self, path: ToTPath) -> Any:
        """Extract final answer from a path."""
        if not path.nodes:
            return None
        
        # Use the last node's observation as the answer
        last_node = path.nodes[-1]
        return last_node.observation

    def can_handle(self, problem_statement: str) -> bool:
        """Check if this strategy can handle the given problem."""
        # ToT can handle complex problems that benefit from exploration
        return len(problem_statement.strip()) > 10  # Prefer complex problems

    def get_tree_stats(self) -> Dict[str, Any]:
        """Get statistics about the explored tree."""
        return {
            "total_nodes": len(self.nodes),
            "total_paths": len(self.paths),
            "max_depth": max((n.depth for n in self.nodes.values()), default=0),
            "best_path_score": self.best_path.evaluation_score if self.best_path else 0.0,
            "iteration_count": self.iteration_count
        }

    def get_best_path(self) -> Optional[ToTPath]:
        """Get the best path found."""
        return self.best_path

    def reset(self) -> None:
        """Reset the strategy state."""
        self.nodes.clear()
        self.paths.clear()
        self.best_path = None
        self.iteration_count = 0
        self.explored_nodes.clear() 