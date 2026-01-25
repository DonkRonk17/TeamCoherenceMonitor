#!/usr/bin/env python3
"""
TeamCoherenceMonitor - Real-Time Coordination Health Dashboard for Multi-Agent Teams

Provides live visibility into team coordination health with metrics tracking,
early warnings, and a unified coherence score (0-100). Designed to prevent
coordination failures before they happen during high-velocity group conversations.

Key Features:
- Live response latency tracking per agent
- @mention acknowledgment rate monitoring
- Context fidelity scoring over time
- Early warning system with configurable thresholds
- Team coherence score (0-100) - single metric for coordination health
- Integration hub for coordination tools (MentionGuard, LiveAudit, PostMortem)

Author: ATLAS (Team Brain)
For: Logan Smith / Metaphy LLC
Version: 1.0
Date: January 25, 2026
License: MIT
"""

import argparse
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from statistics import mean, stdev


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AgentStatus:
    """Tracks current status for a single agent."""
    name: str
    last_seen: Optional[datetime] = None
    is_active: bool = False
    response_latencies: List[float] = field(default_factory=list)
    mentions_received: int = 0
    mentions_acknowledged: int = 0
    correct_claims: int = 0
    total_claims: int = 0
    messages_sent: int = 0
    errors_detected: int = 0
    
    def ack_rate(self) -> float:
        """Calculate mention acknowledgment rate (0-100)."""
        if self.mentions_received == 0:
            return 100.0
        return (self.mentions_acknowledged / self.mentions_received) * 100
    
    def avg_latency(self) -> float:
        """Calculate average response latency in seconds."""
        if not self.response_latencies:
            return 0.0
        return mean(self.response_latencies)
    
    def context_fidelity(self) -> float:
        """Calculate context fidelity (claim accuracy) 0-100."""
        if self.total_claims == 0:
            return 100.0
        return (self.correct_claims / self.total_claims) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active,
            'response_latencies': self.response_latencies[-100:],  # Keep last 100
            'mentions_received': self.mentions_received,
            'mentions_acknowledged': self.mentions_acknowledged,
            'correct_claims': self.correct_claims,
            'total_claims': self.total_claims,
            'messages_sent': self.messages_sent,
            'errors_detected': self.errors_detected,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentStatus':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            last_seen=datetime.fromisoformat(data['last_seen']) if data.get('last_seen') else None,
            is_active=data.get('is_active', False),
            response_latencies=data.get('response_latencies', []),
            mentions_received=data.get('mentions_received', 0),
            mentions_acknowledged=data.get('mentions_acknowledged', 0),
            correct_claims=data.get('correct_claims', 0),
            total_claims=data.get('total_claims', 0),
            messages_sent=data.get('messages_sent', 0),
            errors_detected=data.get('errors_detected', 0),
        )


@dataclass
class Alert:
    """Represents a coordination alert."""
    timestamp: datetime
    severity: str  # INFO, WARNING, CRITICAL
    agent: Optional[str]
    metric: str
    message: str
    value: float
    threshold: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity,
            'agent': self.agent,
            'metric': self.metric,
            'message': self.message,
            'value': self.value,
            'threshold': self.threshold,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            severity=data['severity'],
            agent=data.get('agent'),
            metric=data['metric'],
            message=data['message'],
            value=data['value'],
            threshold=data['threshold'],
        )


@dataclass
class CoherenceSnapshot:
    """Point-in-time snapshot of team coherence."""
    timestamp: datetime
    overall_score: float
    agent_scores: Dict[str, float]
    active_agents: int
    total_agents: int
    alerts_active: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_score': self.overall_score,
            'agent_scores': self.agent_scores,
            'active_agents': self.active_agents,
            'total_agents': self.total_agents,
            'alerts_active': self.alerts_active,
        }


# =============================================================================
# THRESHOLDS CONFIGURATION
# =============================================================================

@dataclass
class Thresholds:
    """Configurable thresholds for alerts and scoring."""
    # Latency thresholds (seconds)
    latency_warning: float = 30.0
    latency_critical: float = 60.0
    
    # Acknowledgment rate thresholds (percentage)
    ack_rate_warning: float = 80.0
    ack_rate_critical: float = 60.0
    
    # Context fidelity thresholds (percentage)
    fidelity_warning: float = 90.0
    fidelity_critical: float = 70.0
    
    # Activity thresholds (seconds since last seen)
    inactive_warning: float = 120.0
    inactive_critical: float = 300.0
    
    # Team coherence thresholds
    coherence_warning: float = 75.0
    coherence_critical: float = 50.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Thresholds':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# COHERENCE SCORER
