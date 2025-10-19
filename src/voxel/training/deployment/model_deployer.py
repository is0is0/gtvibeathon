"""
Model Deployer - Deploys fine-tuned models into production.
Integrates fine-tuned models into the Voxel agent system.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DeployedModel:
    """Represents a deployed fine-tuned model."""
    model_id: str
    provider: str  # anthropic, openai
    agent_role: str  # builder, texture, render, etc.
    deployed_at: str
    status: str  # active, inactive, testing
    performance_metrics: Dict[str, float]
    rollback_model: Optional[str] = None  # Previous model for rollback


class ModelDeployer:
    """
    Deploys fine-tuned models into the Voxel production system.
    Manages model versioning, A/B testing, and rollbacks.
    """

    def __init__(
        self,
        config_path: Path = Path("./src/voxel/config/deployed_models.json")
    ):
        """
        Initialize deployer.

        Args:
            config_path: Path to save deployed model configuration
        """
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        self.deployed_models: Dict[str, DeployedModel] = {}
        self._load_config()

        logger.info(f"ModelDeployer initialized ({len(self.deployed_models)} models deployed)")

    def _load_config(self):
        """Load deployed model configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for model_data in data:
                        model = DeployedModel(**model_data)
                        self.deployed_models[model.agent_role] = model
                logger.info(f"Loaded {len(self.deployed_models)} deployed models")
            except Exception as e:
                logger.warning(f"Could not load config: {e}")

    def _save_config(self):
        """Save deployed model configuration."""
        models_list = [
            {
                "model_id": m.model_id,
                "provider": m.provider,
                "agent_role": m.agent_role,
                "deployed_at": m.deployed_at,
                "status": m.status,
                "performance_metrics": m.performance_metrics,
                "rollback_model": m.rollback_model
            }
            for m in self.deployed_models.values()
        ]

        with open(self.config_path, 'w') as f:
            json.dump(models_list, f, indent=2)

        logger.info(f"Saved {len(self.deployed_models)} deployed models")

    def deploy_model(
        self,
        model_id: str,
        provider: str,
        agent_role: str,
        performance_metrics: Optional[Dict[str, float]] = None
    ) -> DeployedModel:
        """
        Deploy a fine-tuned model to production.

        Args:
            model_id: Fine-tuned model ID
            provider: Provider (anthropic/openai)
            agent_role: Agent role (builder, texture, etc.)
            performance_metrics: Optional evaluation metrics

        Returns:
            DeployedModel instance
        """
        logger.info(f"Deploying model {model_id} for {agent_role}...")

        # Save current model as rollback if exists
        rollback_model = None
        if agent_role in self.deployed_models:
            current = self.deployed_models[agent_role]
            rollback_model = current.model_id
            logger.info(f"Saving rollback: {rollback_model}")

        # Create deployment
        deployed = DeployedModel(
            model_id=model_id,
            provider=provider,
            agent_role=agent_role,
            deployed_at=datetime.now().isoformat(),
            status="active",
            performance_metrics=performance_metrics or {},
            rollback_model=rollback_model
        )

        self.deployed_models[agent_role] = deployed
        self._save_config()

        # Update agent configuration
        self._update_agent_config(deployed)

        logger.info(f"Deployed {model_id} for {agent_role}")

        return deployed

    def _update_agent_config(self, deployed: DeployedModel):
        """Update agent configuration to use new model."""
        # Update the AgentConfig to use fine-tuned model
        agent_config_path = Path("./src/voxel/core/config.py")

        logger.info(f"Updating agent config for {deployed.agent_role} to use {deployed.model_id}")

        # In production, would modify the config file or environment variables
        # For now, this is a placeholder

        # Example: Update .env file
        env_path = Path("./.env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()

            # Update or add model override
            key = f"{deployed.agent_role.upper()}_MODEL"
            value = deployed.model_id

            updated = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    updated = True
                    break

            if not updated:
                lines.append(f"{key}={value}\n")

            with open(env_path, 'w') as f:
                f.writelines(lines)

            logger.info(f"Updated .env with {key}={value}")

    def rollback_model(self, agent_role: str) -> Optional[DeployedModel]:
        """
        Rollback to previous model version.

        Args:
            agent_role: Agent role to rollback

        Returns:
            Rolled back DeployedModel or None
        """
        if agent_role not in self.deployed_models:
            logger.error(f"No deployment found for {agent_role}")
            return None

        current = self.deployed_models[agent_role]

        if not current.rollback_model:
            logger.error(f"No rollback model available for {agent_role}")
            return None

        logger.info(f"Rolling back {agent_role} from {current.model_id} to {current.rollback_model}")

        # Swap models
        rollback_id = current.rollback_model
        current.rollback_model = current.model_id
        current.model_id = rollback_id
        current.deployed_at = datetime.now().isoformat()
        current.status = "active"

        self._save_config()
        self._update_agent_config(current)

        logger.info(f"Rollback complete for {agent_role}")

        return current

    def deactivate_model(self, agent_role: str):
        """
        Deactivate a deployed model (use base model instead).

        Args:
            agent_role: Agent role to deactivate
        """
        if agent_role not in self.deployed_models:
            logger.warning(f"No deployment found for {agent_role}")
            return

        self.deployed_models[agent_role].status = "inactive"
        self._save_config()

        logger.info(f"Deactivated fine-tuned model for {agent_role}")

    def get_active_models(self) -> List[DeployedModel]:
        """Get all active deployed models."""
        return [
            model for model in self.deployed_models.values()
            if model.status == "active"
        ]

    def get_deployment_status(self) -> Dict[str, Any]:
        """Get overall deployment status."""
        active = [m for m in self.deployed_models.values() if m.status == "active"]

        return {
            "total_deployments": len(self.deployed_models),
            "active": len(active),
            "inactive": len(self.deployed_models) - len(active),
            "by_provider": self._count_by_provider(),
            "by_agent": self._count_by_agent(),
            "models": [
                {
                    "agent_role": m.agent_role,
                    "model_id": m.model_id,
                    "provider": m.provider,
                    "status": m.status,
                    "deployed_at": m.deployed_at
                }
                for m in self.deployed_models.values()
            ]
        }

    def _count_by_provider(self) -> Dict[str, int]:
        """Count deployments by provider."""
        counts = {}
        for model in self.deployed_models.values():
            counts[model.provider] = counts.get(model.provider, 0) + 1
        return counts

    def _count_by_agent(self) -> Dict[str, int]:
        """Count deployments by agent role."""
        counts = {}
        for model in self.deployed_models.values():
            counts[model.agent_role] = counts.get(model.agent_role, 0) + 1
        return counts

    def setup_ab_test(
        self,
        agent_role: str,
        model_a: str,
        model_b: str,
        traffic_split: float = 0.5
    ) -> Dict[str, Any]:
        """
        Set up A/B test between two models.

        Args:
            agent_role: Agent role
            model_a: First model ID
            model_b: Second model ID
            traffic_split: Percentage of traffic to model_a (0.0-1.0)

        Returns:
            A/B test configuration
        """
        logger.info(f"Setting up A/B test for {agent_role}: {traffic_split*100}% to {model_a}")

        ab_config = {
            "agent_role": agent_role,
            "model_a": model_a,
            "model_b": model_b,
            "traffic_split": traffic_split,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }

        # Save A/B test config
        ab_config_path = self.config_path.parent / "ab_tests.json"
        ab_tests = []

        if ab_config_path.exists():
            with open(ab_config_path, 'r') as f:
                ab_tests = json.load(f)

        ab_tests.append(ab_config)

        with open(ab_config_path, 'w') as f:
            json.dump(ab_tests, f, indent=2)

        logger.info("A/B test configured")

        return ab_config


def main():
    """Example usage."""
    deployer = ModelDeployer()

    # Deploy a model
    # deployment = deployer.deploy_model(
    #     model_id="ft:gpt-3.5-turbo:custom-builder:abc123",
    #     provider="openai",
    #     agent_role="builder",
    #     performance_metrics={"overall_average": 0.85, "pass_rate": 0.92}
    # )
    # print(f"Deployed: {deployment}")

    # Get status
    status = deployer.get_deployment_status()
    print(f"Deployment status: {status}")

    # Rollback if needed
    # deployer.rollback_model("builder")


if __name__ == "__main__":
    main()
