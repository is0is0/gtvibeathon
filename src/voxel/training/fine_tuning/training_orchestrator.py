"""
Training Orchestrator - Manages fine-tuning jobs for Claude and GPT models.
Submits training jobs, monitors progress, and manages model deployment.
"""

import logging
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Provider(str, Enum):
    """ML provider for fine-tuning."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class JobStatus(str, Enum):
    """Training job status."""
    PENDING = "pending"
    UPLOADING = "uploading"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TrainingJob:
    """Represents a fine-tuning job."""
    job_id: str
    provider: Provider
    agent_role: str  # builder, texture, render, etc.
    model_base: str  # claude-3-sonnet, gpt-4, etc.
    status: JobStatus
    created_at: str
    training_file: str
    validation_file: Optional[str] = None
    fine_tuned_model: Optional[str] = None
    training_tokens: int = 0
    cost_usd: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TrainingOrchestrator:
    """
    Orchestrates fine-tuning jobs across multiple providers.
    Manages job submission, monitoring, and model deployment.
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        output_dir: Path = Path("./training_data/training_jobs")
    ):
        """
        Initialize orchestrator.

        Args:
            anthropic_api_key: Anthropic API key
            openai_api_key: OpenAI API key
            output_dir: Directory to save job metadata
        """
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.jobs_file = self.output_dir / "training_jobs.json"
        self.jobs: Dict[str, TrainingJob] = {}

        self._load_jobs()

        logger.info(f"TrainingOrchestrator initialized ({len(self.jobs)} existing jobs)")

    def _load_jobs(self):
        """Load existing training jobs."""
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file, 'r') as f:
                    data = json.load(f)
                    for job_data in data:
                        job = TrainingJob(**job_data)
                        self.jobs[job.job_id] = job
                logger.info(f"Loaded {len(self.jobs)} training jobs")
            except Exception as e:
                logger.warning(f"Could not load jobs: {e}")

    def _save_jobs(self):
        """Save training jobs to file."""
        jobs_list = [asdict(job) for job in self.jobs.values()]

        with open(self.jobs_file, 'w') as f:
            json.dump(jobs_list, f, indent=2)

        logger.info(f"Saved {len(self.jobs)} training jobs")

    def submit_claude_job(
        self,
        agent_role: str,
        training_file: Path,
        validation_file: Optional[Path] = None,
        model_base: str = "claude-3-sonnet-20240229"
    ) -> TrainingJob:
        """
        Submit fine-tuning job to Anthropic.

        Args:
            agent_role: Agent role (builder, texture, etc.)
            training_file: Path to formatted training data
            validation_file: Optional validation data
            model_base: Base model to fine-tune

        Returns:
            TrainingJob instance
        """
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not set")

        logger.info(f"Submitting Claude fine-tuning job for {agent_role}...")

        try:
            # NOTE: This is a placeholder - actual Anthropic fine-tuning API
            # would be used here. As of early 2025, Anthropic's fine-tuning
            # API may have different endpoints/methods.

            # Simulated job creation
            job_id = f"claude-ft-{agent_role}-{int(time.time())}"

            job = TrainingJob(
                job_id=job_id,
                provider=Provider.ANTHROPIC,
                agent_role=agent_role,
                model_base=model_base,
                status=JobStatus.PENDING,
                created_at=datetime.now().isoformat(),
                training_file=str(training_file),
                validation_file=str(validation_file) if validation_file else None,
                metadata={
                    "note": "Placeholder - actual API call needed"
                }
            )

            self.jobs[job_id] = job
            self._save_jobs()

            logger.info(f"Created Claude job: {job_id}")

            # In production, would call:
            # import anthropic
            # client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            # response = client.fine_tuning.create(
            #     training_file=training_file,
            #     model=model_base,
            #     ...
            # )

            return job

        except Exception as e:
            logger.error(f"Error submitting Claude job: {e}")
            raise

    def submit_openai_job(
        self,
        agent_role: str,
        training_file: Path,
        validation_file: Optional[Path] = None,
        model_base: str = "gpt-4-0613",
        n_epochs: int = 3
    ) -> TrainingJob:
        """
        Submit fine-tuning job to OpenAI.

        Args:
            agent_role: Agent role (builder, texture, etc.)
            training_file: Path to formatted training data
            validation_file: Optional validation data
            model_base: Base model to fine-tune
            n_epochs: Number of training epochs

        Returns:
            TrainingJob instance
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not set")

        logger.info(f"Submitting OpenAI fine-tuning job for {agent_role}...")

        try:
            # NOTE: This uses OpenAI's actual fine-tuning API
            import openai

            openai.api_key = self.openai_api_key

            # Upload training file
            logger.info("Uploading training file...")
            with open(training_file, 'rb') as f:
                training_file_obj = openai.File.create(
                    file=f,
                    purpose='fine-tune'
                )

            # Upload validation file if provided
            validation_file_id = None
            if validation_file:
                logger.info("Uploading validation file...")
                with open(validation_file, 'rb') as f:
                    validation_file_obj = openai.File.create(
                        file=f,
                        purpose='fine-tune'
                    )
                    validation_file_id = validation_file_obj.id

            # Create fine-tuning job
            logger.info("Creating fine-tuning job...")
            fine_tune_job = openai.FineTuningJob.create(
                training_file=training_file_obj.id,
                validation_file=validation_file_id,
                model=model_base,
                hyperparameters={
                    "n_epochs": n_epochs
                }
            )

            job_id = fine_tune_job.id

            job = TrainingJob(
                job_id=job_id,
                provider=Provider.OPENAI,
                agent_role=agent_role,
                model_base=model_base,
                status=JobStatus.TRAINING,
                created_at=datetime.now().isoformat(),
                training_file=str(training_file),
                validation_file=str(validation_file) if validation_file else None,
                metadata={
                    "openai_training_file_id": training_file_obj.id,
                    "openai_validation_file_id": validation_file_id,
                    "n_epochs": n_epochs
                }
            )

            self.jobs[job_id] = job
            self._save_jobs()

            logger.info(f"Created OpenAI job: {job_id}")

            return job

        except Exception as e:
            logger.error(f"Error submitting OpenAI job: {e}")

            # Create failed job record
            job_id = f"openai-ft-{agent_role}-{int(time.time())}-failed"
            job = TrainingJob(
                job_id=job_id,
                provider=Provider.OPENAI,
                agent_role=agent_role,
                model_base=model_base,
                status=JobStatus.FAILED,
                created_at=datetime.now().isoformat(),
                training_file=str(training_file),
                error=str(e)
            )

            self.jobs[job_id] = job
            self._save_jobs()

            raise

    def check_job_status(self, job_id: str) -> TrainingJob:
        """
        Check status of a training job.

        Args:
            job_id: Job ID

        Returns:
            Updated TrainingJob
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job not found: {job_id}")

        job = self.jobs[job_id]

        try:
            if job.provider == Provider.OPENAI:
                import openai
                openai.api_key = self.openai_api_key

                # Get job status
                fine_tune_job = openai.FineTuningJob.retrieve(job_id)

                # Update job status
                status_map = {
                    "validating_files": JobStatus.UPLOADING,
                    "queued": JobStatus.PENDING,
                    "running": JobStatus.TRAINING,
                    "succeeded": JobStatus.COMPLETED,
                    "failed": JobStatus.FAILED,
                    "cancelled": JobStatus.CANCELLED
                }

                job.status = status_map.get(fine_tune_job.status, JobStatus.PENDING)

                if fine_tune_job.fine_tuned_model:
                    job.fine_tuned_model = fine_tune_job.fine_tuned_model

                if fine_tune_job.error:
                    job.error = str(fine_tune_job.error)

                self._save_jobs()

                logger.info(f"Job {job_id} status: {job.status}")

            elif job.provider == Provider.ANTHROPIC:
                # Placeholder for Anthropic status check
                logger.info(f"Anthropic status check not yet implemented for {job_id}")

        except Exception as e:
            logger.error(f"Error checking job status: {e}")
            job.error = str(e)
            self._save_jobs()

        return job

    def monitor_all_jobs(self, poll_interval: int = 60) -> Dict[str, Any]:
        """
        Monitor all active training jobs.

        Args:
            poll_interval: Seconds between status checks

        Returns:
            Summary of all jobs
        """
        logger.info(f"Monitoring {len(self.jobs)} training jobs...")

        active_jobs = [
            job for job in self.jobs.values()
            if job.status in [JobStatus.PENDING, JobStatus.UPLOADING, JobStatus.TRAINING]
        ]

        logger.info(f"Active jobs: {len(active_jobs)}")

        for job in active_jobs:
            try:
                self.check_job_status(job.job_id)
                time.sleep(1)  # Rate limit
            except Exception as e:
                logger.error(f"Error checking {job.job_id}: {e}")

        # Summary
        summary = {
            "total_jobs": len(self.jobs),
            "by_status": self._count_by_status(),
            "by_provider": self._count_by_provider(),
            "by_agent": self._count_by_agent(),
            "completed_models": [
                job.fine_tuned_model
                for job in self.jobs.values()
                if job.fine_tuned_model
            ]
        }

        logger.info(f"Job summary: {summary}")

        return summary

    def _count_by_status(self) -> Dict[str, int]:
        """Count jobs by status."""
        counts = {}
        for job in self.jobs.values():
            status = job.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts

    def _count_by_provider(self) -> Dict[str, int]:
        """Count jobs by provider."""
        counts = {}
        for job in self.jobs.values():
            provider = job.provider.value
            counts[provider] = counts.get(provider, 0) + 1
        return counts

    def _count_by_agent(self) -> Dict[str, int]:
        """Count jobs by agent role."""
        counts = {}
        for job in self.jobs.values():
            agent = job.agent_role
            counts[agent] = counts.get(agent, 0) + 1
        return counts

    def get_completed_models(self) -> List[Dict[str, str]]:
        """Get all successfully fine-tuned models."""
        models = []

        for job in self.jobs.values():
            if job.status == JobStatus.COMPLETED and job.fine_tuned_model:
                models.append({
                    "agent_role": job.agent_role,
                    "provider": job.provider.value,
                    "model_id": job.fine_tuned_model,
                    "base_model": job.model_base,
                    "completed_at": job.created_at
                })

        return models


def main():
    """Example usage."""
    orchestrator = TrainingOrchestrator()

    # Submit OpenAI job
    # job = orchestrator.submit_openai_job(
    #     agent_role="builder",
    #     training_file=Path("./training_data/fine_tuning/openai/train_openai.jsonl"),
    #     validation_file=Path("./training_data/fine_tuning/openai/val_openai.jsonl"),
    #     model_base="gpt-3.5-turbo",
    #     n_epochs=3
    # )
    # print(f"Submitted job: {job.job_id}")

    # Monitor jobs
    summary = orchestrator.monitor_all_jobs()
    print(f"Jobs summary: {summary}")

    # Get completed models
    models = orchestrator.get_completed_models()
    print(f"Completed models: {models}")


if __name__ == "__main__":
    main()
