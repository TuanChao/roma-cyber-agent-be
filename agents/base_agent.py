"""
Base Agent class - All agents inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
import asyncio


class BaseAgent(ABC):
    """Base class for all security monitoring agents"""

    def __init__(self, name: str, agent_id: Optional[str] = None):
        self.name = name
        self.agent_id = agent_id or f"{name}_{datetime.now().timestamp()}"
        self.status = "initialized"
        self.is_running = False
        self.start_time = None
        self.metrics = {
            "events_processed": 0,
            "alerts_generated": 0,
            "errors": 0
        }

        logger.info(f"🤖 Agent '{self.name}' initialized with ID: {self.agent_id}")

    @abstractmethod
    async def start(self) -> None:
        """Start the agent"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the agent"""
        pass

    @abstractmethod
    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single event"""
        pass

    async def _set_status(self, status: str) -> None:
        """Update agent status"""
        self.status = status
        logger.debug(f"Agent {self.name} status: {status}")

    async def _increment_metric(self, metric: str, value: int = 1) -> None:
        """Increment a metric counter"""
        if metric in self.metrics:
            self.metrics[metric] += value

    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "metrics": self.metrics
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "healthy": self.is_running and self.status != "error",
            "status": self.status,
            "timestamp": datetime.now().isoformat()
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', status='{self.status}')>"
