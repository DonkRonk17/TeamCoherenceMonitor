#!/usr/bin/env python3
"""
Comprehensive test suite for TeamCoherenceMonitor.

Tests cover:
- Core functionality (agent management, metric recording)
- Coherence scoring
- Alert system
- Integration methods
- Edge cases
- CLI commands

Run: python test_teamcoherencemonitor.py
"""

import unittest
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from teamcoherencemonitor import (
    TeamCoherenceMonitor,
    AgentStatus,
    Alert,
    CoherenceSnapshot,
    Thresholds,
    CoherenceScorer,
    AlertSystem,
)


class TestAgentStatus(unittest.TestCase):
    """Test AgentStatus data class."""
    
    def test_initialization(self):
        """Test agent status initializes correctly."""
        agent = AgentStatus(name="FORGE")
        self.assertEqual(agent.name, "FORGE")
        self.assertEqual(agent.mentions_received, 0)
        self.assertEqual(agent.mentions_acknowledged, 0)
        self.assertFalse(agent.is_active)
    
    def test_ack_rate_no_mentions(self):
        """Test ack rate with no mentions returns 100%."""
        agent = AgentStatus(name="FORGE")
        self.assertEqual(agent.ack_rate(), 100.0)
    
    def test_ack_rate_calculation(self):
        """Test ack rate calculation."""
        agent = AgentStatus(name="FORGE")
        agent.mentions_received = 10
        agent.mentions_acknowledged = 8
        self.assertEqual(agent.ack_rate(), 80.0)
    
    def test_ack_rate_zero(self):
        """Test ack rate with no acknowledgments."""
        agent = AgentStatus(name="FORGE")
        agent.mentions_received = 5
        agent.mentions_acknowledged = 0
        self.assertEqual(agent.ack_rate(), 0.0)
    
    def test_avg_latency_no_data(self):
        """Test avg latency with no data returns 0."""
        agent = AgentStatus(name="FORGE")
        self.assertEqual(agent.avg_latency(), 0.0)
    
    def test_avg_latency_calculation(self):
        """Test avg latency calculation."""
        agent = AgentStatus(name="FORGE")
        agent.response_latencies = [2.0, 3.0, 5.0]
        self.assertAlmostEqual(agent.avg_latency(), 10.0 / 3)
    
    def test_context_fidelity_no_claims(self):
        """Test context fidelity with no claims returns 100%."""
        agent = AgentStatus(name="FORGE")
        self.assertEqual(agent.context_fidelity(), 100.0)
    
    def test_context_fidelity_calculation(self):
        """Test context fidelity calculation."""
        agent = AgentStatus(name="FORGE")
        agent.total_claims = 10
        agent.correct_claims = 9
        self.assertEqual(agent.context_fidelity(), 90.0)
    
    def test_to_dict_and_from_dict(self):
        """Test serialization roundtrip."""
        agent = AgentStatus(
            name="FORGE",
            last_seen=datetime.now(),
            is_active=True,
            response_latencies=[1.0, 2.0],
            mentions_received=5,
            mentions_acknowledged=4,
        )
        
        data = agent.to_dict()
        restored = AgentStatus.from_dict(data)
        
        self.assertEqual(restored.name, agent.name)
        self.assertEqual(restored.is_active, agent.is_active)
        self.assertEqual(restored.mentions_received, agent.mentions_received)


class TestThresholds(unittest.TestCase):
    """Test Thresholds configuration."""
    
    def test_default_values(self):
        """Test default threshold values."""
        thresholds = Thresholds()
        self.assertEqual(thresholds.latency_warning, 30.0)
        self.assertEqual(thresholds.latency_critical, 60.0)
        self.assertEqual(thresholds.ack_rate_warning, 80.0)
        self.assertEqual(thresholds.ack_rate_critical, 60.0)
    
    def test_custom_values(self):
        """Test custom threshold values."""
        thresholds = Thresholds(latency_warning=20.0, latency_critical=40.0)
        self.assertEqual(thresholds.latency_warning, 20.0)
        self.assertEqual(thresholds.latency_critical, 40.0)
    
    def test_serialization(self):
        """Test threshold serialization."""
        thresholds = Thresholds(latency_warning=15.0)
        data = thresholds.to_dict()
        restored = Thresholds.from_dict(data)
        self.assertEqual(restored.latency_warning, 15.0)


