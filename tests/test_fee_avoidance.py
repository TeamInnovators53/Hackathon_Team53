"""
Unit tests for Key Privilege Maintenance Service Charge Avoidance Engine.
Hackathon Team 53 - Team Innovators.
"""

import pytest
from src.customer_service import CustomerService
from src.fee_avoidance_engine import FeeAvoidanceEngine
from src.models import CustomerProfile, CustomerTier, Language, Account, AccountType


def test_rule1_combined_balance_exemption():
    """Customer with combined balance >= $25,000 has fee waived."""
    profile = CustomerProfile(
        customer_ipi="TEST-001",
        customer_name="Test Balanced",
        phone_number="5551234567",
        ssn_last4="1111",
        relationship_group="D",
        customer_tier=CustomerTier.PRIVILEGED,
        appl_type="KEYPRIV",
        sub_product_code="PQ",
        preferred_language=Language.ENG,
        is_key_at_work=False,
        accounts=[
            Account("A1", AccountType.CHECKING, "Checking", "0101", 15000.0, 15000.0, "2026-11-30"),
            Account("A2", AccountType.SAVINGS, "Savings", "0101", 12000.0, 12000.0, "2026-11-30")
        ]
    )
    status = FeeAvoidanceEngine.evaluate(profile)
    assert status.is_fee_waived is True
    assert status.rule1_met is True
    assert status.total_combined_balance == 27000.0
    assert status.proactive_warning_needed is False


def test_rule2_mortgage_autopay_exemption():
    """Customer with balance < $25k but mortgage auto-pay >= $500 has fee waived."""
    profile = CustomerProfile(
        customer_ipi="TEST-002",
        customer_name="Test Mortgage",
        phone_number="5551234568",
        ssn_last4="2222",
        relationship_group="C",
        customer_tier=CustomerTier.PRIVILEGED,
        appl_type="KEYPRIV",
        sub_product_code="PQ",
        preferred_language=Language.ENG,
        is_key_at_work=False,
        accounts=[
            Account(
                "A1", AccountType.CHECKING, "Checking", "0101", 8000.0, 8000.0, "2026-11-30",
                details={"mortgage_autopay_enabled": True, "mortgage_autopay_amount": 1200.0}
            ),
            Account("MTG1", AccountType.MORTGAGE, "Mortgage", "0101", 250000.0, 0.0, "2026-11-30")
        ]
    )
    status = FeeAvoidanceEngine.evaluate(profile)
    assert status.is_fee_waived is True
    assert status.rule2_met is True
    assert status.rule1_met is False  # 8000 < 25000


def test_rule3_key_at_work_direct_deposits_exemption():
    """Customer with balance < $25k but Key@Work direct deposits >= $2,500 has fee waived."""
    profile = CustomerProfile(
        customer_ipi="TEST-003",
        customer_name="Test KeyAtWork",
        phone_number="5551234569",
        ssn_last4="3333",
        relationship_group="B",
        customer_tier=CustomerTier.PRIVILEGED,
        appl_type="KEYPRIV",
        sub_product_code="PQ",
        preferred_language=Language.ENG,
        is_key_at_work=True,
        accounts=[
            Account(
                "A1", AccountType.CHECKING, "Checking", "0101", 9500.0, 9500.0, "2026-11-30",
                details={"cycle_direct_deposits": 2800.0}
            )
        ]
    )
    status = FeeAvoidanceEngine.evaluate(profile)
    assert status.is_fee_waived is True
    assert status.rule3_met is True
    assert status.rule1_met is False


def test_at_risk_customer_proactive_warning():
    """Customer failing all 3 rules triggers proactive fee warning and actionable advice."""
    profile = CustomerProfile(
        customer_ipi="TEST-004",
        customer_name="Test AtRisk",
        phone_number="5551234570",
        ssn_last4="4444",
        relationship_group="D",
        customer_tier=CustomerTier.PRIVILEGED,
        appl_type="KEYPRIV",
        sub_product_code="PQ",
        preferred_language=Language.ENG,
        is_key_at_work=True,
        accounts=[
            Account(
                "A1", AccountType.CHECKING, "Checking", "0101", 12000.0, 12000.0, "2026-11-20",
                details={"cycle_direct_deposits": 1100.0, "days_remaining": 6, "cycle_end": "2026-11-20"}
            )
        ]
    )
    status = FeeAvoidanceEngine.evaluate(profile)
    assert status.is_fee_waived is False
    assert status.proactive_warning_needed is True
    assert "at risk of a $25.00" in status.alert_message
    assert "Transfer or deposit $13,000.00" in status.actionable_remedy
    assert "direct deposits of $1,400.00" in status.actionable_remedy
