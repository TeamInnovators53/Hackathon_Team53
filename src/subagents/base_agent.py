"""
Base class for all domain sub-agents in Key Privilege Multi-Agent System.
Hackathon Team 53 - Team Innovators.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from src.models import CustomerProfile, AgentResponse


class BaseSubAgent(ABC):
    """
    Abstract interface for specialized conversational sub-agents.
    """

    def __init__(self, agent_id: str, title: str, description: str):
        self.agent_id = agent_id
        self.title = title
        self.description = description

    @abstractmethod
    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        """
        Returns confidence score [0.0 to 1.0] for handling the user query.
        """
        pass

    @abstractmethod
    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Executes sub-agent domain logic and returns rich AgentResponse.
        """
        pass
