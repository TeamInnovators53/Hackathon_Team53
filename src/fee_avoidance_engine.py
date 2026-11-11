"""
KeyBank Key Privilege Checking - Maintenance Service Charge Avoidance & Proactive Reminder Engine.
Hackathon Team 53 - Team Innovators.

Waiver Rules:
1. Maintain total combined balance of $25,000 or more across all accounts.
2. Have a KeyBank mortgage with automatic payment deduction of $500 or more from Key Privilege Checking.
3. Be a Key@Work program member and have direct deposits totaling at least $2,500 or more during statement cycle.
"""

from typing import Tuple
from src.models import CustomerProfile, MaintenanceFeeStatus, AccountType


class FeeAvoidanceEngine:
    """
    Evaluates statement cycle compliance for avoiding the $25 monthly maintenance fee
    on Key Privilege Checking accounts, calculating gaps and proactive menu reminders.
    """

    MONTHLY_FEE = 25.00
    BALANCE_THRESHOLD = 25000.00
    MORTGAGE_AUTOPAY_THRESHOLD = 500.00
    KEY_AT_WORK_DEPOSIT_THRESHOLD = 2500.00

    DEPOSIT_ASSET_TYPES = {
        AccountType.CHECKING,
        AccountType.SAVINGS,
        AccountType.MONEY_MARKET,
        AccountType.INVESTMENT
    }

    @classmethod
    def evaluate(cls, profile: CustomerProfile) -> MaintenanceFeeStatus:
        """
        Calculates compliance across all 3 exemption rules for the active statement cycle.
        """
        # Calculate Rule 1: Combined deposit/asset balance across all KeyBank eligible accounts
        total_balance = sum(
            acc.current_balance
            for acc in profile.accounts
            if acc.prod_code in cls.DEPOSIT_ASSET_TYPES
            and (acc.bank_number == "0101" or acc.is_privilege_eligible)
        )
        rule1_met = total_balance >= cls.BALANCE_THRESHOLD

        # Calculate Rule 2: Mortgage auto-deduction from Privilege Checking
        has_mortgage = any(acc.prod_code == AccountType.MORTGAGE for acc in profile.accounts)
        checking_acc = next((acc for acc in profile.accounts if acc.prod_code == AccountType.CHECKING), None)
        
        mortgage_autopay = 0.0
        if checking_acc and checking_acc.details.get("mortgage_autopay_enabled"):
            mortgage_autopay = float(checking_acc.details.get("mortgage_autopay_amount", 0.0))
        rule2_met = has_mortgage and (mortgage_autopay >= cls.MORTGAGE_AUTOPAY_THRESHOLD)

        # Calculate Rule 3: Key@Work direct deposits
        direct_deposits = 0.0
        if checking_acc:
            direct_deposits = float(checking_acc.details.get("cycle_direct_deposits", 0.0))
        rule3_met = profile.is_key_at_work and (direct_deposits >= cls.KEY_AT_WORK_DEPOSIT_THRESHOLD)

        # Determine winning rule and fee waiver status
        is_waived = rule1_met or rule2_met or rule3_met
        winning_method = None
        if rule1_met:
            winning_method = f"Combined Balance (${total_balance:,.2f} >= ${cls.BALANCE_THRESHOLD:,.2f})"
        elif rule2_met:
            winning_method = f"Mortgage Auto-Payment (${mortgage_autopay:,.2f}/mo >= ${cls.MORTGAGE_AUTOPAY_THRESHOLD:,.2f})"
        elif rule3_met:
            winning_method = f"Key@Work Direct Deposits (${direct_deposits:,.2f} >= ${cls.KEY_AT_WORK_DEPOSIT_THRESHOLD:,.2f})"

        # Determine cycle dates and days remaining
        cycle_start = checking_acc.details.get("cycle_start", "2026-11-01") if checking_acc else "2026-11-01"
        cycle_end = checking_acc.details.get("cycle_end", "2026-11-30") if checking_acc else "2026-11-30"
        days_remaining = checking_acc.details.get("days_remaining", 7) if checking_acc else 7

        # Proactive Warning & Remediation Logic
        proactive_warning_needed = False
        alert_msg = ""
        remedy_msg = ""

        if not is_waived:
            proactive_warning_needed = True
            balance_gap = max(0.0, cls.BALANCE_THRESHOLD - total_balance)
            deposit_gap = max(0.0, cls.KEY_AT_WORK_DEPOSIT_THRESHOLD - direct_deposits) if profile.is_key_at_work else None

            alert_msg = (
                f"Action Required: Your Key Privilege Checking account is currently at risk of a ${cls.MONTHLY_FEE:.2f} "
                f"monthly maintenance service charge for the cycle ending {cycle_end} ({days_remaining} days remaining)."
            )

            # Suggest the fastest route to avoid fee
            suggestions = []
            if balance_gap > 0:
                suggestions.append(f"Transfer or deposit ${balance_gap:,.2f} to reach the $25,000 combined balance tier")
            if profile.is_key_at_work and deposit_gap and deposit_gap > 0:
                suggestions.append(f"Ensure remaining direct deposits of ${deposit_gap:,.2f} arrive before {cycle_end}")
            if has_mortgage and mortgage_autopay < cls.MORTGAGE_AUTOPAY_THRESHOLD:
                suggestions.append("Set up automatic mortgage deduction of $500+ from your Privilege Checking")

            remedy_msg = " • " + "\n • ".join(suggestions)
        else:
            alert_msg = f"Your ${cls.MONTHLY_FEE:.2f} monthly maintenance fee is waived for this cycle via {winning_method}."

        fee_status = MaintenanceFeeStatus(
            monthly_service_charge=cls.MONTHLY_FEE,
            cycle_start_date=cycle_start,
            cycle_end_date=cycle_end,
            days_remaining_in_cycle=days_remaining,
            total_combined_balance=total_balance,
            rule1_target=cls.BALANCE_THRESHOLD,
            rule1_met=rule1_met,
            has_keybank_mortgage=has_mortgage,
            mortgage_auto_deduction_amount=mortgage_autopay,
            rule2_target=cls.MORTGAGE_AUTOPAY_THRESHOLD,
            rule2_met=rule2_met,
            is_key_at_work_member=profile.is_key_at_work,
            cycle_direct_deposits=direct_deposits,
            rule3_target=cls.KEY_AT_WORK_DEPOSIT_THRESHOLD,
            rule3_met=rule3_met,
            is_fee_waived=is_waived,
            winning_waiver_method=winning_method,
            proactive_warning_needed=proactive_warning_needed,
            alert_message=alert_msg,
            actionable_remedy=remedy_msg
        )

        profile.fee_status = fee_status
        return fee_status

    @classmethod
    def get_concise_menu_reminder(cls, fee_status: MaintenanceFeeStatus, lang: str = "ENG") -> str:
        """
        Generates brief proactive reminder message suitable for IVR voice prompt injection
        and chat menu banner.
        """
        if fee_status.is_fee_waived:
            if lang == "SPA":
                return f"[AVISO] Su cuota mensual de mantenimiento de $25.00 est\u00e1 EXONERADA para este ciclo."
            return f"[PRIVILEGE STATUS] Your $25.00 monthly maintenance fee is WAIVED for this cycle."

        # At-risk alert
        balance_gap = cls.BALANCE_THRESHOLD - fee_status.total_combined_balance
        if lang == "SPA":
            return (
                f"[ATENCI\u00d3N CUOTA]: Faltan {fee_status.days_remaining_in_cycle} d\u00edas para el cierre de su ciclo. "
                f"Deposite ${balance_gap:,.2f} o configure su dep\u00f3sito Key@Work para evitar el cargo de $25.00."
            )
        return (
            f"[IMPORTANT PRIVILEGE REMINDER]: {fee_status.days_remaining_in_cycle} days remaining in your statement cycle! "
            f"Add ${balance_gap:,.2f} in combined balance or verify your Key@Work direct deposits to avoid the $25.00 service charge."
        )
