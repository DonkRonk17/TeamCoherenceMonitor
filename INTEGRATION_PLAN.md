# TeamCoherenceMonitor - Integration Plan

Comprehensive integration documentation for Team Brain agents and BCH.

---

## 🎯 INTEGRATION GOALS

This document outlines how TeamCoherenceMonitor integrates with:
1. Team Brain agents (Forge, Atlas, Clio, Nexus, Bolt)
2. Existing Team Brain tools
3. BCH (Beacon Command Hub)
4. Logan's workflows

**Primary Goal:** Provide real-time visibility into multi-agent coordination health.

---

## 📦 BCH INTEGRATION

### Overview

TeamCoherenceMonitor integrates with BCH to provide real-time coordination monitoring during team sessions.

### BCH Commands

```
@coherence status              # Show team coherence score
@coherence dashboard           # Show full dashboard
@coherence agent <NAME>        # Show agent metrics
@coherence alerts              # List active alerts
@coherence check               # Run full check
```

### Implementation Steps

1. **Add to BCH imports:**
   ```python
   from teamcoherencemonitor import TeamCoherenceMonitor
   ```

2. **Create command handlers:**
   ```python
   @bch.command("coherence")
   def coherence_command(args):
       monitor = TeamCoherenceMonitor()
       if args[0] == "status":
           return f"Team Coherence: {monitor.get_coherence_score()}/100"
       # ... more handlers
   ```

3. **Hook into message stream:**
   ```python
   @bch.on_message
   def track_message(message):
       monitor.record_activity(message.sender)
       if message.mentions:
           for mention in message.mentions:
               monitor.record_mention(mention)
   ```

4. **Test integration:**
   - Verify commands work
   - Confirm real-time tracking
   - Validate alert generation

5. **Update BCH documentation:**
   - Add coherence commands to help
   - Document integration patterns

### BCH Event Hooks

TeamCoherenceMonitor can subscribe to BCH events:

| Event | Action |
|-------|--------|
| `message.sent` | Record activity, track response latency |
| `mention.created` | Record mention event |
| `mention.acknowledged` | Record acknowledgment |
| `vote.cast` | Track participation (via claims) |
| `session.start` | Initialize monitoring |
| `session.end` | Take final snapshot, export data |

---

## 🤖 AI AGENT INTEGRATION

### Integration Matrix

| Agent | Primary Use Case | Integration Method | Priority |
|-------|------------------|-------------------|----------|
| **Forge** | Orchestration monitoring | Python API + Synapse | HIGH |
| **Atlas** | Session tracking during builds | Python API | HIGH |
| **Clio** | CLI monitoring on Linux | CLI + Python | MEDIUM |
| **Nexus** | Cross-platform monitoring | Python API | MEDIUM |
| **Bolt** | Lightweight status checks | CLI | LOW |

### Agent-Specific Workflows

---

#### Forge (Orchestrator / Reviewer)

**Primary Use Case:** Monitor team coordination during orchestration sessions.

**Why Forge Needs This:**
- Forge coordinates multi-agent tasks
- Needs visibility into who is responding and how quickly
- Must detect coordination failures early

**Integration Steps:**

1. **Session Start:**
   ```python
   from teamcoherencemonitor import TeamCoherenceMonitor
   
   # Initialize at session start
   monitor = TeamCoherenceMonitor()
   
   # Register expected participants
   for agent in session.participants:
       monitor.register_agent(agent)
   ```

2. **During Orchestration:**
   ```python
   # After delegating task
   monitor.record_mention(target_agent, acknowledged=False)
   
   # When response received
   monitor.record_response(agent, latency=response_time)
   monitor.record_acknowledgment(agent)
   
   # Periodic check
   score = monitor.get_coherence_score()
   if score < 70:
       # Alert Logan or take corrective action
       alert_logan(f"Coordination degrading: {score}")
   ```

3. **Session End:**
   ```python
   # Final snapshot
   snapshot = monitor.take_snapshot()
   
   # Export for session summary
   data = monitor.export_data()
   save_to_session_log(data)
   ```

**Example Forge Workflow:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
from synapselink import quick_send