class TestCoherenceScorer(unittest.TestCase):
    """Test CoherenceScorer class."""
    
    def setUp(self):
        """Set up test scorer."""
        self.thresholds = Thresholds()
        self.scorer = CoherenceScorer(self.thresholds)
    
    def test_score_latency_zero(self):
        """Test latency scoring with zero latency."""
        score = self.scorer.score_latency(0)
        self.assertEqual(score, 100.0)
    
    def test_score_latency_excellent(self):
        """Test latency scoring with excellent latency."""
        score = self.scorer.score_latency(2.0)
        self.assertEqual(score, 100.0)
    
    def test_score_latency_critical(self):
        """Test latency scoring at critical threshold."""
        score = self.scorer.score_latency(60.0)
        self.assertEqual(score, 0.0)
    
    def test_score_latency_midrange(self):
        """Test latency scoring in midrange."""
        score = self.scorer.score_latency(30.0)
        self.assertGreater(score, 0.0)
        self.assertLess(score, 100.0)
    
    def test_score_activity_recent(self):
        """Test activity scoring for recent activity."""
        score = self.scorer.score_activity(10)
        self.assertEqual(score, 100.0)
    
    def test_score_activity_inactive(self):
        """Test activity scoring for inactive agent."""
        score = self.scorer.score_activity(300)
        self.assertEqual(score, 0.0)
    
    def test_calculate_agent_score(self):
        """Test agent score calculation."""
        agent = AgentStatus(name="FORGE")
        agent.last_seen = datetime.now()
        agent.response_latencies = [2.0]
        agent.mentions_received = 10
        agent.mentions_acknowledged = 10
        
        score = self.scorer.calculate_agent_score(agent)
        self.assertGreaterEqual(score, 90.0)  # All metrics excellent
    
    def test_calculate_team_score_empty(self):
        """Test team score with no agents."""
        score, agent_scores = self.scorer.calculate_team_score({})
        self.assertEqual(score, 100.0)
        self.assertEqual(agent_scores, {})
    
    def test_calculate_team_score_multiple_agents(self):
        """Test team score with multiple agents."""
        agents = {
            'FORGE': AgentStatus(name='FORGE'),
            'ATLAS': AgentStatus(name='ATLAS'),
        }
        agents['FORGE'].last_seen = datetime.now()
        agents['ATLAS'].last_seen = datetime.now()
        
        score, agent_scores = self.scorer.calculate_team_score(agents)
        self.assertIn('FORGE', agent_scores)
        self.assertIn('ATLAS', agent_scores)
        self.assertIsInstance(score, float)