# =============================================================================

class CoherenceScorer:
    """
    Calculates team coherence scores using weighted metrics.
    
    Scoring weights:
    - Acknowledgment Rate: 30%
    - Response Latency: 25%
    - Context Fidelity: 30%
    - Activity Status: 15%
    """
    
    WEIGHTS = {
        'ack_rate': 0.30,
        'latency': 0.25,
        'fidelity': 0.30,
        'activity': 0.15,
    }
    
    def __init__(self, thresholds: Thresholds):
        """Initialize with thresholds."""
        self.thresholds = thresholds
    
    def score_latency(self, avg_latency: float) -> float:
        """
        Score latency (0-100, lower latency = higher score).
        
        Args:
            avg_latency: Average response latency in seconds
            
        Returns:
            Score from 0-100
        """
        if avg_latency <= 0:
            return 100.0
        if avg_latency >= self.thresholds.latency_critical:
            return 0.0
        if avg_latency <= 5.0:  # Excellent
            return 100.0
        
        # Linear scale from 5s (100) to critical (0)
        range_size = self.thresholds.latency_critical - 5.0
        score = 100 - ((avg_latency - 5.0) / range_size * 100)
        return max(0.0, min(100.0, score))
    
    def score_activity(self, seconds_since_seen: float) -> float:
        """
        Score activity status (0-100, recent = higher score).
        
        Args:
            seconds_since_seen: Seconds since last activity
            
        Returns:
            Score from 0-100
        """
        if seconds_since_seen <= 0:
            return 100.0
        if seconds_since_seen >= self.thresholds.inactive_critical:
            return 0.0
        if seconds_since_seen <= 30:  # Active within 30s
            return 100.0
        
        # Linear scale from 30s (100) to critical (0)
        range_size = self.thresholds.inactive_critical - 30.0
        score = 100 - ((seconds_since_seen - 30.0) / range_size * 100)
        return max(0.0, min(100.0, score))
    
    def calculate_agent_score(self, agent: AgentStatus) -> float:
        """
        Calculate coherence score for a single agent.
        
        Args:
            agent: Agent status object
            
        Returns:
            Weighted score from 0-100
        """
        # Acknowledgment rate (already 0-100)
        ack_score = agent.ack_rate()
        
        # Latency score
        latency_score = self.score_latency(agent.avg_latency())
        
        # Context fidelity (already 0-100)
        fidelity_score = agent.context_fidelity()
        
        # Activity score
        if agent.last_seen:
            seconds_since = (datetime.now() - agent.last_seen).total_seconds()
        else:
            seconds_since = self.thresholds.inactive_critical  # Unknown = inactive
        activity_score = self.score_activity(seconds_since)
        
        # Weighted average
        total = (
            ack_score * self.WEIGHTS['ack_rate'] +
            latency_score * self.WEIGHTS['latency'] +
            fidelity_score * self.WEIGHTS['fidelity'] +
            activity_score * self.WEIGHTS['activity']
        )
        
        return round(total, 1)
    
    def calculate_team_score(self, agents: Dict[str, AgentStatus]) -> Tuple[float, Dict[str, float]]:
        """
        Calculate team coherence score.
        
        Args:
            agents: Dictionary of agent statuses
            
        Returns:
            Tuple of (overall_score, agent_scores_dict)
        """
        if not agents:
            return 100.0, {}
        
        agent_scores = {}
        for name, agent in agents.items():
            agent_scores[name] = self.calculate_agent_score(agent)
        
        # Team score is average of agent scores
        overall = mean(agent_scores.values()) if agent_scores else 100.0
        
        return round(overall, 1), agent_scores


# =============================================================================
# ALERT SYSTEM
# =============================================================================