class ForgeOrchestrator:
    def __init__(self):
        self.monitor = TeamCoherenceMonitor()
        self.session_active = False
    
    def start_session(self, agents):
        """Initialize monitoring for orchestration session."""
        self.session_active = True
        for agent in agents:
            self.monitor.register_agent(agent)
        print(f"Monitoring {len(agents)} agents")
    
    def delegate_task(self, agent, task):
        """Delegate task and track mention."""
        self.monitor.record_mention(agent, acknowledged=False)
        # Send task via Synapse
        quick_send(agent, "Task Assignment", task)
    
    def receive_response(self, agent, response, latency):
        """Process response and update metrics."""
        self.monitor.record_response(agent, latency)
        self.monitor.record_acknowledgment(agent)
        
        # Check overall health
        self.check_coherence()
    
    def check_coherence(self):
        """Periodic coherence check."""
        score = self.monitor.get_coherence_score()
        alerts = self.monitor.check_all_alerts()
        
        if score < 60:
            quick_send("LOGAN", "CRITICAL", 
                      f"Team coherence critical: {score}/100")
        elif alerts:
            for alert in alerts:
                if alert.severity == "CRITICAL":
                    quick_send("LOGAN", alert.message)
    
    def end_session(self):
        """Finalize session monitoring."""
        self.session_active = False
        snapshot = self.monitor.take_snapshot()
        self.monitor.save()
        return snapshot
```

---

#### Atlas (Executor / Builder)

**Primary Use Case:** Track coordination during tool builds and multi-step tasks.

**Why Atlas Needs This:**
- Atlas executes complex multi-step tasks
- Coordinates with other agents during builds
- Needs to track own responsiveness

**Integration Steps:**

1. **Self-Monitoring:**
   ```python
   from teamcoherencemonitor import TeamCoherenceMonitor
   
   monitor = TeamCoherenceMonitor()
   
   # Track own activity
   monitor.record_activity("ATLAS")
   
   # After responding to a mention
   start_time = time.time()
   # ... process request ...
   latency = time.time() - start_time
   monitor.record_response("ATLAS", latency)
   ```

2. **Build Session Tracking:**
   ```python
   # Track tool build progress
   monitor.record_claim("ATLAS", correct=True)  # Completed step successfully
   
   # At session end
   metrics = monitor.get_agent_metrics("ATLAS")
   print(f"Session Metrics: {metrics}")
   ```

**Example Atlas Workflow:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
import time

class AtlasSession:
    def __init__(self):
        self.monitor = TeamCoherenceMonitor()
        self.monitor.register_agent("ATLAS")
        self.start_time = time.time()
    
    def on_mention(self):
        """Called when ATLAS is @mentioned."""
        self.mention_time = time.time()
        self.monitor.record_mention("ATLAS", acknowledged=False)
    
    def acknowledge(self):
        """Acknowledge the mention."""
        latency = time.time() - self.mention_time
        self.monitor.record_response("ATLAS", latency)
        self.monitor.record_acknowledgment("ATLAS")
    
    def complete_task(self, success: bool):
        """Mark task completion."""
        self.monitor.record_claim("ATLAS", correct=success)
        
    def get_self_score(self):
        """Get own coherence score."""
        return self.monitor.get_agent_metrics("ATLAS")
```

---

#### Clio (Linux / Ubuntu Agent)

**Primary Use Case:** CLI-based monitoring on Linux systems.

**Why Clio Needs This:**
- Clio operates in terminal environment
- Prefers CLI interfaces
- Manages BCH CLI components

**Integration Steps:**

1. **CLI Monitoring:**
   ```bash
   # Quick status check
   python teamcoherencemonitor.py score
   
   # Watch mode (conceptual)
   watch -n 30 "python teamcoherencemonitor.py dashboard --compact"
   ```

2. **Shell Integration:**
   ```bash
   # Add to .bashrc
   alias tcm="python ~/AutoProjects/TeamCoherenceMonitor/teamcoherencemonitor.py"
   
   # Usage
   tcm dashboard
   tcm agent CLIO
   ```

**Platform Considerations:**
- Data stored at `~/.teamcoherencemonitor/`
- Works with all POSIX shells
- Compatible with tmux/screen sessions

---

#### Nexus (Multi-Platform Agent)

**Primary Use Case:** Cross-platform coordination monitoring.

**Why Nexus Needs This:**
- Nexus works across Windows, Linux, macOS
- Needs consistent monitoring regardless of platform
- Often coordinates between platform-specific agents

**Integration Steps:**

1. **Platform-Agnostic Usage:**
   ```python
   from teamcoherencemonitor import TeamCoherenceMonitor
   
   # Works on all platforms
   monitor = TeamCoherenceMonitor()
   
   # Platform detection
   import platform
   print(f"Running on: {platform.system()}")
   ```

2. **Cross-Platform Coordination:**
   ```python
   # Track coordination across platforms
   monitor.record_mention("CLIO")  # Linux agent
   monitor.record_mention("IRIS")  # Desktop agent
   monitor.record_mention("PORTER")  # Mobile agent
   
   # Check overall coordination
   score = monitor.get_coherence_score()
   ```

---

#### Bolt (Cline / Free Executor)

**Primary Use Case:** Quick status checks without API costs.

