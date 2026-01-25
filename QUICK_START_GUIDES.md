# TeamCoherenceMonitor - Quick Start Guides

## 📖 ABOUT THESE GUIDES

Each Team Brain agent has a **5-minute quick-start guide** tailored to their role and workflows.

**Choose your guide:**
- [Forge (Orchestrator)](#-forge-quick-start)
- [Atlas (Executor)](#-atlas-quick-start)
- [Clio (Linux Agent)](#-clio-quick-start)
- [Nexus (Multi-Platform)](#-nexus-quick-start)
- [Bolt (Free Executor)](#-bolt-quick-start)

---

## 🔥 FORGE QUICK START

**Role:** Orchestrator / Reviewer  
**Time:** 5 minutes  
**Goal:** Learn to monitor team coordination during orchestration sessions

### Step 1: Installation Check

```bash
# Verify TeamCoherenceMonitor is available
python teamcoherencemonitor.py --version

# Expected: teamcoherencemonitor 1.0
```

### Step 2: First Use - Session Monitoring

```python
# In your Forge session
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()

# Register session participants
for agent in ["ATLAS", "CLIO", "NEXUS", "BOLT"]:
    monitor.register_agent(agent)

# Get initial team score
score = monitor.get_coherence_score()
print(f"Session Start - Team Coherence: {score}/100")
```

### Step 3: Integration with Forge Workflows

**Use Case 1: Track Task Delegation**
```python
# When delegating a task
monitor.record_mention("ATLAS", acknowledged=False)

# When ATLAS responds
monitor.record_response("ATLAS", latency=3.5)
monitor.record_acknowledgment("ATLAS")

# Check if coordination is healthy
score = monitor.get_coherence_score()
if score < 70:
    print("[!] Coordination degrading - consider intervention")
```

**Use Case 2: End-of-Session Review**
```python
# At session end
snapshot = monitor.take_snapshot()
print(f"Final Score: {snapshot.overall_score}")

# Check for any issues
alerts = monitor.get_alerts()
for alert in alerts:
    print(f"  [{alert.severity}] {alert.message}")

# Save for records
monitor.save()
```

### Step 4: Common Forge Commands

```bash
# View team dashboard
python teamcoherencemonitor.py dashboard

# Check specific agent
python teamcoherencemonitor.py agent ATLAS

# View all alerts
python teamcoherencemonitor.py alerts

# Export session data
python teamcoherencemonitor.py export > session_coherence.json
```

### Next Steps for Forge

1. Read [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - Forge section
2. Try [EXAMPLES.md](EXAMPLES.md) - Example 7 (Session Monitoring)
3. Add to your orchestration startup routine

---

## ⚡ ATLAS QUICK START

**Role:** Executor / Builder  
**Time:** 5 minutes  
**Goal:** Learn to track coordination during tool builds

### Step 1: Installation Check

```bash
python -c "from teamcoherencemonitor import TeamCoherenceMonitor; print('[OK]')"
```

### Step 2: First Use - Self-Monitoring

```python
# In your Atlas session
from teamcoherencemonitor import TeamCoherenceMonitor
import time

monitor = TeamCoherenceMonitor()

# Register yourself
monitor.register_agent("ATLAS")

# Track when you're mentioned
mention_time = time.time()
monitor.record_mention("ATLAS", acknowledged=False)

# After you respond
response_time = time.time() - mention_time
monitor.record_response("ATLAS", latency=response_time)
monitor.record_acknowledgment("ATLAS")

# Check your score
metrics = monitor.get_agent_metrics("ATLAS")
print(f"ATLAS Score: {metrics['coherence_score']}")
```

### Step 3: Integration with Build Workflows

**During Tool Creation:**
```python
# Track build milestones
monitor.record_claim("ATLAS", correct=True)  # Milestone passed
monitor.record_activity("ATLAS")  # Still active

# At session end
print(monitor.format_dashboard(compact=True))
```

**Error Tracking:**
```python
# If you make an error
monitor.record_claim("ATLAS", correct=False)
monitor.record_error("ATLAS")
```

### Step 4: Common Atlas Commands

```bash
# Quick status
python teamcoherencemonitor.py score

# Your metrics
python teamcoherencemonitor.py agent ATLAS

# Record events
python teamcoherencemonitor.py record-response ATLAS 2.5
python teamcoherencemonitor.py record-claim ATLAS --correct
```

### Next Steps for Atlas

1. Integrate into Holy Grail automation
2. Add self-monitoring to tool build checklist
3. Track your performance over multiple sessions

---

## 🐧 CLIO QUICK START

**Role:** Linux / Ubuntu Agent  
**Time:** 5 minutes  
**Goal:** Learn to use TeamCoherenceMonitor in Linux environment

### Step 1: Linux Installation

```bash
# Clone from GitHub
git clone https://github.com/DonkRonk17/TeamCoherenceMonitor.git
cd TeamCoherenceMonitor

# Verify
python3 teamcoherencemonitor.py --version

# Add alias for convenience
echo 'alias tcm="python3 ~/TeamCoherenceMonitor/teamcoherencemonitor.py"' >> ~/.bashrc
source ~/.bashrc
```

### Step 2: First Use - CLI Monitoring

```bash
# Register yourself
tcm register CLIO

# Check team status
tcm dashboard

# Quick score check
tcm score
```

### Step 3: Integration with Clio Workflows

**Use Case: BCH CLI Monitoring**
```bash
# Before BCH session
tcm register FORGE
tcm register ATLAS
tcm register CLIO
tcm register NEXUS
tcm register BOLT

# During session (after events)
tcm record-mention CLIO --ack
tcm record-response CLIO 2.1

# Check status
tcm dashboard --compact
```

**Platform-Specific Features:**
- Data stored at `~/.teamcoherencemonitor/`
- Works in tmux/screen sessions
- Integrates with watch for continuous monitoring

### Step 4: Common Clio Commands

```bash
# Continuous monitoring (every 30 seconds)
watch -n 30 "python3 teamcoherencemonitor.py dashboard --compact"

# Export for analysis
tcm export | jq '.coherence_score'

# Alert check
tcm alerts --severity CRITICAL
```

### Next Steps for Clio

1. Add to ABIOS startup routine
2. Test with BCH CLI components
3. Create shell scripts for common patterns

---

## 🌐 NEXUS QUICK START

**Role:** Multi-Platform Agent  
**Time:** 5 minutes  
**Goal:** Learn cross-platform usage of TeamCoherenceMonitor

### Step 1: Platform Detection

```python
import platform
from teamcoherencemonitor import TeamCoherenceMonitor

monitor = TeamCoherenceMonitor()
print(f"Platform: {platform.system()}")
print(f"Data Dir: {monitor.data_dir}")
```

### Step 2: First Use - Cross-Platform Monitoring

```python
from teamcoherencemonitor import TeamCoherenceMonitor

# Works identically on Windows, Linux, macOS
monitor = TeamCoherenceMonitor()

# Register agents from multiple platforms
monitor.register_agent("CLIO")    # Linux
monitor.register_agent("IRIS")    # Desktop (Windows)
monitor.register_agent("PORTER")  # Mobile

# Track coordination
monitor.record_mention("CLIO", acknowledged=True)
monitor.record_mention("IRIS", acknowledged=True)

# Check overall coherence
score = monitor.get_coherence_score()
print(f"Cross-Platform Coherence: {score}")
```

### Step 3: Platform-Specific Considerations

**Windows:**
- Data: `C:\Users\<username>\.teamcoherencemonitor\`
- Use PowerShell or cmd for CLI

**Linux:**
- Data: `~/.teamcoherencemonitor/`
- Add alias to `.bashrc`

**macOS:**
- Data: `~/.teamcoherencemonitor/`
- Add alias to `.zshrc`

### Step 4: Common Nexus Commands

```bash
# Platform-agnostic commands
python teamcoherencemonitor.py dashboard
python teamcoherencemonitor.py score
python teamcoherencemonitor.py export

# Check specific agent
python teamcoherencemonitor.py agent CLIO
python teamcoherencemonitor.py agent IRIS
```

### Next Steps for Nexus

1. Test on all 3 platforms
2. Report platform-specific issues if any
3. Coordinate monitoring across platforms

---

## 🆓 BOLT QUICK START

**Role:** Free Executor (Cline + Grok)  
**Time:** 5 minutes  
**Goal:** Learn to use TeamCoherenceMonitor without API costs

### Step 1: Verify Free Access

```bash
# No API key required!
python teamcoherencemonitor.py --version

# All features available at zero cost
python teamcoherencemonitor.py --help
```

### Step 2: First Use - Lightweight Monitoring

```bash
# Quick status checks
python teamcoherencemonitor.py score
python teamcoherencemonitor.py alerts

# Register and track
python teamcoherencemonitor.py register BOLT
python teamcoherencemonitor.py record-mention BOLT --ack
```

### Step 3: Integration with Bolt Workflows

**Use Case: Periodic Health Checks**
```bash
# Add to cron or scheduled task
# Every 5 minutes, check coherence
python teamcoherencemonitor.py check
python teamcoherencemonitor.py score
```

**Batch Processing:**
```bash
# Generate status report
python teamcoherencemonitor.py export > /tmp/coherence.json

# Parse with jq (if available)
cat /tmp/coherence.json | jq '.coherence_score'
```

### Step 4: Common Bolt Commands

```bash
# Lightweight commands
python teamcoherencemonitor.py score
python teamcoherencemonitor.py alerts
python teamcoherencemonitor.py check

# Batch recording
python teamcoherencemonitor.py record-mention FORGE --ack
python teamcoherencemonitor.py record-response FORGE 3.0
python teamcoherencemonitor.py record-claim FORGE --correct
```

### Cost Considerations

- **Zero API costs** - Everything runs locally
- **No external dependencies** - Pure Python stdlib
- **Can run frequently** - No budget impact
- **Perfect for automation** - Scheduled health checks

### Next Steps for Bolt

1. Add to Cline workflows
2. Use for automated health monitoring
3. Report any issues via Synapse

---

## 📚 ADDITIONAL RESOURCES

**For All Agents:**
- Full Documentation: [README.md](README.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Integration Plan: [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md)
- Cheat Sheet: [CHEAT_SHEET.txt](CHEAT_SHEET.txt)

**Support:**
- GitHub Issues: https://github.com/DonkRonk17/TeamCoherenceMonitor/issues
- Synapse: Post in THE_SYNAPSE/active/
- Direct: Message ATLAS for complex issues

---

**Last Updated:** January 25, 2026  
**Maintained By:** ATLAS (Team Brain)
