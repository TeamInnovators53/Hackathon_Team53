"""
Data models for KeyBank Key Privilege / Private Client Conversational Multi-Agent System.
Hackathon Team 53 - Team Innovators.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any


class CustomerTier(str, Enum):
    STANDARD = "STANDARD"
    PRIVILEGED = "PRIVILEGED"               # Relationship Groups A-H or Key Privilege Checking (PQ)
    PRIVATE_CLIENT = "PRIVATE_CLIENT"       # Tier 1 Ultra-High Net Worth Key Private Client


class Language(str, Enum):
    ENG = "ENG"
    SPA = "SPA"


class AccountType(str, Enum):
    CHECKING = "DDA"                        # Key Privilege Checking
    SAVINGS = "SAV"                         # Relationship Savings
    MONEY_MARKET = "MMA"                    # Key Silver/Gold Tier MMA
    CREDIT_CARD = "CCA"                     # Key Cashback / Latitude Credit Card
    MORTGAGE = "MTG"                        # KeyBank Residential Mortgage
    INVESTMENT = "INV"                      # Key Investment Services


@dataclass
class Account:
    account_number: str
    prod_code: AccountType
    account_name: str
    bank_number: str                        # '0101' KeyBank Retail, '2912' Laurel Road
    current_balance: float
    available_balance: float
    statement_cycle_date: str
    is_privilege_eligible: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Transaction:
    txn_id: str
    account_number: str
    date: str
    description: str
    amount: float
    category: str                           # 'Dining', 'Travel', 'Luxury Retail', 'Groceries', 'Utilities'
    is_recurring: bool = False
    reward_points_earned: int = 0


@dataclass
class MaintenanceFeeStatus:
    """
    Key Privilege Checking Account Maintenance Service Charge Avoidance Tracker:
    How to Avoid a $25.00 Maintenance Service Charge: Do one of the following during each statement cycle:
      1. Maintain a total balance of $25,000 or more in any combination of your accounts
      2. Have a KeyBank mortgage with automatic payment deductions of $500 or more from your Key Privilege Checking Account each cycle
      3. Be a Key@Work program member and have direct deposits that total at least $2,500 or more during each cycle
    """
    monthly_service_charge: float = 25.00
    cycle_start_date: str = ""
    cycle_end_date: str = ""
    days_remaining_in_cycle: int = 0

    # Rule 1: Total combined balance >= $25,000
    total_combined_balance: float = 0.0
    rule1_target: float = 25000.00
    rule1_met: bool = False

    # Rule 2: Mortgage auto-pay >= $500 from Privilege Checking
    has_keybank_mortgage: bool = False
    mortgage_auto_deduction_amount: float = 0.0
    rule2_target: float = 500.00
    rule2_met: bool = False

    # Rule 3: Key@Work member with direct deposits >= $2,500
    is_key_at_work_member: bool = False
    cycle_direct_deposits: float = 0.0
    rule3_target: float = 2500.00
    rule3_met: bool = False

    # Computed Overall Compliance
    is_fee_waived: bool = False
    winning_waiver_method: Optional[str] = None
    proactive_warning_needed: bool = False
    alert_message: str = ""
    actionable_remedy: str = ""


@dataclass
class RoutingContext:
    transfer_route_code: str = "GENESYS"    # e.g., 'KEY_PRIVATE_CLIENT_TRC', 'MMCCA_PRIMACY', 'KEYPRIVCCA'
    master_bot_id: str = "privilegeConcierge"
    genesys_attached_data: Dict[str, str] = field(default_factory=dict)
    priority_level: str = "HIGH"
    target_queue: str = "Key Privilege Priority Desk"


@dataclass
class CustomerProfile:
    customer_ipi: str
    customer_name: str
    phone_number: str
    ssn_last4: str
    relationship_group: str                 # 'A' - 'H' (Key Household Relationship Group)
    customer_tier: CustomerTier
    appl_type: str                          # 'KEYPRIV', 'PRIVBANK', 'K2U'
    sub_product_code: str                   # 'PQ' = Privilege Checking
    preferred_language: Language
    is_key_at_work: bool
    accounts: List[Account] = field(default_factory=list)
    recent_transactions: List[Transaction] = field(default_factory=list)
    fee_status: Optional[MaintenanceFeeStatus] = None


@dataclass
class AgentResponse:
    subagent_id: str
    subagent_title: str
    message: str
    speech_message: str
    audio_prompt_code: Optional[str] = None # e.g. '[K2U_ENG.704.au]'
    fee_reminder_banner: Optional[str] = None
    structured_data: Dict[str, Any] = field(default_factory=dict)
    suggested_quick_replies: List[str] = field(default_factory=list)
    routing_context: Optional[RoutingContext] = None
    handover_required: bool = False