class TestAlertSystem(unittest.TestCase):
    """Test AlertSystem class."""
    
    def setUp(self):
        """Set up test alert system."""
        self.thresholds = Thresholds()
        self.alerts = AlertSystem(self.thresholds)
    
    def test_check_agent_no_alerts(self):
        """Test agent check with no issues."""
        agent = AgentStatus(name="FORGE")
        agent.last_seen = datetime.now()
        
        alerts = self.alerts.check_agent(agent)
        self.assertEqual(len(alerts), 0)
    
    def test_check_agent_low_ack_rate(self):
        """Test alert on low acknowledgment rate."""
        agent = AgentStatus(name="FORGE")
        agent.mentions_received = 10
        agent.mentions_acknowledged = 5  # 50%
        
        alerts = self.alerts.check_agent(agent)
        self.assertTrue(any(a.metric == 'ack_rate' for a in alerts))
    
    def test_check_agent_high_latency(self):
        """Test alert on high latency."""
        agent = AgentStatus(name="FORGE")
        agent.response_latencies = [70.0]  # Above critical
        
        alerts = self.alerts.check_agent(agent)
        self.assertTrue(any(a.metric == 'latency' for a in alerts))
    
    def test_check_agent_low_fidelity(self):
        """Test alert on low context fidelity."""
        agent = AgentStatus(name="FORGE")
        agent.total_claims = 10
        agent.correct_claims = 5  # 50%
        
        alerts = self.alerts.check_agent(agent)
        self.assertTrue(any(a.metric == 'fidelity' for a in alerts))
    
    def test_check_agent_inactive(self):
        """Test alert on inactive agent."""
        agent = AgentStatus(name="FORGE")
        agent.last_seen = datetime.now() - timedelta(minutes=10)
        
        alerts = self.alerts.check_agent(agent)
        self.assertTrue(any(a.metric == 'activity' for a in alerts))
    
    def test_check_team_coherence_ok(self):
        """Test no alert on good coherence score."""
        alert = self.alerts.check_team_coherence(85.0)
        self.assertIsNone(alert)
    
    def test_check_team_coherence_warning(self):
        """Test warning on low coherence score."""
        alert = self.alerts.check_team_coherence(70.0)
        self.assertIsNotNone(alert)
        self.assertEqual(alert.severity, 'WARNING')
    
    def test_check_team_coherence_critical(self):
        """Test critical on very low coherence score."""
        alert = self.alerts.check_team_coherence(40.0)
        self.assertIsNotNone(alert)
        self.assertEqual(alert.severity, 'CRITICAL')
    
    def test_process_alerts(self):
        """Test alert processing."""
        alert = Alert(
            timestamp=datetime.now(),
            severity='WARNING',
            agent='FORGE',
            metric='ack_rate',
            message='Test alert',
            value=75.0,
            threshold=80.0,
        )
        
        self.alerts.process_alerts([alert])
        self.assertEqual(len(self.alerts.active_alerts), 1)
        self.assertEqual(len(self.alerts.alert_history), 1)
    
    def test_clear_alerts(self):
        """Test clearing alerts."""
        alert = Alert(
            timestamp=datetime.now(),
            severity='WARNING',
            agent='FORGE',
            metric='ack_rate',
            message='Test alert',
            value=75.0,
            threshold=80.0,
        )
        
        self.alerts.process_alerts([alert])
        cleared = self.alerts.clear_alerts(agent='FORGE')
        self.assertEqual(cleared, 1)
        self.assertEqual(len(self.alerts.active_alerts), 0)


