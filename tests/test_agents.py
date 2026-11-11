"""
Unit & Integration tests for Root Agent and all 8 Sub-Agents.
Hackathon Team 53 - Team Innovators.
"""

import pytest
from src.root_agent import RootPrivilegeAgent
from src.customer_service import CustomerService
from src.models import Language, CustomerTier


@pytest.fixture
def agent():
    return RootPrivilegeAgent()


@pytest.fixture
def at_risk_profile():
    samples = CustomerService.get_sample_customers()
    return samples["031379551"] # Eleanor Vance (At Risk)


@pytest.fixture
def private_client_profile():
    samples = CustomerService.get_sample_customers()
    return samples["004645906"] # Dr. Julian Sterling (Private Client)


def test_root_agent_initialization(agent, at_risk_profile):
    resp = agent.initialize_session(at_risk_profile)
    assert resp.subagent_id == "root_agent"
    assert "Eleanor Vance" in resp.message
    # At-risk customer should have fee warning banner
    assert resp.fee_reminder_banner is not None
    assert "at risk of a $25.00" in resp.fee_reminder_banner


def test_dtmf_menu_routing(agent, at_risk_profile):
    # Press 1: Balance inquiry
    r1 = agent.route_and_execute(at_risk_profile, "1")
    assert r1.subagent_id == "balance_inquiry"
    assert "Account Balances" in r1.message

    # Press 2: Credit Card statement
    r2 = agent.route_and_execute(at_risk_profile, "2")
    assert r2.subagent_id == "cc_statement"
    assert "Statement Balance" in r2.message

    # Press 3: Overdraft & Offers
    r3 = agent.route_and_execute(at_risk_profile, "3")
    assert r3.subagent_id == "overdraft_offers"
    assert "4.85% APY" in r3.message

    # Press 4: Purchase History
    r4 = agent.route_and_execute(at_risk_profile, "4")
    assert r4.subagent_id == "purchase_recommendations"
    assert "Purchase History" in r4.message

    # Press 5: Due Reminders & Fee Avoidance
    r5 = agent.route_and_execute(at_risk_profile, "5")
    assert r5.subagent_id == "due_reminders"
    assert "Avoidance" in r5.message

    # Press 6: Dedicated Handover
    r6 = agent.route_and_execute(at_risk_profile, "6")
    assert r6.subagent_id == "priority_handover"
    assert r6.handover_required is True
    assert r6.routing_context.transfer_route_code == "KEYPRIVCCA"

    # Press 7: Language Selection
    r7 = agent.route_and_execute(at_risk_profile, "7")
    assert r7.subagent_id == "language_selection"
    assert at_risk_profile.preferred_language == Language.SPA


def test_natural_language_routing(agent, at_risk_profile):
    # Natural language: CC statement
    resp = agent.route_and_execute(at_risk_profile, "what is my credit card statement balance?")
    assert resp.subagent_id == "cc_statement"

    # Natural language: Balance inquiry
    resp = agent.route_and_execute(at_risk_profile, "how much money do I have in checking?")
    assert resp.subagent_id == "balance_inquiry"

    # Natural language: Priority Handover
    resp = agent.route_and_execute(at_risk_profile, "I need to speak to my private banker right now")
    assert resp.subagent_id == "priority_handover"
    assert resp.handover_required is True

    # Natural language: Fee avoidance rules
    resp = agent.route_and_execute(at_risk_profile, "how do I avoid the maintenance service charge?")
    assert resp.subagent_id == "due_reminders"
    assert "Maintenance Fee Avoidance Deadline" in resp.message


def test_private_client_priority_routing(agent, private_client_profile):
    resp = agent.route_and_execute(private_client_profile, "representative")
    assert resp.subagent_id == "priority_handover"
    assert resp.routing_context.transfer_route_code == "KEY_PRIVATE_CLIENT_TRC"
    assert resp.routing_context.genesys_attached_data["CustomerTier"] == "PRIVATE_CLIENT"
