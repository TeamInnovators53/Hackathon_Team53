"""
Functional test for Server API Handler and Root Agent JSON serialization.
Hackathon Team 53 - Team Innovators.
"""

import json
from src.root_agent import RootPrivilegeAgent
from src.customer_service import CustomerService
from src.fee_avoidance_engine import FeeAvoidanceEngine


def test_api_data_structures():
    agent = RootPrivilegeAgent()
    samples = CustomerService.get_sample_customers()
    profile = samples["031379551"]

    # Test initialization
    init_resp = agent.initialize_session(profile)
    assert init_resp.subagent_id == "root_agent"
    assert init_resp.fee_reminder_banner is not None

    # Test all DTMF options
    for digit in ["1", "2", "3", "4", "5", "6", "7"]:
        resp = agent.route_and_execute(profile, digit)
        assert resp.subagent_id != ""
        assert resp.message != ""

    # Test Fee Avoidance evaluation
    fee_stat = FeeAvoidanceEngine.evaluate(profile)
    assert fee_stat.total_combined_balance == 21450.0
    assert fee_stat.is_fee_waived is False
