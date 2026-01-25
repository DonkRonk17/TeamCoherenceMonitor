# TeamCoherenceMonitor - Integration Examples

## 🎯 INTEGRATION PHILOSOPHY

TeamCoherenceMonitor is designed to work seamlessly with other Team Brain tools. This document provides **copy-paste-ready code examples** for common integration patterns.

---

## 📚 TABLE OF CONTENTS

1. [Pattern 1: TeamCoherenceMonitor + MentionGuard](#pattern-1-teamcoherencemonitor--mentionguard)
2. [Pattern 2: TeamCoherenceMonitor + LiveAudit](#pattern-2-teamcoherencemonitor--liveaudit)
3. [Pattern 3: TeamCoherenceMonitor + PostMortem](#pattern-3-teamcoherencemonitor--postmortem)
4. [Pattern 4: TeamCoherenceMonitor + SynapseLink](#pattern-4-teamcoherencemonitor--synapselink)
5. [Pattern 5: TeamCoherenceMonitor + AgentHealth](#pattern-5-teamcoherencemonitor--agenthealth)
6. [Pattern 6: TeamCoherenceMonitor + TaskQueuePro](#pattern-6-teamcoherencemonitor--taskqueuepro)
7. [Pattern 7: TeamCoherenceMonitor + ContextCompressor](#pattern-7-teamcoherencemonitor--contextcompressor)
8. [Pattern 8: TeamCoherenceMonitor + ConfigManager](#pattern-8-teamcoherencemonitor--configmanager)
9. [Pattern 9: Multi-Tool Coordination Workflow](#pattern-9-multi-tool-coordination-workflow)
10. [Pattern 10: Full BCH Session Monitoring](#pattern-10-full-bch-session-monitoring)

---

## Pattern 1: TeamCoherenceMonitor + MentionGuard

**Use Case:** Unified @mention tracking with coherence monitoring

**Why:** MentionGuard tracks mentions; TeamCoherenceMonitor uses that data for scoring

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
# from mentionguard import MentionGuard  # Import when available

# Initialize both tools
monitor = TeamCoherenceMonitor()
# guard = MentionGuard()

# Simulated MentionGuard data export
mentionguard_export = {
    'events': [
        {'agent': 'FORGE', 'acknowledged': True, 'timestamp': '2026-01-25T10:00:00'},
        {'agent': 'ATLAS', 'acknowledged': True, 'timestamp': '2026-01-25T10:01:00'},
        {'agent': 'CLIO', 'acknowledged': False, 'timestamp': '2026-01-25T10:02:00'},
        {'agent': 'NEXUS', 'acknowledged': False, 'timestamp': '2026-01-25T10:03:00'},
    ]
}

# Import MentionGuard data into coherence monitor
count = monitor.import_mentionguard_data(mentionguard_export)
print(f"Imported {count} mention events")

# Now check coherence (includes mention data)
score = monitor.get_coherence_score()
print(f"Team Coherence: {score}/100")

# Check which agents have low ack rates
for agent in monitor.list_agents():
    metrics = monitor.get_agent_metrics(agent)
    if metrics['ack_rate'] < 80:
        print(f"[!] {agent} has low ack rate: {metrics['ack_rate']:.1f}%")
```

**Result:** Unified visibility into mention acknowledgment across the team

---

## Pattern 2: TeamCoherenceMonitor + LiveAudit

**Use Case:** Import real-time audit findings for fidelity tracking

**Why:** LiveAudit detects false claims; this affects context fidelity scores

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
# from liveaudit import LiveAudit  # Import when available

# Initialize
monitor = TeamCoherenceMonitor()
# audit = LiveAudit()

# Simulated LiveAudit issue export
liveaudit_export = {
    'issues': [
        {'agent': 'FORGE', 'issue_type': 'false_mention_claim', 'severity': 'HIGH'},
        {'agent': 'NEXUS', 'issue_type': 'incorrect_vote_count', 'severity': 'CRITICAL'},
        {'agent': 'NEXUS', 'issue_type': 'false_presence_claim', 'severity': 'HIGH'},
    ]
}

# Import LiveAudit findings
count = monitor.import_liveaudit_data(liveaudit_export)
print(f"Imported {count} audit issues")

# Check impact on fidelity
for agent in ['FORGE', 'NEXUS']:
    metrics = monitor.get_agent_metrics(agent)
    if metrics:
        print(f"{agent}: Fidelity = {metrics['context_fidelity']:.1f}%")

# Check for alerts
alerts = monitor.check_all_alerts()
fidelity_alerts = [a for a in alerts if a.metric == 'fidelity']
print(f"\nFidelity alerts: {len(fidelity_alerts)}")
```

**Result:** Context fidelity scores reflect actual audit findings

---

## Pattern 3: TeamCoherenceMonitor + PostMortem

**Use Case:** Import post-session analysis for historical context

**Why:** PostMortem grades inform long-term performance tracking

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
# from postmortem import PostMortem  # Import when available

# Initialize
monitor = TeamCoherenceMonitor()
# pm = PostMortem()

# Simulated PostMortem export
postmortem_export = {
    'session_id': 'bch_stress_test_001',
    'agent_grades': [
        {'agent': 'FORGE', 'grade': 95, 'claims_made': 20},
        {'agent': 'ATLAS', 'grade': 88, 'claims_made': 15},
        {'agent': 'CLIO', 'grade': 92, 'claims_made': 18},
        {'agent': 'NEXUS', 'grade': 65, 'claims_made': 12},  # Poor performance
        {'agent': 'BOLT', 'grade': 90, 'claims_made': 10},
    ]
}

# Import grades
count = monitor.import_postmortem_data(postmortem_export)
print(f"Imported grades for {count} agents")

# Review impact
scores = monitor.get_agent_scores()
print("\nAgent Coherence Scores (with PostMortem data):")
for agent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    metrics = monitor.get_agent_metrics(agent)
    print(f"  {agent}: {score:.1f} (Fidelity: {metrics['context_fidelity']:.1f}%)")
```

**Result:** Historical performance data informs current coherence scoring

---

## Pattern 4: TeamCoherenceMonitor + SynapseLink

**Use Case:** Send coherence alerts to team via Synapse

**Why:** Keep team informed of coordination status automatically

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
from synapselink import quick_send

monitor = TeamCoherenceMonitor()

# Register agents and simulate some activity
for agent in ["FORGE", "ATLAS", "CLIO", "NEXUS", "BOLT"]:
    monitor.register_agent(agent)

# Simulate degrading coordination
monitor.record_mention("NEXUS", acknowledged=False)
monitor.record_mention("NEXUS", acknowledged=False)
monitor.record_claim("NEXUS", correct=False)

# Check coherence and alert if needed
score = monitor.get_coherence_score()
alerts = monitor.check_all_alerts()

# Send appropriate notifications
if score < 50:
    # Critical - alert Logan and Forge
    quick_send(
        "LOGAN,FORGE",
        f"CRITICAL: Team Coherence at {score:.1f}/100",
        f"Immediate attention required!\n\n"
        f"Active Alerts ({len(alerts)}):\n" +
        "\n".join([f"- [{a.severity}] {a.agent}: {a.message}" for a in alerts]),
        priority="HIGH"
    )
elif score < 75:
    # Warning - notify team
    quick_send(
        "TEAM",
        f"Team Coherence Warning: {score:.1f}/100",
        f"Coordination may need attention.\n\n"
        f"Alerts: {len(alerts)}",
        priority="NORMAL"
    )
else:
    # Good - periodic update
    quick_send(
        "TEAM",
        f"Coherence Update: {score:.1f}/100 [OK]",
        f"Team coordination healthy.",
        priority="LOW"
    )
```

**Result:** Team automatically notified of coordination status

---

## Pattern 5: TeamCoherenceMonitor + AgentHealth

**Use Case:** Correlate coherence with agent health metrics

**Why:** Understand how agent health affects coordination

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
from agenthealth import AgentHealth

# Initialize both tools
monitor = TeamCoherenceMonitor()
health = AgentHealth()

# Use shared session ID for correlation
session_id = "coordination_session_001"

# Start tracking
health.start_session("ATLAS", session_id=session_id)
monitor.register_agent("ATLAS")
monitor.record_activity("ATLAS")

# Simulate work
import time
start = time.time()

# ... do work ...

# Record metrics
latency = time.time() - start
monitor.record_response("ATLAS", latency=latency)
health.heartbeat("ATLAS", status="active")

# At session end - correlate data
monitor_data = monitor.export_data()
health_summary = health.get_session_summary("ATLAS", session_id=session_id)

print("Correlation Analysis:")
print(f"  Coherence Score: {monitor_data['coherence_score']}")
print(f"  Agent Score: {monitor_data['agent_scores'].get('ATLAS', 'N/A')}")
# print(f"  Health Score: {health_summary.get('health_score', 'N/A')}")

# Save both
monitor.save()
health.end_session("ATLAS", session_id=session_id)
```

**Result:** Correlated health and coordination data for analysis

---

## Pattern 6: TeamCoherenceMonitor + TaskQueuePro

**Use Case:** Track task completion rates in coherence

**Why:** Task completion is another form of "claim accuracy"

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
from taskqueuepro import TaskQueuePro

monitor = TeamCoherenceMonitor()
queue = TaskQueuePro()

# Create a task
task_id = queue.create_task(
    title="Build WidgetTool v1.0",
    agent="ATLAS",
    priority=2
)

# Track the mention (task assignment)
monitor.record_mention("ATLAS", acknowledged=False)

# Agent starts task
queue.start_task(task_id)
monitor.record_acknowledgment("ATLAS")

# Task in progress - track activity
monitor.record_activity("ATLAS")

# Task completed successfully
queue.complete_task(task_id, result="Tool complete")
monitor.record_claim("ATLAS", correct=True)  # Successful claim

# Or if task failed
# queue.fail_task(task_id, error="Build error")
# monitor.record_claim("ATLAS", correct=False)  # Failed claim
# monitor.record_error("ATLAS")

# Check combined status
print(f"Coherence: {monitor.get_coherence_score()}")
metrics = monitor.get_agent_metrics("ATLAS")
print(f"ATLAS Fidelity: {metrics['context_fidelity']}%")
```

**Result:** Task completion tracked alongside coordination metrics

---

## Pattern 7: TeamCoherenceMonitor + ContextCompressor

**Use Case:** Compress coherence reports for efficient sharing

**Why:** Save tokens when sharing detailed status reports

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
from contextcompressor import ContextCompressor

monitor = TeamCoherenceMonitor()
compressor = ContextCompressor()

# Generate detailed report
for agent in ["FORGE", "ATLAS", "CLIO", "NEXUS", "BOLT"]:
    monitor.register_agent(agent)
    monitor.record_mention(agent, acknowledged=True)
    monitor.record_response(agent, latency=2.0)

full_dashboard = monitor.format_dashboard()
print(f"Full dashboard: {len(full_dashboard)} characters")

# Compress for sharing
compressed = compressor.compress_text(
    full_dashboard,
    query="team coordination status",
    method="summary"
)

print(f"Compressed: {len(compressed.compressed_text)} characters")
print(f"Savings: {compressed.estimated_token_savings} tokens")
print()
print("Compressed Report:")
print(compressed.compressed_text)
```

**Result:** Token-efficient coherence reports for sharing

---

## Pattern 8: TeamCoherenceMonitor + ConfigManager

**Use Case:** Centralize threshold configuration

**Why:** Share configuration across tools and environments

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor, Thresholds
from configmanager import ConfigManager

config = ConfigManager()

# Load or create default thresholds
default_thresholds = {
    "latency_warning": 30.0,
    "latency_critical": 60.0,
    "ack_rate_warning": 80.0,
    "ack_rate_critical": 60.0,
    "fidelity_warning": 90.0,
    "fidelity_critical": 70.0,
}

tcm_config = config.get("teamcoherencemonitor", default_thresholds)

# Create thresholds from config
thresholds = Thresholds(
    latency_warning=tcm_config.get("latency_warning", 30.0),
    latency_critical=tcm_config.get("latency_critical", 60.0),
    ack_rate_warning=tcm_config.get("ack_rate_warning", 80.0),
    ack_rate_critical=tcm_config.get("ack_rate_critical", 60.0),
    fidelity_warning=tcm_config.get("fidelity_warning", 90.0),
    fidelity_critical=tcm_config.get("fidelity_critical", 70.0),
)

# Initialize monitor with centralized config
monitor = TeamCoherenceMonitor(thresholds=thresholds)

print(f"Loaded thresholds from config:")
print(f"  Latency Warning: {thresholds.latency_warning}s")
print(f"  ACK Rate Warning: {thresholds.ack_rate_warning}%")

# Update config based on experience
if need_stricter_thresholds:
    config.set("teamcoherencemonitor.latency_warning", 20.0)
    config.save()
```

**Result:** Centralized, persistent threshold configuration

---

## Pattern 9: Multi-Tool Coordination Workflow

**Use Case:** Complete workflow using multiple coordination tools

**Why:** Demonstrate real production scenario with tool integration

**Code:**

```python
from teamcoherencemonitor import TeamCoherenceMonitor
from synapselink import quick_send
# from mentionguard import MentionGuard
# from liveaudit import LiveAudit

# Initialize tool stack
monitor = TeamCoherenceMonitor()
# guard = MentionGuard()
# audit = LiveAudit()

print("="*60)
print("BCH COORDINATION WORKFLOW")
print("="*60)

# Phase 1: Session Setup
print("\n[1] Session Setup")
agents = ["FORGE", "ATLAS", "CLIO", "NEXUS", "BOLT"]
for agent in agents:
    monitor.register_agent(agent)
print(f"  Registered {len(agents)} agents")

# Phase 2: Track Coordination Events
print("\n[2] Coordination Events")
events = [
    ("FORGE", True, 1.5),
    ("ATLAS", True, 2.3),
    ("CLIO", True, 1.8),
    ("NEXUS", False, 0),  # Missed mention!
    ("BOLT", True, 2.0),
]

for agent, acked, latency in events:
    monitor.record_mention(agent, acknowledged=acked)
    if acked:
        monitor.record_response(agent, latency=latency)
    status = "[ACK]" if acked else "[MISSED]"
    print(f"  @{agent} {status}")

# Phase 3: Check Status
print("\n[3] Status Check")
score = monitor.get_coherence_score()
alerts = monitor.check_all_alerts()
print(f"  Coherence: {score:.1f}/100")
print(f"  Alerts: {len(alerts)}")

# Phase 4: Handle Issues
print("\n[4] Issue Handling")
if score < 80 or alerts:
    # Notify about issues
    for alert in alerts:
        print(f"  [{alert.severity}] {alert.agent}: {alert.message}")
    
    # Send notification
    quick_send(
        "FORGE",
        f"Coordination Issue: {score:.1f}/100",
        f"Please review team status.\nAlerts: {len(alerts)}",
        priority="NORMAL"
    )

# Phase 5: Session Summary
print("\n[5] Session Summary")
snapshot = monitor.take_snapshot()
print(f"  Final Score: {snapshot.overall_score}")
print(f"  Active: {snapshot.active_agents}/{snapshot.total_agents}")

# Save state
monitor.save()

print("\n" + "="*60)
print("WORKFLOW COMPLETE")
print("="*60)
```

**Result:** Fully instrumented coordination workflow

---

## Pattern 10: Full BCH Session Monitoring

**Use Case:** Complete BCH session with all monitoring features

**Why:** Production-grade session monitoring example

**Code:**

```python
import json
from datetime import datetime
from pathlib import Path
from teamcoherencemonitor import TeamCoherenceMonitor, Thresholds
from synapselink import quick_send

class BCHSessionMonitor:
    """Full session monitoring for BCH operations."""
    
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.start_time = datetime.now()
        
        # Initialize with production thresholds
        self.thresholds = Thresholds(
            ack_rate_warning=85.0,
            ack_rate_critical=70.0,
            latency_warning=25.0,
            latency_critical=50.0,
        )
        self.monitor = TeamCoherenceMonitor(thresholds=self.thresholds)
        self.events = []
    
    def register_participants(self, agents: list):
        """Register session participants."""
        for agent in agents:
            self.monitor.register_agent(agent)
        print(f"Registered {len(agents)} participants")
    
    def on_message(self, sender: str, mentions: list = None, latency: float = None):
        """Process incoming message."""
        self.monitor.record_activity(sender)
        
        if latency:
            self.monitor.record_response(sender, latency=latency)
        
        if mentions:
            for mention in mentions:
                self.monitor.record_mention(mention, acknowledged=False)
        
        self.events.append({
            'time': datetime.now().isoformat(),
            'sender': sender,
            'mentions': mentions,
            'latency': latency,
        })
    
    def on_acknowledgment(self, agent: str):
        """Record mention acknowledgment."""
        self.monitor.record_acknowledgment(agent)
    
    def check_health(self) -> dict:
        """Check session health and alert if needed."""
        score = self.monitor.get_coherence_score()
        alerts = self.monitor.check_all_alerts()
        
        status = {
            'score': score,
            'alerts': len(alerts),
            'critical': len([a for a in alerts if a.severity == 'CRITICAL']),
        }
        
        # Auto-alert on critical issues
        if status['critical'] > 0:
            quick_send(
                "LOGAN",
                f"BCH Session Critical: {score:.1f}",
                f"Session: {self.session_name}\n"
                f"Critical alerts: {status['critical']}",
                priority="HIGH"
            )
        
        return status
    
    def end_session(self) -> dict:
        """Finalize session and generate report."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        snapshot = self.monitor.take_snapshot()
        
        report = {
            'session_name': self.session_name,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'final_coherence': snapshot.overall_score,
            'agent_scores': snapshot.agent_scores,
            'active_agents': snapshot.active_agents,
            'total_agents': snapshot.total_agents,
            'event_count': len(self.events),
            'alerts_generated': len(self.monitor.alerts.alert_history),
        }
        
        # Save report
        report_file = Path(f"session_{self.session_name}_{end_time.strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save monitor state
        self.monitor.save()
        
        # Notify team
        quick_send(
            "TEAM",
            f"Session Complete: {self.session_name}",
            f"Duration: {duration/60:.1f} min\n"
            f"Final Coherence: {snapshot.overall_score:.1f}/100\n"
            f"Report: {report_file}",
            priority="NORMAL"
        )
        
        return report


# Usage Example
if __name__ == "__main__":
    # Create session
    session = BCHSessionMonitor("stress_test_002")
    
    # Register participants
    session.register_participants([
        "FORGE", "ATLAS", "CLIO", "NEXUS", "BOLT", "IRIS", "PORTER"
    ])
    
    # Simulate session activity
    session.on_message("FORGE", mentions=["ATLAS", "CLIO"], latency=1.5)
    session.on_acknowledgment("ATLAS")
    session.on_message("ATLAS", latency=2.3)
    session.on_acknowledgment("CLIO")
    session.on_message("CLIO", mentions=["NEXUS"], latency=1.8)
    # NEXUS misses mention...
    session.on_message("BOLT", latency=2.0)
    
    # Check health
    health = session.check_health()
    print(f"Mid-session health: {health}")
    
    # End session
    report = session.end_session()
    print(f"Session ended: {report['final_coherence']:.1f}/100")
```

**Result:** Production-ready BCH session monitoring

---

## 📊 RECOMMENDED INTEGRATION PRIORITY

**Week 1 (Essential):**
1. ✅ SynapseLink - Team notifications
2. ✅ MentionGuard - Mention tracking
3. ✅ LiveAudit - Real-time verification

**Week 2 (Productivity):**
4. ☐ PostMortem - Historical analysis
5. ☐ AgentHealth - Health correlation
6. ☐ TaskQueuePro - Task tracking

**Week 3 (Advanced):**
7. ☐ ConfigManager - Centralized config
8. ☐ ContextCompressor - Token optimization
9. ☐ Full BCH integration

---

## 🔧 TROUBLESHOOTING INTEGRATIONS

**Import Errors:**
```python
# Ensure all tools are in Python path
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "OneDrive/Documents/AutoProjects"))

# Then import
from teamcoherencemonitor import TeamCoherenceMonitor
```

**Version Conflicts:**
```bash
# Check versions
python teamcoherencemonitor.py --version

# Update if needed
cd AutoProjects/TeamCoherenceMonitor
git pull origin main
```

**Data Directory Issues:**
```python
# Use custom data directory if needed
from pathlib import Path
monitor = TeamCoherenceMonitor(data_dir=Path("/custom/path"))
```

---

**Last Updated:** January 25, 2026  
**Maintained By:** ATLAS (Team Brain)
