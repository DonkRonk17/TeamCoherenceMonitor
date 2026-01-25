# TeamCoherenceMonitor - Usage Examples

Comprehensive examples demonstrating all features of TeamCoherenceMonitor.

## Quick Navigation

- [Example 1: Basic Setup](#example-1-basic-setup)
- [Example 2: Recording Events](#example-2-recording-events)
- [Example 3: Viewing Dashboard](#example-3-viewing-dashboard)
- [Example 4: Working with Alerts](#example-4-working-with-alerts)
- [Example 5: Coherence Scoring](#example-5-coherence-scoring)
- [Example 6: Integration with MentionGuard](#example-6-integration-with-mentionguard)
- [Example 7: Session Monitoring](#example-7-session-monitoring)
- [Example 8: Custom Thresholds](#example-8-custom-thresholds)
- [Example 9: Trend Analysis](#example-9-trend-analysis)
- [Example 10: Full Production Workflow](#example-10-full-production-workflow)

---

## Example 1: Basic Setup

**Scenario:** First time setting up TeamCoherenceMonitor for your team.

### CLI Usage

```bash
# Check version
python teamcoherencemonitor.py --version
# Output: teamcoherencemonitor 1.0

# Register your team agents
python teamcoherencemonitor.py register FORGE
python teamcoherencemonitor.py register ATLAS
python teamcoherencemonitor.py register CLIO
python teamcoherencemonitor.py register NEXUS
python teamcoherencemonitor.py register BOLT

# Verify agents are registered
python teamcoherencemonitor.py agents
```

**Expected Output:**
```
[OK] Registered agent: FORGE
[OK] Registered agent: ATLAS
[OK] Registered agent: CLIO
[OK] Registered agent: NEXUS
[OK] Registered agent: BOLT

Registered Agents (5):
  ATLAS: 85.0
  BOLT: 85.0
  CLIO: 85.0
  FORGE: 85.0
  NEXUS: 85.0
```

### Python Usage

```python
from teamcoherencemonitor import TeamCoherenceMonitor

# Initialize monitor
monitor = TeamCoherenceMonitor()

# Register agents
agents = ["FORGE", "ATLAS", "CLIO", "NEXUS", "BOLT"]
for agent in agents:
    monitor.register_agent(agent)
    print(f"Registered: {agent}")

# Save state
monitor.save()
print("Setup complete!")
```

**What You Learned:**
- How to initialize the monitor
- How to register agents
- How to save state

---

## Example 2: Recording Events

**Scenario:** Recording various events during a session.

### CLI Usage

```bash
# Record that FORGE was mentioned and acknowledged
python teamcoherencemonitor.py record-mention FORGE --ack

# Record that ATLAS was mentioned but didn't acknowledge
python teamcoherencemonitor.py record-mention ATLAS

# Record FORGE's response time (2.5 seconds)
python teamcoherencemonitor.py record-response FORGE 2.5

# Record that CLIO made a correct claim
python teamcoherencemonitor.py record-claim CLIO --correct

# Record that NEXUS made an incorrect claim
python teamcoherencemonitor.py record-claim NEXUS
```

**Expected Output:**
```
[OK] Recorded mention for FORGE
[OK] Recorded mention for ATLAS
[OK] Recorded 2.5s response for FORGE
[OK] Recorded correct claim for CLIO
[OK] Recorded incorrect claim for NEXUS
```

### Python Usage

```python
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()

# Record various events
monitor.record_mention("FORGE", acknowledged=True)
monitor.record_mention("ATLAS", acknowledged=False)
monitor.record_response("FORGE", latency=2.5)
monitor.record_response("ATLAS", latency=5.0)
monitor.record_claim("CLIO", correct=True)
monitor.record_claim("NEXUS", correct=False)
monitor.record_error("NEXUS")

# Check current scores
scores = monitor.get_agent_scores()
for agent, score in scores.items():
    print(f"{agent}: {score:.1f}")

monitor.save()
```

**What You Learned:**
- How to record @mentions
- How to track acknowledgments
- How to record response latencies
- How to track claim accuracy

---

## Example 3: Viewing Dashboard

**Scenario:** Viewing team coordination status.

### CLI Usage

```bash
# Full dashboard
python teamcoherencemonitor.py dashboard

# Compact dashboard
python teamcoherencemonitor.py dashboard --compact

# Just the score
python teamcoherencemonitor.py score
```

**Full Dashboard Output:**
```
======================================================================
TEAM COHERENCE MONITOR - Score: 82.5/100 [OK]
======================================================================

AGENT STATUS
----------------------------------------------------------------------
Agent        Score   ACK%   Latency  Fidelity  Status
----------------------------------------------------------------------
ATLAS         78.5    50.0%     5.0s   100.0%   Active
BOLT          85.0   100.0%     0.0s   100.0%   Inactive
CLIO          90.0   100.0%     0.0s   100.0%   Active
FORGE         92.5   100.0%     2.5s   100.0%   Active
NEXUS         66.5   100.0%     0.0s    50.0%   Active

ALERTS
----------------------------------------------------------------------
[!] [NEXUS] NEXUS context fidelity below threshold

TREND (30min): STABLE (+0.0)
======================================================================
```

**Compact Dashboard Output:**
```
======================================================================
TEAM COHERENCE MONITOR - Score: 82.5/100 [OK]
======================================================================

Agents: 5 | Active Alerts: 1

  ATLAS        78.5 [OK]   ACK: 50.0%  LAT:  5.0s
  BOLT         85.0 [OK]   ACK:100.0%  LAT:  0.0s
  CLIO         90.0 [OK]   ACK:100.0%  LAT:  0.0s
  FORGE        92.5 [OK]   ACK:100.0%  LAT:  2.5s
  NEXUS        66.5 [!]    ACK:100.0%  LAT:  0.0s
======================================================================
```

### Python Usage

```python
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()

# Get dashboard as string
dashboard = monitor.format_dashboard()
print(dashboard)

# Get compact dashboard
compact = monitor.format_dashboard(compact=True)
print(compact)

# Get just the score
score = monitor.get_coherence_score()
print(f"Team Coherence: {score:.1f}/100")
```

**What You Learned:**
- How to view full dashboard
- How to use compact mode
- How to get the coherence score

---

## Example 4: Working with Alerts

**Scenario:** Managing coordination alerts.

### CLI Usage

```bash
# View all active alerts
python teamcoherencemonitor.py alerts

# Filter by severity
python teamcoherencemonitor.py alerts --severity CRITICAL
python teamcoherencemonitor.py alerts --severity WARNING

# Run a full check (generates alerts + takes snapshot)
python teamcoherencemonitor.py check
```

**Expected Output:**
```
Active Alerts (2):
  [X] [NEXUS] NEXUS context fidelity critically low
  [!] [ATLAS] ATLAS acknowledgment rate below threshold
```

### Python Usage

```python
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()

# Simulate some poor metrics
monitor.record_mention("FORGE", acknowledged=False)
monitor.record_mention("FORGE", acknowledged=False)
monitor.record_claim("ATLAS", correct=False)
monitor.record_claim("ATLAS", correct=False)

# Check for alerts
new_alerts = monitor.check_all_alerts()
print(f"Generated {len(new_alerts)} new alerts")

# View all active alerts
all_alerts = monitor.get_alerts()
for alert in all_alerts:
    print(f"[{alert.severity}] {alert.agent}: {alert.message}")

# View only critical alerts
critical = monitor.get_alerts(severity="CRITICAL")
print(f"\nCritical alerts: {len(critical)}")

# Clear alerts for an agent
cleared = monitor.clear_alerts(agent="FORGE")
print(f"Cleared {cleared} alerts for FORGE")
```

**What You Learned:**
- How to check for alerts
- How to filter alerts by severity
- How to clear alerts

---

## Example 5: Coherence Scoring

**Scenario:** Understanding and working with coherence scores.

### CLI Usage

```bash
# Get team score
python teamcoherencemonitor.py score

# Get detailed agent metrics
python teamcoherencemonitor.py agent FORGE
```

**Expected Output:**
```
Team Coherence: 82.5/100 [OK]

Agent: FORGE
  Coherence Score: 92.5
  Ack Rate: 100.0%
  Avg Latency: 2.50s
  Context Fidelity: 100.0%
  Mentions: 2/2
  Messages: 3
  Errors: 0
  Status: Active
```

### Python Usage

```python
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()

# Register and populate data
monitor.register_agent("FORGE")
monitor.record_mention("FORGE", acknowledged=True)
monitor.record_mention("FORGE", acknowledged=True)
monitor.record_response("FORGE", latency=2.0)
monitor.record_response("FORGE", latency=3.0)
monitor.record_claim("FORGE", correct=True)

# Get team coherence score
team_score = monitor.get_coherence_score()
print(f"Team Score: {team_score:.1f}")

# Get individual scores
agent_scores = monitor.get_agent_scores()
for agent, score in agent_scores.items():
    print(f"  {agent}: {score:.1f}")

# Get detailed metrics for one agent
metrics = monitor.get_agent_metrics("FORGE")
print(f"\nFORGE Metrics:")
print(f"  ACK Rate: {metrics['ack_rate']:.1f}%")
print(f"  Avg Latency: {metrics['avg_latency']:.2f}s")
print(f"  Fidelity: {metrics['context_fidelity']:.1f}%")
print(f"  Score: {metrics['coherence_score']:.1f}")
```

**What You Learned:**
- How scores are calculated
- How to get detailed agent metrics
- What each metric means

---

## Example 6: Integration with MentionGuard

**Scenario:** Importing data from MentionGuard for unified monitoring.

### Python Usage

```python
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()

# Simulated MentionGuard export data
mentionguard_data = {
    'events': [
        {'agent': 'FORGE', 'acknowledged': True, 'timestamp': '2026-01-25T10:00:00'},
        {'agent': 'ATLAS', 'acknowledged': True, 'timestamp': '2026-01-25T10:01:00'},
        {'agent': 'CLIO', 'acknowledged': False, 'timestamp': '2026-01-25T10:02:00'},
        {'agent': 'FORGE', 'acknowledged': True, 'timestamp': '2026-01-25T10:03:00'},
        {'agent': 'NEXUS', 'acknowledged': False, 'timestamp': '2026-01-25T10:04:00'},
    ]
}

# Import the data
count = monitor.import_mentionguard_data(mentionguard_data)
print(f"Imported {count} mention events from MentionGuard")

# Check the impact on scores
scores = monitor.get_agent_scores()
print("\nAgent Acknowledgment Scores:")
for agent, score in sorted(scores.items()):
    agent_obj = monitor.get_agent(agent)
    ack_rate = agent_obj.ack_rate() if agent_obj else 0
    print(f"  {agent}: {ack_rate:.1f}% ACK rate")

monitor.save()
```

**Expected Output:**
```
Imported 5 mention events from MentionGuard

Agent Acknowledgment Scores:
  ATLAS: 100.0% ACK rate
  CLIO: 0.0% ACK rate
  FORGE: 100.0% ACK rate
  NEXUS: 0.0% ACK rate
```

**What You Learned:**
- How to import MentionGuard data
- How mention events affect scores
- Integration patterns

---

## Example 7: Session Monitoring

**Scenario:** Continuous monitoring during a team session.

### Python Usage

```python
import time
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()

# Register all session participants
participants = ["FORGE", "ATLAS", "CLIO", "NEXUS", "BOLT"]
for p in participants:
    monitor.register_agent(p)

print("Session monitoring started...")
print("="*50)

# Simulate a session with events
session_events = [
    ("mention", "FORGE", True),
    ("response", "FORGE", 2.1),
    ("mention", "ATLAS", True),
    ("response", "ATLAS", 3.5),
    ("claim", "CLIO", True),
    ("mention", "NEXUS", False),  # Missed mention!
    ("response", "FORGE", 1.8),
    ("claim", "NEXUS", False),    # Wrong claim!
]

for event_type, agent, value in session_events:
    if event_type == "mention":
        monitor.record_mention(agent, acknowledged=value)
        print(f"@{agent} mentioned {'[ACK]' if value else '[MISSED]'}")
    elif event_type == "response":
        monitor.record_response(agent, latency=value)
        print(f"{agent} responded in {value}s")
    elif event_type == "claim":
        monitor.record_claim(agent, correct=value)
        print(f"{agent} claim {'correct' if value else 'INCORRECT'}")
    
    # Check coherence after each event
    score = monitor.get_coherence_score()
    status = "[OK]" if score >= 75 else "[!]" if score >= 50 else "[X]"
    print(f"  -> Coherence: {score:.1f} {status}")
    print()

# Final check
print("="*50)
print("Session Complete - Final Status:")
print(monitor.format_dashboard(compact=True))

# Check for alerts
alerts = monitor.check_all_alerts()
if alerts:
    print(f"\n{len(alerts)} alerts generated:")
    for alert in alerts:
        print(f"  [{alert.severity}] {alert.message}")

monitor.save()
```

**What You Learned:**
- How to monitor in real-time
- How events affect coherence
- How to detect issues as they happen

---

## Example 8: Custom Thresholds

**Scenario:** Configuring stricter or more lenient thresholds.

### Python Usage

```python
from teamcoherencemonitor import TeamCoherenceMonitor, Thresholds

# Create strict thresholds for critical missions
strict_thresholds = Thresholds(
    latency_warning=15.0,       # Warning at 15s (default 30s)
    latency_critical=30.0,      # Critical at 30s (default 60s)
    ack_rate_warning=90.0,      # Warning below 90% (default 80%)
    ack_rate_critical=75.0,     # Critical below 75% (default 60%)
    fidelity_warning=95.0,      # Warning below 95% (default 90%)
    fidelity_critical=85.0,     # Critical below 85% (default 70%)
    inactive_warning=60.0,      # Warning after 1 min (default 2 min)
    inactive_critical=180.0,    # Critical after 3 min (default 5 min)
)

# Initialize with strict thresholds
monitor = TeamCoherenceMonitor(thresholds=strict_thresholds)

# Register agents
monitor.register_agent("FORGE")
monitor.register_agent("ATLAS")

# Simulate "normal" latency that would now trigger warnings
monitor.record_response("FORGE", latency=20.0)  # Would be OK with defaults
monitor.record_response("ATLAS", latency=25.0)  # Would be OK with defaults

# Check for alerts
alerts = monitor.check_all_alerts()
print(f"Alerts with strict thresholds: {len(alerts)}")
for alert in alerts:
    print(f"  [{alert.severity}] {alert.message}")

# Compare with default thresholds
print("\n--- With Default Thresholds ---")
monitor_default = TeamCoherenceMonitor(auto_load=False)
monitor_default.register_agent("FORGE")
monitor_default.register_agent("ATLAS")
monitor_default.record_response("FORGE", latency=20.0)
monitor_default.record_response("ATLAS", latency=25.0)

alerts_default = monitor_default.check_all_alerts()
print(f"Alerts with default thresholds: {len(alerts_default)}")
```

**Expected Output:**
```
Alerts with strict thresholds: 2
  [WARNING] FORGE response latency high
  [WARNING] ATLAS response latency high

--- With Default Thresholds ---
Alerts with default thresholds: 0
```

**What You Learned:**
- How to create custom thresholds
- Impact of threshold tuning
- When to use strict vs lenient settings

---

## Example 9: Trend Analysis

**Scenario:** Analyzing coherence trends over time.

### Python Usage

```python
import time
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()
monitor.register_agent("FORGE")
monitor.register_agent("ATLAS")

print("Simulating 10-minute session with degrading coherence...")
print("="*50)

# Simulate a session where things gradually get worse
for minute in range(10):
    # Take a snapshot
    snapshot = monitor.take_snapshot()
    print(f"Minute {minute}: Score {snapshot.overall_score:.1f}")
    
    # Add some events (performance degrades over time)
    if minute < 5:
        # First half: good performance
        monitor.record_mention("FORGE", acknowledged=True)
        monitor.record_response("FORGE", latency=2.0 + minute * 0.5)
        monitor.record_claim("FORGE", correct=True)
    else:
        # Second half: degrading performance
        monitor.record_mention("FORGE", acknowledged=False)
        monitor.record_response("FORGE", latency=10.0 + minute * 2)
        monitor.record_claim("FORGE", correct=False)

# Analyze the trend
trend = monitor.get_trend(minutes=30)
print("\n" + "="*50)
print("TREND ANALYSIS")
print("="*50)
print(f"Trend Direction: {trend['trend']}")
print(f"Score Change: {trend['change']:+.1f}")
print(f"Min Score: {trend['min_score']:.1f}")
print(f"Max Score: {trend['max_score']:.1f}")
print(f"Avg Score: {trend['avg_score']:.1f}")
print(f"Samples: {trend['samples']}")

# Get detailed interpretation
if trend['trend'] == 'DEGRADING':
    print("\n[!] WARNING: Team coherence is degrading!")
    print("    Consider intervention to prevent further decline.")
elif trend['trend'] == 'IMPROVING':
    print("\n[OK] Team coherence is improving!")
elif trend['trend'] == 'STABLE':
    print("\n[INFO] Team coherence is stable.")
```

**What You Learned:**
- How to take snapshots
- How to analyze trends
- How to interpret trend data

---

## Example 10: Full Production Workflow

**Scenario:** Complete end-to-end workflow for BCH session monitoring.

### Python Usage

```python
import json
from datetime import datetime
from pathlib import Path
from teamcoherencemonitor import TeamCoherenceMonitor, Thresholds

print("="*70)
print("BCH SESSION MONITORING - Full Production Workflow")
print("="*70)
print()

# 1. Initialize with production thresholds
print("[1/7] Initializing monitor...")
thresholds = Thresholds(
    ack_rate_warning=85.0,
    ack_rate_critical=70.0,
)
monitor = TeamCoherenceMonitor(thresholds=thresholds)

# 2. Register all BCH agents
print("[2/7] Registering agents...")
bch_agents = ["FORGE", "ATLAS", "CLIO", "NEXUS", "BOLT", "IRIS", "PORTER"]
for agent in bch_agents:
    monitor.register_agent(agent)
print(f"  Registered {len(bch_agents)} agents")

# 3. Simulate session activity
print("[3/7] Recording session events...")
events = [
    # Opening coordination
    ("mention", "FORGE", True),
    ("response", "FORGE", 1.5),
    ("mention", "CLIO", True),
    ("response", "CLIO", 2.1),
    
    # Task assignment
    ("mention", "ATLAS", True),
    ("response", "ATLAS", 3.2),
    ("claim", "FORGE", True),
    
    # Work in progress
    ("response", "NEXUS", 4.5),
    ("mention", "BOLT", True),
    ("response", "BOLT", 2.0),
    
    # Issue occurs - IRIS misses mention
    ("mention", "IRIS", False),
    ("claim", "IRIS", False),
    
    # Recovery
    ("mention", "IRIS", True),
    ("response", "IRIS", 8.5),
    ("claim", "IRIS", True),
    
    # Closing
    ("response", "FORGE", 1.2),
    ("claim", "FORGE", True),
]

for event_type, agent, value in events:
    if event_type == "mention":
        monitor.record_mention(agent, acknowledged=value)
    elif event_type == "response":
        monitor.record_response(agent, latency=value)
    elif event_type == "claim":
        monitor.record_claim(agent, correct=value)

print(f"  Recorded {len(events)} events")

# 4. Check alerts
print("[4/7] Checking alerts...")
alerts = monitor.check_all_alerts()
critical = [a for a in alerts if a.severity == "CRITICAL"]
warnings = [a for a in alerts if a.severity == "WARNING"]
print(f"  Critical: {len(critical)}, Warnings: {len(warnings)}")

# 5. Take final snapshot
print("[5/7] Taking final snapshot...")
snapshot = monitor.take_snapshot()

# 6. Generate session report
print("[6/7] Generating report...")
print()
print("-"*70)
print("SESSION REPORT")
print("-"*70)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Final Coherence Score: {snapshot.overall_score:.1f}/100")
print(f"Active Agents: {snapshot.active_agents}/{snapshot.total_agents}")
print(f"Active Alerts: {snapshot.alerts_active}")
print()

print("Agent Performance:")
for agent, score in sorted(snapshot.agent_scores.items()):
    metrics = monitor.get_agent_metrics(agent)
    status = "[OK]" if score >= 75 else "[!]" if score >= 50 else "[X]"
    print(f"  {agent:10} {score:5.1f} {status}")
    print(f"            ACK: {metrics['ack_rate']:5.1f}%  "
          f"LAT: {metrics['avg_latency']:5.2f}s  "
          f"FID: {metrics['context_fidelity']:5.1f}%")

print()
if alerts:
    print("Issues Detected:")
    for alert in alerts:
        icon = "[X]" if alert.severity == "CRITICAL" else "[!]"
        print(f"  {icon} [{alert.agent}] {alert.message}")

# 7. Export data
print()
print("[7/7] Exporting data...")
export_data = monitor.export_data()
export_file = Path("session_coherence_export.json")
with open(export_file, "w") as f:
    json.dump(export_data, f, indent=2)
print(f"  Exported to: {export_file}")

# Save state
monitor.save()

print()
print("="*70)
print("SESSION MONITORING COMPLETE")
print("="*70)
```

**Expected Output:**
```
======================================================================
BCH SESSION MONITORING - Full Production Workflow
======================================================================

[1/7] Initializing monitor...
[2/7] Registering agents...
  Registered 7 agents
[3/7] Recording session events...
  Recorded 18 events
[4/7] Checking alerts...
  Critical: 0, Warnings: 1
[5/7] Taking final snapshot...
[6/7] Generating report...

----------------------------------------------------------------------
SESSION REPORT
----------------------------------------------------------------------
Timestamp: 2026-01-25T14:30:00.000000
Final Coherence Score: 84.2/100
Active Agents: 6/7
Active Alerts: 1

Agent Performance:
  ATLAS       88.5 [OK]
            ACK: 100.0%  LAT:  3.20s  FID: 100.0%
  BOLT        90.0 [OK]
            ACK: 100.0%  LAT:  2.00s  FID: 100.0%
  CLIO        89.5 [OK]
            ACK: 100.0%  LAT:  2.10s  FID: 100.0%
  FORGE       92.0 [OK]
            ACK: 100.0%  LAT:  1.35s  FID: 100.0%
  IRIS        75.5 [OK]
            ACK:  50.0%  LAT:  8.50s  FID:  50.0%
  NEXUS       85.0 [OK]
            ACK: 100.0%  LAT:  4.50s  FID: 100.0%
  PORTER      85.0 [OK]
            ACK: 100.0%  LAT:  0.00s  FID: 100.0%

Issues Detected:
  [!] [IRIS] IRIS acknowledgment rate below threshold

[7/7] Exporting data...
  Exported to: session_coherence_export.json

======================================================================
SESSION MONITORING COMPLETE
======================================================================
```

**What You Learned:**
- Complete production workflow
- Session initialization and teardown
- Report generation
- Data export for archival

---

## Summary

These examples demonstrate:

1. **Basic Setup** - Initialize and configure the monitor
2. **Recording Events** - Track mentions, responses, claims
3. **Dashboard Views** - Full and compact monitoring
4. **Alert Management** - Detection and handling
5. **Coherence Scoring** - Understanding metrics
6. **Tool Integration** - Working with MentionGuard
7. **Session Monitoring** - Real-time tracking
8. **Custom Thresholds** - Tuning sensitivity
9. **Trend Analysis** - Historical patterns
10. **Production Workflow** - End-to-end operations

For more information, see:
- [README.md](README.md) - Full documentation
- [CHEAT_SHEET.txt](CHEAT_SHEET.txt) - Quick reference
- [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - Integration guide
