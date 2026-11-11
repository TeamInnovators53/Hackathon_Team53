"""
Customer Profile & Relationship Group Identification Service.
Hackathon Team 53 - Team Innovators.

Maps customers to KeyBank Relationship Groups (A-H), validates Key Privilege / Private Client status,
and provides sample profiles for Hackathon demonstration and live voice/chat testing.
"""

from typing import Dict, List, Optional
from src.models import (
    CustomerProfile, CustomerTier, Language, Account, AccountType, Transaction
)
from src.fee_avoidance_engine import FeeAvoidanceEngine


class CustomerService:
    """
    Identifies privileged customers based on Relationship Group mapping (A-H)
    and Application Type ('KEYPRIV', sub-product 'PQ', 'PRIVBANK').
    """

    # Official KeyBank Household Relationship Groups eligible for Primacy / Key Privilege benefits
    PRIVILEGE_RELATIONSHIP_GROUPS = {"A", "B", "C", "D", "E", "F", "G", "H"}

    @classmethod
    def is_privileged_customer(cls, relationship_group: str, appl_type: str = "KEYPRIV", sub_product: str = "PQ") -> bool:
        """
        Determines if caller qualifies for Key Privilege / Private Client treatment.
        """
        if appl_type in {"KEYPRIV", "PRIVBANK"}:
            return True
        if sub_product == "PQ":
            return True
        return relationship_group.upper() in cls.PRIVILEGE_RELATIONSHIP_GROUPS

    @classmethod
    def get_tier(cls, relationship_group: str, appl_type: str, total_balance: float) -> CustomerTier:
        if appl_type == "PRIVBANK" or relationship_group in {"A", "B"} or total_balance >= 250000.0:
            return CustomerTier.PRIVATE_CLIENT
        if cls.is_privileged_customer(relationship_group, appl_type):
            return CustomerTier.PRIVILEGED
        return CustomerTier.STANDARD

    @classmethod
    def get_sample_customers(cls) -> Dict[str, CustomerProfile]:
        """
        Returns pre-configured customer profiles for hackathon demo scenarios.
        """
        customers = {}

        # ----------------------------------------------------------------------------------
        # Scenario 1: AT-RISK PRIVILEGED CUSTOMER (Triggers Proactive Fee Avoidance Reminders!)
        # Group D, Balance $21,450 (Needs $3,550 to hit $25k), Key@Work $1,200 ($1,300 short)
        # ----------------------------------------------------------------------------------
        c1 = CustomerProfile(
            customer_ipi="031379551",
            customer_name="Eleanor Vance",
            phone_number="3854569511",
            ssn_last4="3584",
            relationship_group="D",
            customer_tier=CustomerTier.PRIVILEGED,
            appl_type="KEYPRIV",
            sub_product_code="PQ",
            preferred_language=Language.ENG,
            is_key_at_work=True,
            accounts=[
                Account(
                    account_number="4042250101",
                    prod_code=AccountType.CHECKING,
                    account_name="Key Privilege Checking",
                    bank_number="0101",
                    current_balance=14250.00,
                    available_balance=14200.00,
                    statement_cycle_date="2026-11-20",
                    details={
                        "cycle_start": "2026-10-21",
                        "cycle_end": "2026-11-20",
                        "days_remaining": 5,
                        "mortgage_autopay_enabled": False,
                        "mortgage_autopay_amount": 0.0,
                        "cycle_direct_deposits": 1200.00, # Less than $2,500 target!
                        "overdraft_protection": True,
                        "overdraft_backup_account": "Relationship Savings (*7702)"
                    }
                ),
                Account(
                    account_number="4042257702",
                    prod_code=AccountType.SAVINGS,
                    account_name="Relationship High-Yield Savings",
                    bank_number="0101",
                    current_balance=7200.00,
                    available_balance=7200.00,
                    statement_cycle_date="2026-11-20"
                ),
                Account(
                    account_number="5229063980757605",
                    prod_code=AccountType.CREDIT_CARD,
                    account_name="KeyBank Latitude Privilege Card",
                    bank_number="0101",
                    current_balance=-1840.50,
                    available_balance=13159.50,
                    statement_cycle_date="2026-11-25",
                    details={
                        "credit_limit": 15000.00,
                        "statement_balance": 1840.50,
                        "minimum_payment_due": 45.00,
                        "payment_due_date": "2026-11-28",
                        "reward_points": 24850,
                        "cashback_available": 248.50,
                        "apr": 16.24
                    }
                )
            ],
            recent_transactions=[
                Transaction("TXN-101", "4042250101", "2026-11-08", "Whole Foods Market", 142.80, "Groceries", reward_points_earned=285),
                Transaction("TXN-102", "4042250101", "2026-11-06", "Four Seasons Hotel Dining", 385.00, "Dining", reward_points_earned=1155),
                Transaction("TXN-103", "4042250101", "2026-11-04", "Nordstrom Westlake", 210.45, "Luxury Retail", reward_points_earned=420),
                Transaction("TXN-104", "4042250101", "2026-11-01", "Key@Work Payroll Direct Deposit", 1200.00, "Deposit"),
                Transaction("TXN-105", "5229063980757605", "2026-11-09", "Delta Air Lines First Class Upgrade", 620.00, "Travel", reward_points_earned=1860)
            ]
        )
        FeeAvoidanceEngine.evaluate(c1)
        customers[c1.customer_ipi] = c1

        # ----------------------------------------------------------------------------------
        # Scenario 2: PRIVATE CLIENT - ULTRA HIGH NET WORTH (Fee Waived via $25k+ Combined Balance)
        # Group A, Balance $245,000 (Waived), Investment Portfolio, Custom Premium Lending
        # ----------------------------------------------------------------------------------
        c2 = CustomerProfile(
            customer_ipi="004645906",
            customer_name="Dr. Julian Sterling",
            phone_number="3307148766",
            ssn_last4="8210",
            relationship_group="A",
            customer_tier=CustomerTier.PRIVATE_CLIENT,
            appl_type="PRIVBANK",
            sub_product_code="PQ",
            preferred_language=Language.ENG,
            is_key_at_work=False,
            accounts=[
                Account(
                    account_number="404225056",
                    prod_code=AccountType.CHECKING,
                    account_name="Key Private Client Checking",
                    bank_number="0101",
                    current_balance=45200.00,
                    available_balance=45200.00,
                    statement_cycle_date="2026-11-30",
                    details={
                        "cycle_start": "2026-11-01",
                        "cycle_end": "2026-11-30",
                        "days_remaining": 19,
                        "mortgage_autopay_enabled": False,
                        "cycle_direct_deposits": 0.0,
                        "dedicated_advisor": "Victoria Reynolds, CFP® (Chagrin Falls Wealth Center)"
                    }
                ),
                Account(
                    account_number="4042259910",
                    prod_code=AccountType.MONEY_MARKET,
                    account_name="Key Private Tier Money Market",
                    bank_number="0101",
                    current_balance=125000.00,
                    available_balance=125000.00,
                    statement_cycle_date="2026-11-30"
                ),
                Account(
                    account_number="5144746867062196",
                    prod_code=AccountType.CREDIT_CARD,
                    account_name="KeyBank World Elite Mastercard",
                    bank_number="0101",
                    current_balance=-3420.00,
                    available_balance=46580.00,
                    statement_cycle_date="2026-11-28",
                    details={
                        "credit_limit": 50000.00,
                        "statement_balance": 3420.00,
                        "minimum_payment_due": 75.00,
                        "payment_due_date": "2026-12-02",
                        "reward_points": 182400,
                        "cashback_available": 1824.00,
                        "apr": 14.25
                    }
                )
            ],
            recent_transactions=[
                Transaction("TXN-201", "404225056", "2026-11-07", "Ritz-Carlton Club & Spa", 1250.00, "Luxury Travel", reward_points_earned=3750),
                Transaction("TXN-202", "404225056", "2026-11-05", "Sotheby's Auction Gallery", 4200.00, "Art & Collectibles", reward_points_earned=8400)
            ]
        )
        FeeAvoidanceEngine.evaluate(c2)
        customers[c2.customer_ipi] = c2

        # ----------------------------------------------------------------------------------
        # Scenario 3: PRIVILEGED CUSTOMER (Fee Waived via KeyBank Mortgage Auto-Deduction $1,450/mo)
        # Group C, Balance $18,200 (< $25k), but has Mortgage Auto-Pay of $1,450/mo
        # ----------------------------------------------------------------------------------
        c3 = CustomerProfile(
            customer_ipi="019284752",
            customer_name="Marcus Thorne",
            phone_number="2165551234",
            ssn_last4="4491",
            relationship_group="C",
            customer_tier=CustomerTier.PRIVILEGED,
            appl_type="KEYPRIV",
            sub_product_code="PQ",
            preferred_language=Language.ENG,
            is_key_at_work=False,
            accounts=[
                Account(
                    account_number="4042251188",
                    prod_code=AccountType.CHECKING,
                    account_name="Key Privilege Checking",
                    bank_number="0101",
                    current_balance=18200.00,
                    available_balance=18200.00,
                    statement_cycle_date="2026-11-15",
                    details={
                        "cycle_start": "2026-10-16",
                        "cycle_end": "2026-11-15",
                        "days_remaining": 4,
                        "mortgage_autopay_enabled": True,
                        "mortgage_autopay_amount": 1450.00,
                        "mortgage_account_linked": "MTG-8849201",
                        "cycle_direct_deposits": 0.0
                    }
                ),
                Account(
                    account_number="MTG-8849201",
                    prod_code=AccountType.MORTGAGE,
                    account_name="KeyBank Fixed Residential Mortgage",
                    bank_number="0101",
                    current_balance=284500.00,
                    available_balance=0.0,
                    statement_cycle_date="2026-11-01",
                    details={"monthly_pni": 1450.00, "interest_rate": 3.25}
                )
            ]
        )
        FeeAvoidanceEngine.evaluate(c3)
        customers[c3.customer_ipi] = c3

        # ----------------------------------------------------------------------------------
        # Scenario 4: BILINGUAL SPANISH PRIVILEGED CUSTOMER (Language Code 'SPA')
        # Group B, Balance $32,000, Speaks Spanish -> Routes to MMCCA_SPANISH / Spanish VIP Queue
        # ----------------------------------------------------------------------------------
        c4 = CustomerProfile(
            customer_ipi="048291043",
            customer_name="Sofia Ramirez-Cruz",
            phone_number="3055557890",
            ssn_last4="6120",
            relationship_group="B",
            customer_tier=CustomerTier.PRIVILEGED,
            appl_type="KEYPRIV",
            sub_product_code="PQ",
            preferred_language=Language.SPA,
            is_key_at_work=True,
            accounts=[
                Account(
                    account_number="4042253399",
                    prod_code=AccountType.CHECKING,
                    account_name="Key Privilege Checking (Espa\u00f1ol)",
                    bank_number="0101",
                    current_balance=28400.00,
                    available_balance=28400.00,
                    statement_cycle_date="2026-11-22",
                    details={
                        "cycle_start": "2026-10-23",
                        "cycle_end": "2026-11-22",
                        "days_remaining": 11,
                        "mortgage_autopay_enabled": False,
                        "cycle_direct_deposits": 3200.00
                    }
                )
            ]
        )
        FeeAvoidanceEngine.evaluate(c4)
        customers[c4.customer_ipi] = c4

        return customers

    @classmethod
    def find_by_identifier(cls, query: str) -> Optional[CustomerProfile]:
        """
        Finds a customer by phone number, IPI, SSN last 4, or account number.
        """
        clean_q = query.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        samples = cls.get_sample_customers()

        for profile in samples.values():
            if clean_q == profile.customer_ipi or clean_q == profile.phone_number or clean_q == profile.ssn_last4:
                return profile
            for acc in profile.accounts:
                if clean_q in acc.account_number or acc.account_number.endswith(clean_q):
                    return profile
        return None
