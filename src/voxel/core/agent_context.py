"""Agent context for sharing information between agents."""

import logging
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
from collections import defaultdict

from voxel.core.models import AgentRole

logger = logging.getLogger(__name__)


class ContextType(str, Enum):
    """Types of context information."""
    GEOMETRY = "geometry"
    MATERIALS = "materials"
    LIGHTING = "lighting"
    ANIMATION = "animation"
    RIGGING = "rigging"
    COMPOSITING = "compositing"
    SEQUENCE = "sequence"
    FEEDBACK = "feedback"
    SUGGESTIONS = "suggestions"


@dataclass
class ContextItem:
    """A single piece of context information."""
    type: ContextType
    source_agent: AgentRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    tags: Set[str] = field(default_factory=set)


class AgentContext:
    """Shared context for agent collaboration with real-time updates."""
    
    def __init__(self):
        self.context_items: List[ContextItem] = []
        self.agent_insights: Dict[AgentRole, Dict[str, Any]] = {}
        self.collaboration_history: List[Dict[str, Any]] = []
        self.shared_assets: Dict[str, Any] = {}
        
        # Real-time update system
        self._observers: Dict[AgentRole, List[Callable]] = defaultdict(list)
        self._context_lock = threading.Lock()
        self._update_queue: List[Dict[str, Any]] = []
        self._last_update_time: Dict[AgentRole, datetime] = {}
    
    def add_context(self, 
                   context_type: ContextType, 
                   source_agent: AgentRole, 
                   content: str,
                   metadata: Optional[Dict[str, Any]] = None,
                   confidence: float = 1.0,
                   tags: Optional[Set[str]] = None) -> None:
        """Add context information from an agent with real-time updates."""
        with self._context_lock:
            item = ContextItem(
                type=context_type,
                source_agent=source_agent,
                content=content,
                metadata=metadata or {},
                confidence=confidence,
                tags=tags or set()
            )
            self.context_items.append(item)
            
            # Update timestamp for source agent
            self._last_update_time[source_agent] = datetime.now()
            
            # Create update notification
            update_notification = {
                "type": "context_added",
                "context_type": context_type,
                "source_agent": source_agent,
                "content": content,
                "timestamp": datetime.now(),
                "metadata": metadata or {}
            }
            self._update_queue.append(update_notification)
            
            # Notify relevant observers in real-time
            self._notify_observers(update_notification)
            
        logger.info(f"Added {context_type} context from {source_agent}: {content[:50]}...")
    
    def get_context(self, 
                   context_type: Optional[ContextType] = None,
                   source_agent: Optional[AgentRole] = None,
                   tags: Optional[Set[str]] = None,
                   min_confidence: float = 0.0) -> List[ContextItem]:
        """Get context items matching criteria."""
        filtered = self.context_items
        
        if context_type:
            filtered = [item for item in filtered if item.type == context_type]
        
        if source_agent:
            filtered = [item for item in filtered if item.source_agent == source_agent]
        
        if tags:
            filtered = [item for item in filtered if any(tag in item.tags for tag in tags)]
        
        if min_confidence > 0:
            filtered = [item for item in filtered if item.confidence >= min_confidence]
        
        # Sort by confidence and timestamp
        filtered.sort(key=lambda x: (x.confidence, x.timestamp), reverse=True)
        return filtered
    
    def get_agent_insights(self, agent_role: AgentRole) -> Dict[str, Any]:
        """Get insights from a specific agent."""
        return self.agent_insights.get(agent_role, {})
    
    def set_agent_insights(self, agent_role: AgentRole, insights: Dict[str, Any]) -> None:
        """Set insights from an agent."""
        self.agent_insights[agent_role] = insights
        logger.info(f"Updated insights for {agent_role}: {len(insights)} items")
    
    def get_related_context(self, current_agent: AgentRole, context_type: ContextType) -> List[ContextItem]:
        """Get context related to what the current agent is working on."""
        # Get context from other agents that's relevant to current agent's work
        related = []
        
        for item in self.context_items:
            if item.source_agent == current_agent:
                continue  # Skip own context
            
            # Check if context is relevant to current agent's work
            if self._is_relevant_context(current_agent, context_type, item):
                related.append(item)
        
        return related
    
    def _is_relevant_context(self, current_agent: AgentRole, context_type: ContextType, item: Optional[ContextItem]) -> bool:
        """Check if context item is relevant to current agent's work."""
        # Define relevance rules
        relevance_rules = {
            AgentRole.BUILDER: {
                ContextType.GEOMETRY: True,
                ContextType.MATERIALS: True,
                ContextType.LIGHTING: False,
                ContextType.ANIMATION: False,
                ContextType.RIGGING: True,  # Builder should know about rigging needs
                ContextType.COMPOSITING: False,
                ContextType.SEQUENCE: False,
            },
            AgentRole.TEXTURE: {
                ContextType.GEOMETRY: True,  # Texture needs to know about geometry
                ContextType.MATERIALS: True,
                ContextType.LIGHTING: True,  # Lighting affects material appearance
                ContextType.ANIMATION: False,
                ContextType.RIGGING: False,
                ContextType.COMPOSITING: True,  # Compositing affects final look
                ContextType.SEQUENCE: False,
            },
            AgentRole.RENDER: {
                ContextType.GEOMETRY: True,
                ContextType.MATERIALS: True,
                ContextType.LIGHTING: True,
                ContextType.ANIMATION: True,
                ContextType.RIGGING: True,
                ContextType.COMPOSITING: True,
                ContextType.SEQUENCE: False,
            },
            AgentRole.ANIMATION: {
                ContextType.GEOMETRY: True,
                ContextType.MATERIALS: False,
                ContextType.LIGHTING: False,
                ContextType.ANIMATION: True,
                ContextType.RIGGING: True,  # Animation needs rigging info
                ContextType.COMPOSITING: False,
                ContextType.SEQUENCE: True,  # Animation feeds into sequences
            },
            AgentRole.RIGGING: {
                ContextType.GEOMETRY: True,  # Rigging needs geometry info
                ContextType.MATERIALS: False,
                ContextType.LIGHTING: False,
                ContextType.ANIMATION: True,  # Rigging affects animation
                ContextType.RIGGING: True,
                ContextType.COMPOSITING: False,
                ContextType.SEQUENCE: False,
            },
            AgentRole.COMPOSITING: {
                ContextType.GEOMETRY: False,
                ContextType.MATERIALS: True,  # Compositing affects materials
                ContextType.LIGHTING: True,  # Compositing affects lighting
                ContextType.ANIMATION: True,  # Compositing affects animation
                ContextType.RIGGING: False,
                ContextType.COMPOSITING: True,
                ContextType.SEQUENCE: True,  # Compositing feeds into sequences
            },
            AgentRole.SEQUENCE: {
                ContextType.GEOMETRY: False,
                ContextType.MATERIALS: False,
                ContextType.LIGHTING: False,
                ContextType.ANIMATION: True,  # Sequences use animations
                ContextType.RIGGING: False,
                ContextType.COMPOSITING: True,  # Sequences use composited footage
                ContextType.SEQUENCE: True,
            },
        }
        
        return relevance_rules.get(current_agent, {}).get(context_type, False)
    
    def get_collaboration_summary(self) -> str:
        """Get a summary of all collaboration context."""
        summary_parts = []
        
        # Group by context type
        by_type = {}
        for item in self.context_items:
            if item.type not in by_type:
                by_type[item.type] = []
            by_type[item.type].append(item)
        
        for context_type, items in by_type.items():
            summary_parts.append(f"\n{context_type.value.upper()}:")
            for item in items[:3]:  # Show top 3 items
                summary_parts.append(f"  - {item.source_agent.value}: {item.content[:100]}...")
        
        return "\n".join(summary_parts)
    
    def add_collaboration_event(self, event_type: str, agent: AgentRole, details: Dict[str, Any]) -> None:
        """Add a collaboration event to history."""
        event = {
            "timestamp": datetime.now(),
            "event_type": event_type,
            "agent": agent,
            "details": details
        }
        self.collaboration_history.append(event)
        logger.info(f"Collaboration event: {event_type} from {agent}")
    
    def get_shared_asset(self, asset_name: str) -> Any:
        """Get a shared asset."""
        return self.shared_assets.get(asset_name)
    
    def set_shared_asset(self, asset_name: str, asset: Any) -> None:
        """Set a shared asset."""
        self.shared_assets[asset_name] = asset
        logger.info(f"Shared asset '{asset_name}' set by agent")
    
    def clear_context(self) -> None:
        """Clear all context (useful for new scenes)."""
        with self._context_lock:
            self.context_items.clear()
            self.agent_insights.clear()
            self.collaboration_history.clear()
            self.shared_assets.clear()
            self._update_queue.clear()
            self._last_update_time.clear()
        logger.info("Agent context cleared")
    
    def register_observer(self, agent_role: AgentRole, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register an agent to receive real-time context updates."""
        self._observers[agent_role].append(callback)
        logger.info(f"Registered observer for {agent_role}")
    
    def unregister_observer(self, agent_role: AgentRole, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Unregister an agent from receiving updates."""
        if callback in self._observers[agent_role]:
            self._observers[agent_role].remove(callback)
            logger.info(f"Unregistered observer for {agent_role}")
    
    def _notify_observers(self, update_notification: Dict[str, Any]) -> None:
        """Notify all relevant observers of context changes."""
        context_type = update_notification["context_type"]
        source_agent = update_notification["source_agent"]
        
        # Notify agents that are interested in this context type
        for agent_role, callbacks in self._observers.items():
            if agent_role == source_agent:
                continue  # Don't notify the source agent
            
            # Check if this agent is interested in this context type
            if self._is_relevant_context(agent_role, context_type, None):
                for callback in callbacks:
                    try:
                        callback(update_notification)
                    except Exception as e:
                        logger.error(f"Error notifying {agent_role}: {e}")
    
    def get_updates_since(self, agent_role: AgentRole, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get all updates since a specific time for an agent."""
        if since is None:
            since = self._last_update_time.get(agent_role, datetime.min)
        
        with self._context_lock:
            relevant_updates = []
            for update in self._update_queue:
                if update["timestamp"] > since:
                    # Check if this update is relevant to the agent
                    if self._is_relevant_context(agent_role, update["context_type"], None):
                        relevant_updates.append(update)
            
            return relevant_updates
    
    def get_latest_context(self, agent_role: AgentRole, context_type: ContextType) -> Optional[ContextItem]:
        """Get the latest context item of a specific type relevant to an agent."""
        relevant_items = self.get_related_context(agent_role, context_type)
        return relevant_items[0] if relevant_items else None
    
    def subscribe_to_context_type(self, agent_role: AgentRole, context_type: ContextType, 
                                callback: Callable[[ContextItem], None]) -> None:
        """Subscribe to specific context type updates."""
        def context_filter(update: Dict[str, Any]) -> None:
            if update["context_type"] == context_type:
                # Find the corresponding context item
                for item in self.context_items:
                    if (item.type == context_type and 
                        item.source_agent == update["source_agent"] and
                        item.content == update["content"]):
                        callback(item)
                        break
        
        self.register_observer(agent_role, context_filter)
    
    def get_context_stream(self, agent_role: AgentRole) -> List[Dict[str, Any]]:
        """Get a stream of all context updates relevant to an agent."""
        return self.get_updates_since(agent_role)
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get statistics about the context."""
        return {
            "total_context_items": len(self.context_items),
            "context_by_type": {t.value: len([i for i in self.context_items if i.type == t]) 
                              for t in ContextType},
            "context_by_agent": {a.value: len([i for i in self.context_items if i.source_agent == a]) 
                                for a in AgentRole},
            "collaboration_events": len(self.collaboration_history),
            "shared_assets": len(self.shared_assets)
        }