**Why Bolt Needs This:**
- Bolt uses free execution (no API costs)
- Needs lightweight monitoring
- Can run periodic health checks

**Integration Steps:**

1. **Lightweight CLI Usage:**
   ```bash
   # Quick checks
   python teamcoherencemonitor.py score
   python teamcoherencemonitor.py alerts
   ```

2. **Batch Status Reports:**
   ```bash
   # Generate status report
   python teamcoherencemonitor.py export > /tmp/coherence_status.json
   ```

**Cost Considerations:**
- Zero API costs (uses local computation)
- Can run frequently without budget impact
- Useful for automated health checks

---

## 🔗 INTEGRATION WITH OTHER TEAM BRAIN TOOLS

### With MentionGuard

**Purpose:** Import @mention tracking data for comprehensive monitoring.

**Integration Pattern:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
from mentionguard import MentionGuard

monitor = TeamCoherenceMonitor()
guard = MentionGuard()

# Export MentionGuard data
mention_data = guard.export_events()

# Import into coherence monitor
count = monitor.import_mentionguard_data(mention_data)
print(f"Imported {count} mention events")

# Now coherence score includes mention data
score = monitor.get_coherence_score()
```

**Data Flow:**
```
MentionGuard → export_events() → TeamCoherenceMonitor → unified_score
```

---

### With LiveAudit

**Purpose:** Import real-time audit findings for fidelity scoring.

**Integration Pattern:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
from liveaudit import LiveAudit

monitor = TeamCoherenceMonitor()
audit = LiveAudit()

# Export audit issues
audit_data = audit.export_issues()

# Import into coherence monitor
count = monitor.import_liveaudit_data(audit_data)

# Issues decrease context fidelity scores
score = monitor.get_coherence_score()
```

**Data Flow:**
```
LiveAudit → export_issues() → TeamCoherenceMonitor → fidelity_scores
```

---

### With PostMortem

**Purpose:** Import session analysis for historical context.

**Integration Pattern:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
from postmortem import PostMortem

monitor = TeamCoherenceMonitor()
pm = PostMortem()

# Analyze completed session
pm.analyze("session_log.json")
grades = pm.export_grades()

# Import agent grades
count = monitor.import_postmortem_data(grades)

# Historical performance informs current scoring
```

**Data Flow:**
```
PostMortem → analyze() → export_grades() → TeamCoherenceMonitor
```

---

### With SynapseLink

**Purpose:** Send coherence alerts to team.

**Integration Pattern:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
from synapselink import quick_send

monitor = TeamCoherenceMonitor()

# Check coherence
score = monitor.get_coherence_score()
alerts = monitor.check_all_alerts()

# Alert on issues
if score < 70:
    quick_send(
        "LOGAN,FORGE",
        f"Team Coherence Alert: {score}/100",
        f"Active alerts: {len(alerts)}\n" +
        "\n".join([f"- {a.message}" for a in alerts]),
        priority="HIGH"
    )
```

---

### With AgentHealth

**Purpose:** Correlate coherence with agent health metrics.

**Integration Pattern:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
from agenthealth import AgentHealth

monitor = TeamCoherenceMonitor()
health = AgentHealth()

# Use shared session ID
session_id = "session_xyz"
health.start_session("ATLAS", session_id=session_id)

# Track coherence alongside health
monitor.record_activity("ATLAS")

# Correlate data at session end
coherence_data = monitor.export_data()
health_data = health.get_session_summary("ATLAS", session_id)

# Combined analysis
print(f"Coherence: {coherence_data['coherence_score']}")
print(f"Health: {health_data['overall_health']}")
```

---

### With TaskQueuePro

**Purpose:** Track task completion rates.

**Integration Pattern:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
from taskqueuepro import TaskQueuePro

monitor = TeamCoherenceMonitor()
queue = TaskQueuePro()

# Create task
task_id = queue.create_task("Build widget", agent="ATLAS")
monitor.record_mention("ATLAS")

# On completion
queue.complete_task(task_id)
monitor.record_claim("ATLAS", correct=True)

# On failure
queue.fail_task(task_id)
monitor.record_claim("ATLAS", correct=False)
```

---

### With ContextCompressor

**Purpose:** Compress coherence reports for token efficiency.

**Integration Pattern:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor
from contextcompressor import ContextCompressor

monitor = TeamCoherenceMonitor()
compressor = ContextCompressor()

# Generate full report
report = monitor.format_dashboard()

# Compress for sharing
compressed = compressor.compress_text(
    report,
    query="team status",
    method="summary"
)

print(f"Original: {len(report)} chars")
print(f"Compressed: {len(compressed.compressed_text)} chars")
```

---

### With ConfigManager

**Purpose:** Centralize threshold configuration.

**Integration Pattern:**
```python
from teamcoherencemonitor import TeamCoherenceMonitor, Thresholds
from configmanager import ConfigManager