class TestTeamCoherenceMonitor(unittest.TestCase):
    """Test TeamCoherenceMonitor main class."""
    
    def setUp(self):
        """Set up test monitor with temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = TeamCoherenceMonitor(
            data_dir=Path(self.temp_dir),
            auto_load=False,
        )
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test monitor initializes correctly."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(len(self.monitor.agents), 0)
    
    def test_register_agent(self):
        """Test agent registration."""
        agent = self.monitor.register_agent("FORGE")
        self.assertEqual(agent.name, "FORGE")
        self.assertIn("FORGE", self.monitor.agents)
    
    def test_register_agent_case_insensitive(self):
        """Test agent registration is case insensitive."""
        self.monitor.register_agent("forge")
        self.assertIn("FORGE", self.monitor.agents)
    
    def test_register_agent_idempotent(self):
        """Test registering same agent twice."""
        agent1 = self.monitor.register_agent("FORGE")
        agent2 = self.monitor.register_agent("FORGE")
        self.assertEqual(agent1, agent2)
        self.assertEqual(len(self.monitor.agents), 1)
    
    def test_unregister_agent(self):
        """Test agent unregistration."""
        self.monitor.register_agent("FORGE")
        result = self.monitor.unregister_agent("FORGE")
        self.assertTrue(result)
        self.assertNotIn("FORGE", self.monitor.agents)
    
    def test_unregister_nonexistent_agent(self):
        """Test unregistering nonexistent agent."""
        result = self.monitor.unregister_agent("NONEXISTENT")
        self.assertFalse(result)
    
    def test_get_agent(self):
        """Test getting agent."""
        self.monitor.register_agent("FORGE")
        agent = self.monitor.get_agent("FORGE")
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "FORGE")
    
    def test_get_agent_not_found(self):
        """Test getting nonexistent agent."""
        agent = self.monitor.get_agent("NONEXISTENT")
        self.assertIsNone(agent)
    
    def test_list_agents(self):
        """Test listing agents."""
        self.monitor.register_agent("FORGE")
        self.monitor.register_agent("ATLAS")
        agents = self.monitor.list_agents()
        self.assertEqual(set(agents), {"FORGE", "ATLAS"})
    
    def test_record_activity(self):
        """Test recording activity."""
        self.monitor.record_activity("FORGE")
        agent = self.monitor.get_agent("FORGE")
        self.assertIsNotNone(agent.last_seen)
        self.assertTrue(agent.is_active)
    
    def test_record_mention(self):
        """Test recording mention."""
        self.monitor.record_mention("FORGE", acknowledged=False)
        agent = self.monitor.get_agent("FORGE")
        self.assertEqual(agent.mentions_received, 1)
        self.assertEqual(agent.mentions_acknowledged, 0)
    
    def test_record_mention_acknowledged(self):
        """Test recording acknowledged mention."""
        self.monitor.record_mention("FORGE", acknowledged=True)
        agent = self.monitor.get_agent("FORGE")
        self.assertEqual(agent.mentions_received, 1)
        self.assertEqual(agent.mentions_acknowledged, 1)
    
    def test_record_acknowledgment(self):
        """Test recording acknowledgment."""
        self.monitor.record_acknowledgment("FORGE")
        agent = self.monitor.get_agent("FORGE")
        self.assertEqual(agent.mentions_acknowledged, 1)
    
    def test_record_response(self):
        """Test recording response."""
        self.monitor.record_response("FORGE", 2.5)
        agent = self.monitor.get_agent("FORGE")
        self.assertEqual(len(agent.response_latencies), 1)
        self.assertEqual(agent.response_latencies[0], 2.5)
        self.assertEqual(agent.messages_sent, 1)
    
    def test_record_response_limits_history(self):
        """Test response history is limited to 100."""
        for i in range(150):
            self.monitor.record_response("FORGE", float(i))
        
        agent = self.monitor.get_agent("FORGE")
        self.assertEqual(len(agent.response_latencies), 100)
    
    def test_record_claim(self):
        """Test recording claim."""
        self.monitor.record_claim("FORGE", correct=True)
        agent = self.monitor.get_agent("FORGE")
        self.assertEqual(agent.total_claims, 1)
        self.assertEqual(agent.correct_claims, 1)
    
    def test_record_incorrect_claim(self):
        """Test recording incorrect claim."""
        self.monitor.record_claim("FORGE", correct=False)
        agent = self.monitor.get_agent("FORGE")
        self.assertEqual(agent.total_claims, 1)
        self.assertEqual(agent.correct_claims, 0)
    
    def test_record_error(self):
        """Test recording error."""
        self.monitor.record_error("FORGE")
        agent = self.monitor.get_agent("FORGE")
        self.assertEqual(agent.errors_detected, 1)
    
    def test_get_coherence_score(self):
        """Test getting coherence score."""
        self.monitor.register_agent("FORGE")
        score = self.monitor.get_coherence_score()
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_get_agent_scores(self):
        """Test getting agent scores."""
        self.monitor.register_agent("FORGE")
        self.monitor.register_agent("ATLAS")
        scores = self.monitor.get_agent_scores()
        self.assertIn("FORGE", scores)
        self.assertIn("ATLAS", scores)
    
    def test_get_agent_metrics(self):
        """Test getting agent metrics."""
        self.monitor.record_response("FORGE", 2.5)
        metrics = self.monitor.get_agent_metrics("FORGE")
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['name'], "FORGE")
        self.assertIn('coherence_score', metrics)
    
    def test_get_agent_metrics_not_found(self):
        """Test getting metrics for nonexistent agent."""
        metrics = self.monitor.get_agent_metrics("NONEXISTENT")
        self.assertIsNone(metrics)
    
    def test_take_snapshot(self):
        """Test taking snapshot."""
        self.monitor.register_agent("FORGE")
        snapshot = self.monitor.take_snapshot()
        self.assertIsInstance(snapshot, CoherenceSnapshot)
        self.assertIsNotNone(snapshot.timestamp)
        self.assertEqual(snapshot.total_agents, 1)
    
    def test_get_trend_insufficient_data(self):
        """Test getting trend with insufficient data."""
        trend = self.monitor.get_trend()
        self.assertEqual(trend['trend'], 'STABLE')
    
    def test_check_all_alerts(self):
        """Test checking all alerts."""
        self.monitor.register_agent("FORGE")
        alerts = self.monitor.check_all_alerts()
        self.assertIsInstance(alerts, list)
    
    def test_get_alerts(self):
        """Test getting alerts."""
        alerts = self.monitor.get_alerts()
        self.assertIsInstance(alerts, list)
    
    def test_clear_alerts(self):
        """Test clearing alerts."""
        cleared = self.monitor.clear_alerts()
        self.assertEqual(cleared, 0)
    
    def test_format_dashboard(self):
        """Test formatting dashboard."""
        self.monitor.register_agent("FORGE")
        dashboard = self.monitor.format_dashboard()
        self.assertIn("TEAM COHERENCE MONITOR", dashboard)
        self.assertIn("FORGE", dashboard)
    
    def test_format_dashboard_compact(self):
        """Test formatting compact dashboard."""
        self.monitor.register_agent("FORGE")
        dashboard = self.monitor.format_dashboard(compact=True)
        self.assertIn("TEAM COHERENCE MONITOR", dashboard)
    
    def test_export_data(self):
        """Test exporting data."""
        self.monitor.register_agent("FORGE")
        self.monitor.record_response("FORGE", 2.5)
        
        data = self.monitor.export_data()
        self.assertIn('coherence_score', data)
        self.assertIn('agents', data)
        self.assertIn('FORGE', data['agents'])
    
    def test_save_and_load(self):
        """Test saving and loading data."""
        self.monitor.register_agent("FORGE")
        self.monitor.record_response("FORGE", 2.5)
        self.monitor.save()
        
        # Create new monitor that auto-loads
        monitor2 = TeamCoherenceMonitor(
            data_dir=Path(self.temp_dir),
            auto_load=True,
        )
        
        self.assertIn("FORGE", monitor2.agents)
    
    def test_reset(self):
        """Test resetting monitor."""
        self.monitor.register_agent("FORGE")
        self.monitor.record_response("FORGE", 2.5)
        self.monitor.reset()
        
        self.assertEqual(len(self.monitor.agents), 0)


class TestIntegration(unittest.TestCase):
    """Test integration methods."""
    
    def setUp(self):
        """Set up test monitor."""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = TeamCoherenceMonitor(
            data_dir=Path(self.temp_dir),
            auto_load=False,
        )
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_import_mentionguard_data(self):
        """Test importing MentionGuard data."""
        data = {
            'events': [
                {'agent': 'FORGE', 'acknowledged': True},
                {'agent': 'ATLAS', 'acknowledged': False},
            ]
        }
        
        count = self.monitor.import_mentionguard_data(data)
        self.assertEqual(count, 2)
        
        forge = self.monitor.get_agent("FORGE")
        self.assertEqual(forge.mentions_received, 1)
        self.assertEqual(forge.mentions_acknowledged, 1)
    
    def test_import_liveaudit_data(self):
        """Test importing LiveAudit data."""
        data = {
            'issues': [
                {'agent': 'FORGE', 'issue_type': 'false_claim'},
                {'agent': 'FORGE', 'issue_type': 'missed_mention'},
            ]
        }
        
        count = self.monitor.import_liveaudit_data(data)
        self.assertEqual(count, 2)
        
        forge = self.monitor.get_agent("FORGE")
        self.assertEqual(forge.errors_detected, 2)
    
    def test_import_postmortem_data(self):
        """Test importing PostMortem data."""
        data = {
            'agent_grades': [
                {'agent': 'FORGE', 'grade': 90, 'claims_made': 10},
                {'agent': 'ATLAS', 'grade': 80, 'claims_made': 5},
            ]
        }
        
        count = self.monitor.import_postmortem_data(data)
        self.assertEqual(count, 2)
        
        forge = self.monitor.get_agent("FORGE")
        self.assertEqual(forge.total_claims, 10)
        self.assertEqual(forge.correct_claims, 9)  # 90% of 10


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test monitor."""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = TeamCoherenceMonitor(
            data_dir=Path(self.temp_dir),
            auto_load=False,
        )
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_agents(self):
        """Test operations with no agents."""
        score = self.monitor.get_coherence_score()
        self.assertEqual(score, 100.0)
        
        scores = self.monitor.get_agent_scores()
        self.assertEqual(scores, {})
    
    def test_agent_with_no_activity(self):
        """Test agent with no activity."""
        self.monitor.register_agent("FORGE")
        score = self.monitor.get_coherence_score()
        # Should have some penalty for no activity
        self.assertIsInstance(score, float)
    
    def test_many_agents(self):
        """Test with many agents."""
        for i in range(20):
            self.monitor.register_agent(f"AGENT_{i}")
        
        score = self.monitor.get_coherence_score()
        self.assertIsInstance(score, float)
        
        dashboard = self.monitor.format_dashboard()
        self.assertIn("AGENT_0", dashboard)
    
    def test_special_characters_in_agent_name(self):
        """Test agent names are uppercased."""
        self.monitor.register_agent("forge_v2")
        self.assertIn("FORGE_V2", self.monitor.agents)
    
    def test_negative_latency_handled(self):
        """Test negative latency is handled."""
        self.monitor.record_response("FORGE", -1.0)
        agent = self.monitor.get_agent("FORGE")
        # Should still record the latency
        self.assertIn(-1.0, agent.response_latencies)
    
    def test_very_high_latency(self):
        """Test very high latency."""
        self.monitor.record_response("FORGE", 1000.0)
        score = self.monitor.get_coherence_score()
        self.assertLess(score, 100.0)
    
    def test_alert_serialization(self):
        """Test alert to/from dict."""
        alert = Alert(
            timestamp=datetime.now(),
            severity='CRITICAL',
            agent='FORGE',
            metric='ack_rate',
            message='Test',
            value=50.0,
            threshold=60.0,
        )
        
        data = alert.to_dict()
        restored = Alert.from_dict(data)
        
        self.assertEqual(restored.severity, alert.severity)
        self.assertEqual(restored.agent, alert.agent)