class AlertSystem:
    """
    Monitors metrics and generates alerts when thresholds are crossed.
    """
    
    def __init__(self, thresholds: Thresholds):
        """Initialize with thresholds."""
        self.thresholds = thresholds
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
    
    def check_agent(self, agent: AgentStatus) -> List[Alert]:
        """
        Check an agent's metrics and generate alerts if needed.
        
        Args:
            agent: Agent status to check
            
        Returns:
            List of generated alerts
        """
        alerts = []
        now = datetime.now()
        
        # Check acknowledgment rate
        ack_rate = agent.ack_rate()
        if agent.mentions_received > 0:
            if ack_rate < self.thresholds.ack_rate_critical:
                alerts.append(Alert(
                    timestamp=now,
                    severity='CRITICAL',
                    agent=agent.name,
                    metric='ack_rate',
                    message=f'{agent.name} acknowledgment rate critically low',
                    value=ack_rate,
                    threshold=self.thresholds.ack_rate_critical,
                ))
            elif ack_rate < self.thresholds.ack_rate_warning:
                alerts.append(Alert(
                    timestamp=now,
                    severity='WARNING',
                    agent=agent.name,
                    metric='ack_rate',
                    message=f'{agent.name} acknowledgment rate below threshold',
                    value=ack_rate,
                    threshold=self.thresholds.ack_rate_warning,
                ))
        
        # Check latency
        avg_latency = agent.avg_latency()
        if avg_latency > 0:
            if avg_latency >= self.thresholds.latency_critical:
                alerts.append(Alert(
                    timestamp=now,
                    severity='CRITICAL',
                    agent=agent.name,
                    metric='latency',
                    message=f'{agent.name} response latency critically high',
                    value=avg_latency,
                    threshold=self.thresholds.latency_critical,
                ))
            elif avg_latency >= self.thresholds.latency_warning:
                alerts.append(Alert(
                    timestamp=now,
                    severity='WARNING',
                    agent=agent.name,
                    metric='latency',
                    message=f'{agent.name} response latency high',
                    value=avg_latency,
                    threshold=self.thresholds.latency_warning,
                ))
        
        # Check context fidelity
        fidelity = agent.context_fidelity()
        if agent.total_claims > 0:
            if fidelity < self.thresholds.fidelity_critical:
                alerts.append(Alert(
                    timestamp=now,
                    severity='CRITICAL',
                    agent=agent.name,
                    metric='fidelity',
                    message=f'{agent.name} context fidelity critically low',
                    value=fidelity,
                    threshold=self.thresholds.fidelity_critical,
                ))
            elif fidelity < self.thresholds.fidelity_warning:
                alerts.append(Alert(
                    timestamp=now,
                    severity='WARNING',
                    agent=agent.name,
                    metric='fidelity',
                    message=f'{agent.name} context fidelity below threshold',
                    value=fidelity,
                    threshold=self.thresholds.fidelity_warning,
                ))
        
        # Check activity
        if agent.last_seen:
            seconds_inactive = (now - agent.last_seen).total_seconds()
            if seconds_inactive >= self.thresholds.inactive_critical:
                alerts.append(Alert(
                    timestamp=now,
                    severity='CRITICAL',
                    agent=agent.name,
                    metric='activity',
                    message=f'{agent.name} has been inactive for {seconds_inactive:.0f}s',
                    value=seconds_inactive,
                    threshold=self.thresholds.inactive_critical,
                ))
            elif seconds_inactive >= self.thresholds.inactive_warning:
                alerts.append(Alert(
                    timestamp=now,
                    severity='WARNING',
                    agent=agent.name,
                    metric='activity',
                    message=f'{agent.name} inactive for {seconds_inactive:.0f}s',
                    value=seconds_inactive,
                    threshold=self.thresholds.inactive_warning,
                ))
        
        return alerts
    
    def check_team_coherence(self, score: float) -> Optional[Alert]:
        """
        Check team coherence score and generate alert if needed.
        
        Args:
            score: Team coherence score (0-100)
            
        Returns:
            Alert if threshold crossed, None otherwise
        """
        now = datetime.now()
        
        if score < self.thresholds.coherence_critical:
            return Alert(
                timestamp=now,
                severity='CRITICAL',
                agent=None,
                metric='coherence',
                message=f'Team coherence critically low: {score:.1f}',
                value=score,
                threshold=self.thresholds.coherence_critical,
            )
        elif score < self.thresholds.coherence_warning:
            return Alert(
                timestamp=now,
                severity='WARNING',
                agent=None,
                metric='coherence',
                message=f'Team coherence below threshold: {score:.1f}',
                value=score,
                threshold=self.thresholds.coherence_warning,
            )
        
        return None
    
    def process_alerts(self, alerts: List[Alert]) -> None:
        """
        Process new alerts (add to active/history).
        
        Args:
            alerts: List of new alerts
        """
        for alert in alerts:
            self.active_alerts.append(alert)
            self.alert_history.append(alert)
        
        # Keep only recent active alerts (last hour)
        cutoff = datetime.now() - timedelta(hours=1)
        self.active_alerts = [a for a in self.active_alerts if a.timestamp > cutoff]
        
        # Keep history limited to 1000 entries
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Alert]:
        """
        Get active alerts, optionally filtered by severity.
        
        Args:
            severity: Optional severity filter (INFO, WARNING, CRITICAL)
            
        Returns:
            List of matching alerts
        """
        if severity:
            return [a for a in self.active_alerts if a.severity == severity]
        return self.active_alerts.copy()
    
    def clear_alerts(self, agent: Optional[str] = None, metric: Optional[str] = None) -> int:
        """
        Clear active alerts matching criteria.
        
        Args:
            agent: Optional agent name filter
            metric: Optional metric filter
            
        Returns:
            Number of alerts cleared
        """
        before = len(self.active_alerts)
        self.active_alerts = [
            a for a in self.active_alerts
            if (agent is None or a.agent != agent) and
               (metric is None or a.metric != metric)
        ]
        return before - len(self.active_alerts)