config = ConfigManager()

# Load shared thresholds
tcm_config = config.get("teamcoherencemonitor", {
    "latency_warning": 30.0,
    "latency_critical": 60.0,
    "ack_rate_warning": 80.0,
})

# Create thresholds from config
thresholds = Thresholds(**tcm_config)

# Initialize with config
monitor = TeamCoherenceMonitor(thresholds=thresholds)
```

---

## 🚀 ADOPTION ROADMAP

### Phase 1: Core Adoption (Week 1)

**Goal:** All agents aware and can use basic features.

**Steps:**
1. ✅ Tool deployed to GitHub
2. ☐ Quick-start guides sent via Synapse
3. ☐ Each agent tests basic workflow
4. ☐ Feedback collected

**Success Criteria:**
- All 5 agents have used tool at least once
- No blocking issues reported
- Basic CLI commands working

### Phase 2: Integration (Week 2-3)

**Goal:** Integrated into daily workflows.

**Steps:**
1. ☐ Add to agent startup routines
2. ☐ Integrate with MentionGuard, LiveAudit
3. ☐ Create BCH command handlers
4. ☐ Monitor usage patterns

**Success Criteria:**
- Used daily by at least 3 agents
- Integration with 2+ other tools working
- BCH commands functional

### Phase 3: Optimization (Week 4+)

**Goal:** Optimized and fully adopted.

**Steps:**
1. ☐ Collect efficiency metrics
2. ☐ Tune thresholds based on real data
3. ☐ Implement v1.1 improvements
4. ☐ Full Team Brain ecosystem integration

**Success Criteria:**
- Measurable coordination improvements
- All agents using regularly
- Integration with all coordination tools

---

## 📊 SUCCESS METRICS

### Adoption Metrics
- **Agent usage:** Track which agents use the tool
- **Daily sessions:** Number of monitoring sessions per day
- **Integration count:** Number of tool integrations active

### Efficiency Metrics
- **Time to detect:** How fast are coordination issues detected
- **Alert response:** Time to address alerts
- **Score improvements:** Trend in team coherence over time

### Quality Metrics
- **False positive rate:** Alerts that weren't real issues
- **False negative rate:** Issues missed by the tool
- **User satisfaction:** Agent feedback on usefulness

---

## 🛠️ TECHNICAL INTEGRATION DETAILS

### Import Paths

```python
# Main import
from teamcoherencemonitor import TeamCoherenceMonitor

# With thresholds
from teamcoherencemonitor import TeamCoherenceMonitor, Thresholds

# All components
from teamcoherencemonitor import (
    TeamCoherenceMonitor,
    Thresholds,
    AgentStatus,
    Alert,
    CoherenceSnapshot,
    CoherenceScorer,
    AlertSystem,
)
```

### Configuration Integration

**Config File:** `~/.teamcoherencemonitor/monitor_data.json`

**Shared Config Pattern:**
```json
{
  "teamcoherencemonitor": {
    "latency_warning": 30.0,
    "latency_critical": 60.0,
    "ack_rate_warning": 80.0,
    "ack_rate_critical": 60.0
  }
}
```

### Error Handling Integration

**Standardized Error Codes:**
- 0: Success
- 1: General error
- 2: Agent not found
- 3: Invalid threshold
- 4: Data persistence error

### Logging Integration

**Log Format:** Compatible with Team Brain standard

**Log Location:** Integrated with Python logging module

---

## 🔧 MAINTENANCE & SUPPORT

### Update Strategy
- **Minor updates (v1.x):** Monthly
- **Major updates (v2.0+):** Quarterly
- **Security patches:** Immediate

### Support Channels
- **GitHub Issues:** Bug reports and feature requests
- **Synapse:** Team Brain discussions
- **Direct:** Message ATLAS for complex issues

### Known Limitations
- Requires manual event recording (no auto-detection yet)
- Thresholds need tuning for each team
- Historical data limited to 1000 snapshots

---

## 📚 ADDITIONAL RESOURCES

- **Main Documentation:** [README.md](README.md)
- **Examples:** [EXAMPLES.md](EXAMPLES.md)
- **Quick Start:** [QUICK_START_GUIDES.md](QUICK_START_GUIDES.md)
- **Integration Examples:** [INTEGRATION_EXAMPLES.md](INTEGRATION_EXAMPLES.md)
- **Cheat Sheet:** [CHEAT_SHEET.txt](CHEAT_SHEET.txt)
- **GitHub:** https://github.com/DonkRonk17/TeamCoherenceMonitor

---

**Last Updated:** January 25, 2026  
**Maintained By:** ATLAS (Team Brain)
