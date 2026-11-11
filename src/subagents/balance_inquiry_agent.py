"""
Sub-Agent: Balance Inquiry.
Hackathon Team 53 - Team Innovators.
"""

from typing import Dict, Any
from src.subagents.base_agent import BaseSubAgent
from src.models import CustomerProfile, AgentResponse, AccountType


class BalanceInquirySubAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_id="balance_inquiry",
            title="Relationship Balance Specialist",
            description="Reports balances across Key Privilege Checking, Savings, MMA, and total relationship holdings."
        )

    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        text = user_text.lower()
        keywords = ["balance", "how much money", "account balance", "checking balance", "savings balance", "how much do i have", "funds"]
        for kw in keywords:
            if kw in text:
                return 0.95
        return 0.0

    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        is_spa = profile.preferred_language.value == "SPA"

        # Tally balances
        total_balance = sum(a.current_balance for a in profile.accounts if a.bank_number == "0101" or a.is_privilege_eligible)

        account_lines = []
        for acc in profile.accounts:
            bal_str = f"${acc.current_balance:,.2f}"
            if acc.prod_code == AccountType.CREDIT_CARD:
                bal_str = f"${abs(acc.current_balance):,.2f} (Current Balance)"
            account_lines.append(f"• **{acc.account_name}** (*{acc.account_number[-4:]}): **{bal_str}**")

        accounts_text = "\n".join(account_lines)

        fee_status = profile.fee_status
        fee_note = ""
        if fee_status:
            if fee_status.is_fee_waived:
                fee_note = f"\n\n\U0001f6e1\ufe0f **Relationship Tier Status:** Your combined balance of **${total_balance:,.2f}** qualifies for **100% Waived Monthly Service Charges** (Threshold: $25,000.00)."
            else:
                gap = 25000.00 - total_balance
                fee_note = (
                    f"\n\n\u26a0\ufe0f **Maintenance Fee Advisory:** Your combined balance is **${total_balance:,.2f}** "
                    f"(${gap:,.2f} below the $25,000 fee waiver threshold). You have {fee_status.days_remaining_in_cycle} days "
                    f"in your cycle to top up to avoid the $25.00 maintenance fee."
                )

        if is_spa:
            msg = (
                f"\U0001f4b0 **Saldos de sus Cuentas Key Privilege para {profile.customer_name}:**\n\n"
                f"{accounts_text}\n\n"
                f"**Saldo Total Combinado:** **${total_balance:,.2f}**"
                f"{fee_note}"
            )
            speech = f"El saldo en su cuenta de cheques Key Privilege es de ${profile.accounts[0].current_balance:,.2f}, con un saldo combinado de relación de ${total_balance:,.2f}."
            prompt = "[K2U_SPA.701.au]"
        else:
            msg = (
                f"\U0001f4b0 **Account Balances for {profile.customer_name} (Tier: {profile.customer_tier.value}):**\n\n"
                f"{accounts_text}\n\n"
                f"\U0001f3db\ufe0f **Total Combined Relationship Holdings:** **${total_balance:,.2f}**"
                f"{fee_note}"
            )
            speech = (
                f"Here are your Key Privilege balances. Your checking account balance is "
                f"${profile.accounts[0].current_balance:,.2f}, and your total combined relationship balance is ${total_balance:,.2f}."
            )
            prompt = "[K2U_ENG.701.au]"

        return AgentResponse(
            subagent_id=self.agent_id,
            subagent_title=self.title,
            message=msg,
            speech_message=speech,
            audio_prompt_code=prompt,
            structured_data={
                "total_balance": total_balance,
                "accounts": [
                    {"name": a.account_name, "num": a.account_number[-4:], "balance": a.current_balance}
                    for a in profile.accounts
                ]
            },
            suggested_quick_replies=[
                "How to Avoid Maintenance Fee",
                "Credit Card Statement",
                "Overdraft & Offers",
                "Speak to Dedicated Concierge"
            ]
        )
