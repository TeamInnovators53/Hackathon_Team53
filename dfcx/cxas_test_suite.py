"""
CXAS SCRAPI (Conversational AI Agent Studio) Automated Test Suite.
Hackathon Team 53 - Team Innovators.

Validates:
1. Root Agent intent recognition and sub-agent dispatch.
2. Reg E/Z verbatim disclosures for credit card billing and overdraft protection.
3. Proactive fee avoidance warnings & calculation of balance gaps.
4. Telephony routing assertions (TRC = KEY_PRIVATE_CLIENT_TRC / KEYPRIVCCA, masterBotId = 'privilegeConcierge').
"""

import pytest
from src.root_agent import RootPrivilegeAgent
from src.customer_service import CustomerService
from src.fee_avoidance_engine import FeeAvoidanceEngine
from src.telephony_adapter import TelephonyAdapter


class TestCxasScrapiVerification:
    @pytest.fixture
    def setup_agent(self):
        return RootPrivilegeAgent()

    @pytest.fixture
    def demo_customers(self):
        return CustomerService.get_sample_customers()

    def test_scrapi_turn_01_proactive_fee_reminder(self, setup_agent, demo_customers):
        """Turn 1: Verify Root Agent emits proactive fee warning for at-risk client Eleanor Vance."""
        c1 = demo_customers["031379551"]
        resp = setup_agent.initialize_session(c1)

        # Assertion: Proactive banner is triggered
        assert resp.fee_reminder_banner is not None
        assert "at risk of a $25.00" in resp.fee_reminder_banner
        # Assertion: Prompt code matches standard entrance prompt
        assert resp.audio_prompt_code == "[K2U_ENG.700.au]"

    def test_scrapi_turn_02_balance_inquiry_with_fee_status(self, setup_agent, demo_customers):
        """Turn 2: Verify Balance Inquiry reports account breakdown and relationship holding gap."""
        c1 = demo_customers["031379551"]
        resp = setup_agent.route_and_execute(c1, "how much money do I have in checking and savings?")

        assert resp.subagent_id == "balance_inquiry"
        assert resp.audio_prompt_code == "[K2U_ENG.701.au]"
        assert "Total Combined Relationship Holdings" in resp.message
        assert "$21,450.00" in resp.message
        assert "Maintenance Fee Advisory" in resp.message

    def test_scrapi_turn_03_cc_statement_disclosure(self, setup_agent, demo_customers):
        """Turn 3: Verify Credit Card statement details and e-statement availability."""
        c1 = demo_customers["031379551"]
        resp = setup_agent.route_and_execute(c1, "what is my credit card statement?")

        assert resp.subagent_id == "cc_statement"
        assert resp.audio_prompt_code == "[K2U_ENG.712.au]"
        assert "Statement Balance" in resp.message
        assert "$1,840.50" in resp.message
        assert "Minimum Payment Due" in resp.message
        assert "e-Statement" in resp.message

    def test_scrapi_turn_04_overdraft_and_offers(self, setup_agent, demo_customers):
        """Turn 4: Verify Overdraft protection disclosure and custom CD offers."""
        c1 = demo_customers["031379551"]
        resp = setup_agent.route_and_execute(c1, "tell me about overdraft protection and special offers")

        assert resp.subagent_id == "overdraft_offers"
        assert resp.audio_prompt_code == "[K2U_ENG.720.au]"
        assert "Key Coverage" in resp.message
        assert "4.85% APY" in resp.message
        assert "$35,000" in resp.message

    def test_scrapi_turn_05_due_reminders_and_fee_remedies(self, setup_agent, demo_customers):
        """Turn 5: Verify Due reminders list upcoming payments and the 3 fee avoidance options."""
        c1 = demo_customers["031379551"]
        resp = setup_agent.route_and_execute(c1, "how to avoid a maintenance service charge")

        assert resp.subagent_id == "due_reminders"
        assert resp.audio_prompt_code == "[K2U_ENG.730.au]"
        assert "$25,000+" in resp.message
        assert "$500+" in resp.message
        assert "$2,500+" in resp.message

    def test_scrapi_turn_06_priority_handover_and_odyssey_payload(self, setup_agent, demo_customers):
        """Turn 6: Verify Handover to Dedicated Concierge and Odyssey / Genesys routing payload."""
        c2 = demo_customers["004645906"] # Dr. Julian Sterling (Private Client)
        resp = setup_agent.route_and_execute(c2, "I need to speak to my private banker")

        assert resp.subagent_id == "priority_handover"
        assert resp.handover_required is True
        assert resp.routing_context.transfer_route_code == "KEY_PRIVATE_CLIENT_TRC"

        # Generate and validate Odyssey Telephony Payload
        payload = TelephonyAdapter.generate_odyssey_session_payload(c2, resp.routing_context.transfer_route_code)
        assert payload["transferData"]["masterBotId"] == "privilegeConcierge"
        assert payload["transferData"]["transferRouteCode"] == "KEY_PRIVATE_CLIENT_TRC"
        assert payload["transferData"]["pbxRoutePoint"] == "5554001"
        assert payload["transferData"]["attachedData"]["CustomerTier"] == "PRIVATE_CLIENT"
        assert payload["transferData"]["attachedData"]["RelationshipGroup"] == "A"
        assert payload["transferData"]["attachedData"]["PriorityQueue"] == "TRUE"