# =============================================================================
# MAIN CLASS
# =============================================================================

class TeamCoherenceMonitor:
    """
    Real-time coordination health dashboard for multi-agent teams.
    
    Provides live visibility into team coordination with metrics tracking,
    early warnings, and a unified coherence score.
    
    Example:
        >>> monitor = TeamCoherenceMonitor()
        >>> monitor.register_agent("FORGE")
        >>> monitor.record_mention("FORGE", acknowledged=True)
        >>> monitor.record_response("FORGE", latency=2.5)
        >>> score = monitor.get_coherence_score()
        >>> print(f"Team coherence: {score}")
    """
    
    DEFAULT_DATA_DIR = Path.home() / ".teamcoherencemonitor"
    
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        thresholds: Optional[Thresholds] = None,
        auto_load: bool = True,
    ):
        """
        Initialize the monitor.
        
        Args:
            data_dir: Directory for data storage (default: ~/.teamcoherencemonitor)
            thresholds: Custom thresholds (default: Thresholds())
            auto_load: Whether to auto-load existing data (default: True)
        """
        self.data_dir = Path(data_dir) if data_dir else self.DEFAULT_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.thresholds = thresholds or Thresholds()
        self.agents: Dict[str, AgentStatus] = {}
        self.scorer = CoherenceScorer(self.thresholds)
        self.alerts = AlertSystem(self.thresholds)
        self.snapshots: List[CoherenceSnapshot] = []
        self.session_start = datetime.now()
        
        if auto_load:
            self._load_data()
    
    # -------------------------------------------------------------------------
    # Agent Management
    # -------------------------------------------------------------------------
    
    def register_agent(self, name: str) -> AgentStatus:
        """
        Register an agent for monitoring.
        
        Args:
            name: Agent name (e.g., "FORGE", "ATLAS")
            
        Returns:
            Agent status object
        """
        name = name.upper()
        if name not in self.agents:
            self.agents[name] = AgentStatus(name=name)
        return self.agents[name]
    
    def unregister_agent(self, name: str) -> bool:
        """
        Remove an agent from monitoring.
        
        Args:
            name: Agent name
            
        Returns:
            True if removed, False if not found
        """
        name = name.upper()
        if name in self.agents:
            del self.agents[name]
            return True
        return False
    
    def get_agent(self, name: str) -> Optional[AgentStatus]:
        """
        Get agent status by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent status or None if not found
        """
        return self.agents.get(name.upper())
    
    def list_agents(self) -> List[str]:
        """Get list of registered agent names."""
        return list(self.agents.keys())
    
    # -------------------------------------------------------------------------
    # Metric Recording
    # -------------------------------------------------------------------------
    
    def record_activity(self, agent_name: str) -> None:
        """
        Record agent activity (update last_seen).
        
        Args:
            agent_name: Agent name
        """
        agent = self.register_agent(agent_name)
        agent.last_seen = datetime.now()
        agent.is_active = True
    
    def record_mention(self, agent_name: str, acknowledged: bool = False) -> None:
        """
        Record a mention event for an agent.
        
        Args:
            agent_name: Agent that was mentioned
            acknowledged: Whether the mention was acknowledged
        """
        agent = self.register_agent(agent_name)
        agent.mentions_received += 1
        if acknowledged:
            agent.mentions_acknowledged += 1
    
    def record_acknowledgment(self, agent_name: str) -> None:
        """
        Record that an agent acknowledged a previous mention.
        
        Args:
            agent_name: Agent name
        """
        agent = self.register_agent(agent_name)
        agent.mentions_acknowledged += 1
    
    def record_response(self, agent_name: str, latency: float) -> None:
        """
        Record a response latency for an agent.
        
        Args:
            agent_name: Agent name
            latency: Response latency in seconds
        """
        agent = self.register_agent(agent_name)
        agent.response_latencies.append(latency)
        agent.last_seen = datetime.now()
        agent.messages_sent += 1
        
        # Keep only last 100 latencies
        if len(agent.response_latencies) > 100:
            agent.response_latencies = agent.response_latencies[-100:]
    
    def record_claim(self, agent_name: str, correct: bool) -> None:
        """
        Record a claim accuracy event (for context fidelity).
        
        Args:
            agent_name: Agent that made the claim
            correct: Whether the claim was accurate
        """
        agent = self.register_agent(agent_name)
        agent.total_claims += 1
        if correct:
            agent.correct_claims += 1
    
    def record_error(self, agent_name: str) -> None:
        """
        Record an error detected for an agent.
        
        Args:
            agent_name: Agent name
        """
        agent = self.register_agent(agent_name)
        agent.errors_detected += 1
    
    # -------------------------------------------------------------------------
    # Scoring & Analysis
    # -------------------------------------------------------------------------
    
    def get_coherence_score(self) -> float:
        """
        Get current team coherence score (0-100).
        
        Returns:
            Team coherence score
        """
        score, _ = self.scorer.calculate_team_score(self.agents)
        return score
    
    def get_agent_scores(self) -> Dict[str, float]:
        """
        Get coherence scores for all agents.
        
        Returns:
            Dictionary of agent_name -> score
        """
        _, scores = self.scorer.calculate_team_score(self.agents)
        return scores
    
    def get_agent_metrics(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metrics for an agent.
        
        Args:
            agent_name: Agent name
            
        Returns:
            Metrics dictionary or None if agent not found
        """
        agent = self.get_agent(agent_name)
        if not agent:
            return None
        
        return {
            'name': agent.name,
            'ack_rate': round(agent.ack_rate(), 1),
            'avg_latency': round(agent.avg_latency(), 2),
            'context_fidelity': round(agent.context_fidelity(), 1),
            'mentions_received': agent.mentions_received,
            'mentions_acknowledged': agent.mentions_acknowledged,
            'messages_sent': agent.messages_sent,
            'errors_detected': agent.errors_detected,
            'is_active': agent.is_active,
            'last_seen': agent.last_seen.isoformat() if agent.last_seen else None,
            'coherence_score': self.scorer.calculate_agent_score(agent),
        }
    
    def take_snapshot(self) -> CoherenceSnapshot:
        """
        Take a point-in-time snapshot of team coherence.
        
        Returns:
            Coherence snapshot
        """
        score, agent_scores = self.scorer.calculate_team_score(self.agents)
        
        active_count = sum(1 for a in self.agents.values() if a.is_active)
        
        snapshot = CoherenceSnapshot(
            timestamp=datetime.now(),
            overall_score=score,
            agent_scores=agent_scores,
            active_agents=active_count,
            total_agents=len(self.agents),
            alerts_active=len(self.alerts.active_alerts),
        )
        
        self.snapshots.append(snapshot)
        
        # Keep last 1000 snapshots
        if len(self.snapshots) > 1000:
            self.snapshots = self.snapshots[-1000:]
        
        return snapshot
    
    def get_trend(self, minutes: int = 30) -> Dict[str, Any]:
        """
        Get coherence trend over time.
        
        Args:
            minutes: Time window in minutes (default: 30)
            
        Returns:
            Trend analysis dictionary
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [s for s in self.snapshots if s.timestamp > cutoff]
        
        if len(recent) < 2:
            return {
                'trend': 'STABLE',
                'change': 0.0,
                'samples': len(recent),
                'min_score': self.get_coherence_score(),
                'max_score': self.get_coherence_score(),
                'avg_score': self.get_coherence_score(),
            }
        
        scores = [s.overall_score for s in recent]
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        avg_first = mean(first_half)
        avg_second = mean(second_half)
        change = avg_second - avg_first
        
        if change > 5:
            trend = 'IMPROVING'
        elif change < -5:
            trend = 'DEGRADING'
        else:
            trend = 'STABLE'
        
        return {
            'trend': trend,
            'change': round(change, 1),
            'samples': len(recent),
            'min_score': min(scores),
            'max_score': max(scores),
            'avg_score': round(mean(scores), 1),
        }
    
    # -------------------------------------------------------------------------
    # Alert Management
    # -------------------------------------------------------------------------
    
    def check_all_alerts(self) -> List[Alert]:
        """
        Check all agents and team coherence for alerts.
        
        Returns:
            List of new alerts generated
        """
        new_alerts = []
        
        # Check each agent
        for agent in self.agents.values():
            agent_alerts = self.alerts.check_agent(agent)
            new_alerts.extend(agent_alerts)
        
        # Check team coherence
        score = self.get_coherence_score()
        coherence_alert = self.alerts.check_team_coherence(score)
        if coherence_alert:
            new_alerts.append(coherence_alert)
        
        # Process alerts
        self.alerts.process_alerts(new_alerts)
        
        return new_alerts
    
    def get_alerts(self, severity: Optional[str] = None) -> List[Alert]:
        """
        Get active alerts.
        
        Args:
            severity: Optional filter (INFO, WARNING, CRITICAL)
            
        Returns:
            List of active alerts
        """
        return self.alerts.get_active_alerts(severity)
    
    def clear_alerts(self, agent: Optional[str] = None) -> int:
        """
        Clear active alerts.
        
        Args:
            agent: Optional agent name to filter
            
        Returns:
            Number of alerts cleared
        """
        return self.alerts.clear_alerts(agent=agent)
    
    # -------------------------------------------------------------------------
    # Dashboard / Display
    # -------------------------------------------------------------------------
    
    def format_dashboard(self, compact: bool = False) -> str:
        """
        Format a text dashboard of current status.
        
        Args:
            compact: If True, show compact version
            
        Returns:
            Formatted dashboard string
        """
        lines = []
        
        # Header
        score = self.get_coherence_score()
        status = "[OK]" if score >= 75 else "[!]" if score >= 50 else "[X]"
        
        lines.append("=" * 70)
        lines.append(f"TEAM COHERENCE MONITOR - Score: {score:.1f}/100 {status}")
        lines.append("=" * 70)
        
        if compact:
            # Compact view
            lines.append("")
            lines.append(f"Agents: {len(self.agents)} | Active Alerts: {len(self.alerts.active_alerts)}")
            lines.append("")
            
            agent_scores = self.get_agent_scores()
            for name, agent_score in sorted(agent_scores.items()):
                agent = self.agents[name]
                status_icon = "[OK]" if agent_score >= 75 else "[!]" if agent_score >= 50 else "[X]"
                lines.append(f"  {name:12} {agent_score:5.1f} {status_icon}  ACK:{agent.ack_rate():5.1f}%  LAT:{agent.avg_latency():5.1f}s")
        else:
            # Full view
            lines.append("")
            lines.append("AGENT STATUS")
            lines.append("-" * 70)
            lines.append(f"{'Agent':<12} {'Score':>6} {'ACK%':>6} {'Latency':>8} {'Fidelity':>8} {'Status':>8}")
            lines.append("-" * 70)
            
            agent_scores = self.get_agent_scores()
            for name, agent_score in sorted(agent_scores.items()):
                agent = self.agents[name]
                status = "Active" if agent.is_active else "Inactive"
                lines.append(
                    f"{name:<12} {agent_score:>6.1f} {agent.ack_rate():>5.1f}% "
                    f"{agent.avg_latency():>7.1f}s {agent.context_fidelity():>7.1f}% {status:>8}"
                )
            
            lines.append("")
            lines.append("ALERTS")
            lines.append("-" * 70)
            
            alerts = self.get_alerts()
            if alerts:
                for alert in alerts[-10:]:  # Last 10
                    icon = "[X]" if alert.severity == "CRITICAL" else "[!]" if alert.severity == "WARNING" else "[i]"
                    lines.append(f"{icon} [{alert.agent or 'TEAM'}] {alert.message}")
            else:
                lines.append("No active alerts")
            
            # Trend
            trend = self.get_trend()
            lines.append("")
            lines.append(f"TREND (30min): {trend['trend']} ({trend['change']:+.1f})")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    # -------------------------------------------------------------------------
    # Integration Hub
    # -------------------------------------------------------------------------
    
    def import_mentionguard_data(self, data: Dict[str, Any]) -> int:
        """
        Import data from MentionGuard tool.
        
        Args:
            data: MentionGuard export data
            
        Returns:
            Number of events imported
        """
        count = 0
        for event in data.get('events', []):
            agent = event.get('agent')
            if agent:
                self.record_mention(agent, acknowledged=event.get('acknowledged', False))
                count += 1
        return count
    
    def import_liveaudit_data(self, data: Dict[str, Any]) -> int:
        """
        Import data from LiveAudit tool.
        
        Args:
            data: LiveAudit export data
            
        Returns:
            Number of events imported
        """
        count = 0
        for issue in data.get('issues', []):
            agent = issue.get('agent')
            if agent:
                # False claims decrease fidelity
                self.record_claim(agent, correct=False)
                self.record_error(agent)
                count += 1
        return count
    
    def import_postmortem_data(self, data: Dict[str, Any]) -> int:
        """
        Import data from PostMortem analysis.
        
        Args:
            data: PostMortem export data
            
        Returns:
            Number of events imported
        """
        count = 0
        for agent_data in data.get('agent_grades', []):
            agent_name = agent_data.get('agent')
            if agent_name:
                # Use the postmortem grade to adjust context fidelity
                grade = agent_data.get('grade', 100)
                claims = agent_data.get('claims_made', 10)
                correct = int(claims * grade / 100)
                
                agent = self.register_agent(agent_name)
                agent.total_claims += claims
                agent.correct_claims += correct
                count += 1
        return count
    
    def export_data(self) -> Dict[str, Any]:
        """
        Export monitor data for integration.
        
        Returns:
            Dictionary with all monitor data
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'coherence_score': self.get_coherence_score(),
            'agent_scores': self.get_agent_scores(),
            'agents': {name: agent.to_dict() for name, agent in self.agents.items()},
            'active_alerts': [a.to_dict() for a in self.alerts.active_alerts],
            'trend': self.get_trend(),
            'thresholds': self.thresholds.to_dict(),
        }
    
    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------
    
    def _load_data(self) -> None:
        """Load data from disk."""
        data_file = self.data_dir / "monitor_data.json"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load agents
                for name, agent_data in data.get('agents', {}).items():
                    self.agents[name] = AgentStatus.from_dict(agent_data)
                
                # Load thresholds
                if 'thresholds' in data:
                    self.thresholds = Thresholds.from_dict(data['thresholds'])
                    self.scorer = CoherenceScorer(self.thresholds)
                    self.alerts = AlertSystem(self.thresholds)
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[!] Warning: Could not load data: {e}", file=sys.stderr)
    
    def save(self) -> None:
        """Save data to disk."""
        data_file = self.data_dir / "monitor_data.json"
        
        data = {
            'saved_at': datetime.now().isoformat(),
            'agents': {name: agent.to_dict() for name, agent in self.agents.items()},
            'thresholds': self.thresholds.to_dict(),
        }
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def reset(self) -> None:
        """Reset all monitoring data."""
        self.agents.clear()
        self.alerts.active_alerts.clear()
        self.alerts.alert_history.clear()
        self.snapshots.clear()
        self.session_start = datetime.now()


# =============================================================================
# CLI INTERFACE
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog='teamcoherencemonitor',
        description='Real-Time Coordination Health Dashboard for Multi-Agent Teams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dashboard                    # Show team dashboard
  %(prog)s dashboard --compact          # Show compact dashboard
  %(prog)s score                        # Get team coherence score
  %(prog)s agents                       # List registered agents
  %(prog)s agent FORGE                  # Show FORGE metrics
  %(prog)s alerts                       # List active alerts
  %(prog)s record-mention FORGE         # Record mention for FORGE
  %(prog)s record-response FORGE 2.5    # Record 2.5s response for FORGE
  %(prog)s export                       # Export all data as JSON
  %(prog)s reset                        # Reset all data

For more information: https://github.com/DonkRonk17/TeamCoherenceMonitor
        """
    )
    
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--data-dir', type=Path,
                       help='Data directory (default: ~/.teamcoherencemonitor)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dashboard command
    dash_parser = subparsers.add_parser('dashboard', help='Show team dashboard')
    dash_parser.add_argument('--compact', '-c', action='store_true',
                            help='Show compact view')
    
    # Score command
    subparsers.add_parser('score', help='Get team coherence score')
    
    # Agents command
    subparsers.add_parser('agents', help='List registered agents')
    
    # Agent command
    agent_parser = subparsers.add_parser('agent', help='Show agent metrics')
    agent_parser.add_argument('name', help='Agent name')
    
    # Alerts command
    alerts_parser = subparsers.add_parser('alerts', help='List active alerts')
    alerts_parser.add_argument('--severity', '-s',
                              choices=['INFO', 'WARNING', 'CRITICAL'],
                              help='Filter by severity')
    
    # Record commands
    mention_parser = subparsers.add_parser('record-mention', help='Record mention event')
    mention_parser.add_argument('agent', help='Agent name')
    mention_parser.add_argument('--ack', action='store_true', help='Mark as acknowledged')
    
    response_parser = subparsers.add_parser('record-response', help='Record response')
    response_parser.add_argument('agent', help='Agent name')
    response_parser.add_argument('latency', type=float, help='Latency in seconds')
    
    claim_parser = subparsers.add_parser('record-claim', help='Record claim accuracy')
    claim_parser.add_argument('agent', help='Agent name')
    claim_parser.add_argument('--correct', action='store_true', help='Claim was correct')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register an agent')
    register_parser.add_argument('agent', help='Agent name')
    
    # Export command
    subparsers.add_parser('export', help='Export all data as JSON')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset all monitoring data')
    
    # Check command
    subparsers.add_parser('check', help='Check all alerts and take snapshot')
    
    return parser


