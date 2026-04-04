"""
PM Agent Suite — importable agents for program management.

Quick start:
    from agents import StatusSentinel, RiskRadar, StakeholderScribe
    from agents import DecisionLogger, DependencyDetective, DeliveryCoach

    agent = StatusSentinel()
    response = agent.chat("Give me a RAG status report for Program Alpha.")
    print(response)
"""

from .base_agent import BaseAgent
from .agents import (
    StatusSentinel,
    RiskRadar,
    StakeholderScribe,
    DecisionLogger,
    DependencyDetective,
    DeliveryCoach,
)

ALL_AGENTS = [
    StatusSentinel,
    RiskRadar,
    StakeholderScribe,
    DecisionLogger,
    DependencyDetective,
    DeliveryCoach,
]

__all__ = [
    "BaseAgent",
    "StatusSentinel",
    "RiskRadar",
    "StakeholderScribe",
    "DecisionLogger",
    "DependencyDetective",
    "DeliveryCoach",
    "ALL_AGENTS",
]
