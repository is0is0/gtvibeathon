"""
Database query utilities for Voxel.

This module provides common query functions and analytics for the Voxel database.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from .models import Project, Generation, AgentExecution, Script, Render, Review, Tag, GenerationTag, Analytics

logger = logging.getLogger(__name__)


class DatabaseQueries:
    """Database query utilities."""

    def __init__(self, db_manager):
        """Initialize with database manager."""
        self.db_manager = db_manager

    def get_project_history(self, project_id: int) -> List[Generation]:
        """Get all generations for a project."""
        with self.db_manager.get_session() as session:
            return session.query(Generation).filter(
                Generation.project_id == project_id
            ).order_by(desc(Generation.created_at)).all()

    def get_generation_details(self, generation_id: int) -> Dict[str, Any]:
        """Get detailed information about a generation."""
        with self.db_manager.get_session() as session:
            generation = session.query(Generation).filter(Generation.id == generation_id).first()
            if not generation:
                return {}

            # Get all related data
            agent_executions = session.query(AgentExecution).filter(
                AgentExecution.generation_id == generation_id
            ).order_by(AgentExecution.created_at).all()

            scripts = session.query(Script).filter(
                Script.generation_id == generation_id
            ).order_by(Script.created_at).all()

            renders = session.query(Render).filter(
                Render.generation_id == generation_id
            ).order_by(Render.created_at).all()

            reviews = session.query(Review).filter(
                Review.generation_id == generation_id
            ).order_by(Review.created_at).all()

            return {
                "generation": generation,
                "agent_executions": agent_executions,
                "scripts": scripts,
                "renders": renders,
                "reviews": reviews,
            }

    def get_recent_generations(self, limit: int = 10) -> List[Generation]:
        """Get recent generations across all projects."""
        with self.db_manager.get_session() as session:
            return session.query(Generation).order_by(
                desc(Generation.created_at)
            ).limit(limit).all()

    def get_generations_by_status(self, status: str) -> List[Generation]:
        """Get generations by status."""
        with self.db_manager.get_session() as session:
            return session.query(Generation).filter(
                Generation.status == status
            ).order_by(desc(Generation.created_at)).all()

    def get_agent_performance(self, agent_type: str, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a specific agent type."""
        with self.db_manager.get_session() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            executions = session.query(AgentExecution).filter(
                AgentExecution.agent_type == agent_type,
                AgentExecution.created_at >= start_date
            ).all()

            if not executions:
                return {"total_executions": 0, "success_rate": 0, "avg_time_ms": 0}

            total_executions = len(executions)
            successful_executions = len([e for e in executions if e.status == "success"])
            success_rate = (successful_executions / total_executions) * 100 if total_executions > 0 else 0
            
            avg_time = sum(e.execution_time_ms for e in executions if e.execution_time_ms) / total_executions if total_executions > 0 else 0
            total_tokens = sum(e.token_count for e in executions if e.token_count) or 0

            return {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "success_rate": success_rate,
                "avg_time_ms": avg_time,
                "total_tokens": total_tokens,
            }

    def get_project_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get statistics for a specific project."""
        with self.db_manager.get_session() as session:
            generations = session.query(Generation).filter(
                Generation.project_id == project_id
            ).all()

            if not generations:
                return {"total_generations": 0, "success_rate": 0, "avg_quality": 0}

            total_generations = len(generations)
            completed_generations = len([g for g in generations if g.status == "completed"])
            success_rate = (completed_generations / total_generations) * 100 if total_generations > 0 else 0

            # Get quality scores
            quality_scores = [g.quality_score for g in generations if g.quality_score is not None]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

            # Get total render time
            total_render_time = 0
            for generation in generations:
                renders = session.query(Render).filter(Render.generation_id == generation.id).all()
                total_render_time += sum(r.render_time_seconds for r in renders if r.render_time_seconds)

            return {
                "total_generations": total_generations,
                "completed_generations": completed_generations,
                "success_rate": success_rate,
                "avg_quality": avg_quality,
                "total_render_time": total_render_time,
            }

    def get_system_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get system-wide analytics."""
        with self.db_manager.get_session() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            # Total generations
            total_generations = session.query(Generation).filter(
                Generation.created_at >= start_date
            ).count()

            # Successful generations
            successful_generations = session.query(Generation).filter(
                Generation.created_at >= start_date,
                Generation.status == "completed"
            ).count()

            # Average quality score
            avg_quality_result = session.query(func.avg(Generation.quality_score)).filter(
                Generation.created_at >= start_date,
                Generation.quality_score.isnot(None)
            ).scalar()
            avg_quality = avg_quality_result or 0

            # Total render time
            total_render_time = session.query(func.sum(Render.render_time_seconds)).filter(
                Render.created_at >= start_date
            ).scalar() or 0

            # Total tokens used
            total_tokens = session.query(func.sum(AgentExecution.token_count)).filter(
                AgentExecution.created_at >= start_date,
                AgentExecution.token_count.isnot(None)
            ).scalar() or 0

            # Most used tags
            tag_usage = session.query(
                Tag.name,
                func.count(GenerationTag.tag_id).label('usage_count')
            ).join(GenerationTag).filter(
                GenerationTag.created_at >= start_date
            ).group_by(Tag.name).order_by(desc('usage_count')).limit(10).all()

            return {
                "total_generations": total_generations,
                "successful_generations": successful_generations,
                "success_rate": (successful_generations / total_generations * 100) if total_generations > 0 else 0,
                "avg_quality": avg_quality,
                "total_render_time": total_render_time,
                "total_tokens": total_tokens,
                "most_used_tags": [{"name": name, "count": count} for name, count in tag_usage],
            }

    def search_generations(self, query: str, limit: int = 20) -> List[Generation]:
        """Search generations by prompt text."""
        with self.db_manager.get_session() as session:
            return session.query(Generation).filter(
                Generation.prompt.ilike(f"%{query}%")
            ).order_by(desc(Generation.created_at)).limit(limit).all()

    def get_generations_by_tag(self, tag_name: str) -> List[Generation]:
        """Get generations that have a specific tag."""
        with self.db_manager.get_session() as session:
            return session.query(Generation).join(
                GenerationTag
            ).join(Tag).filter(
                Tag.name == tag_name
            ).order_by(desc(Generation.created_at)).all()

    def get_quality_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get quality score trends over time."""
        with self.db_manager.get_session() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            # Group by date and get average quality
            results = session.query(
                func.date(Generation.created_at).label('date'),
                func.avg(Generation.quality_score).label('avg_quality'),
                func.count(Generation.id).label('count')
            ).filter(
                Generation.created_at >= start_date,
                Generation.quality_score.isnot(None)
            ).group_by(
                func.date(Generation.created_at)
            ).order_by(asc('date')).all()

            return [
                {
                    "date": str(result.date),
                    "avg_quality": float(result.avg_quality or 0),
                    "count": result.count
                }
                for result in results
            ]

    def get_agent_usage_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get usage statistics for each agent type."""
        with self.db_manager.get_session() as session:
            start_date = datetime.now() - timedelta(days=days)
            
            results = session.query(
                AgentExecution.agent_type,
                func.count(AgentExecution.id).label('total_executions'),
                func.avg(AgentExecution.execution_time_ms).label('avg_time'),
                func.sum(AgentExecution.token_count).label('total_tokens')
            ).filter(
                AgentExecution.created_at >= start_date
            ).group_by(
                AgentExecution.agent_type
            ).all()

            return [
                {
                    "agent_type": result.agent_type,
                    "total_executions": result.total_executions,
                    "avg_time_ms": float(result.avg_time or 0),
                    "total_tokens": result.total_tokens or 0
                }
                for result in results
            ]

    def get_failed_generations(self, limit: int = 20) -> List[Generation]:
        """Get recently failed generations for debugging."""
        with self.db_manager.get_session() as session:
            return session.query(Generation).filter(
                Generation.status == "failed"
            ).order_by(desc(Generation.created_at)).limit(limit).all()

    def get_longest_running_generations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get generations that took the longest to complete."""
        with self.db_manager.get_session() as session:
            # Calculate duration for completed generations
            results = session.query(
                Generation.id,
                Generation.prompt,
                Generation.created_at,
                Generation.completed_at,
                (Generation.completed_at - Generation.created_at).label('duration')
            ).filter(
                Generation.status == "completed",
                Generation.completed_at.isnot(None)
            ).order_by(desc('duration')).limit(limit).all()

            return [
                {
                    "id": result.id,
                    "prompt": result.prompt,
                    "duration_seconds": result.duration.total_seconds(),
                    "created_at": result.created_at,
                    "completed_at": result.completed_at
                }
                for result in results
            ]