def main():
    """CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize monitor
    monitor = TeamCoherenceMonitor(data_dir=args.data_dir)
    
    try:
        if args.command == 'dashboard':
            print(monitor.format_dashboard(compact=args.compact))
        
        elif args.command == 'score':
            score = monitor.get_coherence_score()
            status = "[OK]" if score >= 75 else "[!]" if score >= 50 else "[X]"
            print(f"Team Coherence: {score:.1f}/100 {status}")
        
        elif args.command == 'agents':
            agents = monitor.list_agents()
            if agents:
                scores = monitor.get_agent_scores()
                print(f"Registered Agents ({len(agents)}):")
                for name in sorted(agents):
                    score = scores.get(name, 0)
                    print(f"  {name}: {score:.1f}")
            else:
                print("No agents registered")
        
        elif args.command == 'agent':
            metrics = monitor.get_agent_metrics(args.name)
            if metrics:
                print(f"Agent: {metrics['name']}")
                print(f"  Coherence Score: {metrics['coherence_score']:.1f}")
                print(f"  Ack Rate: {metrics['ack_rate']:.1f}%")
                print(f"  Avg Latency: {metrics['avg_latency']:.2f}s")
                print(f"  Context Fidelity: {metrics['context_fidelity']:.1f}%")
                print(f"  Mentions: {metrics['mentions_acknowledged']}/{metrics['mentions_received']}")
                print(f"  Messages: {metrics['messages_sent']}")
                print(f"  Errors: {metrics['errors_detected']}")
                print(f"  Status: {'Active' if metrics['is_active'] else 'Inactive'}")
            else:
                print(f"[!] Agent not found: {args.name}")
                return 1
        
        elif args.command == 'alerts':
            alerts = monitor.get_alerts(severity=getattr(args, 'severity', None))
            if alerts:
                print(f"Active Alerts ({len(alerts)}):")
                for alert in alerts:
                    icon = "[X]" if alert.severity == "CRITICAL" else "[!]"
                    print(f"  {icon} [{alert.agent or 'TEAM'}] {alert.message}")
            else:
                print("[OK] No active alerts")
        
        elif args.command == 'record-mention':
            monitor.record_mention(args.agent, acknowledged=args.ack)
            monitor.save()
            print(f"[OK] Recorded mention for {args.agent.upper()}")
        
        elif args.command == 'record-response':
            monitor.record_response(args.agent, args.latency)
            monitor.save()
            print(f"[OK] Recorded {args.latency}s response for {args.agent.upper()}")
        
        elif args.command == 'record-claim':
            monitor.record_claim(args.agent, correct=args.correct)
            monitor.save()
            status = "correct" if args.correct else "incorrect"
            print(f"[OK] Recorded {status} claim for {args.agent.upper()}")
        
        elif args.command == 'register':
            monitor.register_agent(args.agent)
            monitor.save()
            print(f"[OK] Registered agent: {args.agent.upper()}")
        
        elif args.command == 'export':
            data = monitor.export_data()
            print(json.dumps(data, indent=2))
        
        elif args.command == 'reset':
            monitor.reset()
            monitor.save()
            print("[OK] All monitoring data reset")
        
        elif args.command == 'check':
            alerts = monitor.check_all_alerts()
            snapshot = monitor.take_snapshot()
            monitor.save()
            
            print(f"[OK] Check complete")
            print(f"  Coherence: {snapshot.overall_score:.1f}")
            print(f"  Active Agents: {snapshot.active_agents}/{snapshot.total_agents}")
            print(f"  New Alerts: {len(alerts)}")
        
        return 0
    
    except Exception as e:
        print(f"[X] Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