class TestCLI(unittest.TestCase):
    """Test CLI commands."""
    
    def setUp(self):
        """Set up test monitor."""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = TeamCoherenceMonitor(
            data_dir=Path(self.temp_dir),
            auto_load=False,
        )
    
    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_dashboard_command(self):
        """Test dashboard output."""
        self.monitor.register_agent("FORGE")
        output = self.monitor.format_dashboard()
        
        # Check key elements
        self.assertIn("TEAM COHERENCE MONITOR", output)
        self.assertIn("Score:", output)
        self.assertIn("FORGE", output)
    
    def test_compact_dashboard(self):
        """Test compact dashboard output."""
        self.monitor.register_agent("FORGE")
        output = self.monitor.format_dashboard(compact=True)
        
        self.assertIn("TEAM COHERENCE MONITOR", output)
        self.assertIn("Agents:", output)
    
    def test_export_json_valid(self):
        """Test export produces valid JSON."""
        self.monitor.register_agent("FORGE")
        self.monitor.record_response("FORGE", 2.5)
        
        data = self.monitor.export_data()
        json_str = json.dumps(data)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        self.assertIn('coherence_score', parsed)


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests with nice output."""
    print("=" * 70)
    print("TESTING: TeamCoherenceMonitor v1.0")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAgentStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestThresholds))
    suite.addTests(loader.loadTestsFromTestCase(TestCoherenceScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestTeamCoherenceMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestCLI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {result.testsRun} tests")
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"[OK] Passed: {passed}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[X] Errors: {len(result.errors)}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
