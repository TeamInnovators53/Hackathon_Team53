"""
Sub-Agent: Due Reminders & Maintenance Fee Countdown.
Hackathon Team 53 - Team Innovators.
"""

from typing import Dict, Any
from src.subagents.base_agent import BaseSubAgent
from src.models import CustomerProfile, AgentResponse, AccountType


class DueRemindersSubAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_id="due_reminders",
            title="Due Dates & Fee Avoidance Reminders",
            description="Alerts customer on upcoming bills, statement cycle closing, and maintenance service charge waiver deadlines."
        )

    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        text = user_text.lower()
        keywords = ["due reminders", "due dates", "when is my bill due", "reminders", "payment due", "upcoming payments", "avoid fee", "maintenance fee", "service charge", "avoid maintenance"]
        for kw in keywords:
            if kw in text:
                return 0.95
        return 0.0

    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        is_spa = profile.preferred_language.value == "SPA"
        fee_status = profile.fee_status

        reminders = []

        # 1. Credit card due date
        cc_acc = next((a for a in profile.accounts if a.prod_code == AccountType.CREDIT_CARD), None)
        if cc_acc:
            due_date = cc_acc.details.get("payment_due_date", "2026-11-28")
            min_due = cc_acc.details.get("minimum_payment_due", 45.00)
            reminders.append(f"• \U0001f4b3 **Credit Card Payment:** Minimum payment of **${min_due:,.2f}** due on **{due_date}** (Auto-pay scheduled).")

        # 2. Mortgage auto-pay
        mtg = next((a for a in profile.accounts if a.prod_code == AccountType.MORTGAGE), None)
        if mtg:
            pni = mtg.details.get("monthly_pni", 1450.00)
            reminders.append(f"• \U0001f3e1 **KeyBank Mortgage Auto-Deduction:** **${pni:,.2f}** scheduled for **2026-12-01**.")

        # 3. Privilege Checking Maintenance Fee Waiver Status
        if fee_status:
            cycle_end = fee_status.cycle_end_date
            days_left = fee_status.days_remaining_in_cycle
            if fee_status.is_fee_waived:
                reminders.append(
                    f"• \u2705 **Maintenance Fee Waiver Status:** **Waived ($0.00)** for cycle ending {cycle_end}. "
                    f"Qualified via {fee_status.winning_waiver_method}."
                )
            else:
                gap = 25000.00 - fee_status.total_combined_balance
                reminders.append(
                    f"• \u26a0\ufe0f **URGENT: Maintenance Fee Avoidance Deadline:** **{days_left} Days Remaining** (Cycle ends {cycle_end}).\n"
                    f"  *To avoid the $25.00 monthly service charge, do one of the following before {cycle_end}:*\n"
                    f"    1. Maintain **$25,000+** combined balance across accounts (Currently **${fee_status.total_combined_balance:,.2f}**; add **${gap:,.2f}**).\n"
                    f"    2. Auto-deduct **$500+** mortgage payment from this Key Privilege Checking.\n"
                    f"    3. Complete direct deposits of **$2,500+** as a Key@Work member (Currently **${fee_status.cycle_direct_deposits:,.2f}**)."
                )

        reminders_text = "\n\n".join(reminders)

        if is_spa:
            msg = (
                f"\U0001f514 **Recordatorios de Vencimientos y Estado de Cuota para {profile.customer_name}:**\n\n"
                f"{reminders_text}\n\n"
                f"\U0001f4c5 Puede configurar recordatorios v\u00eda SMS o correo electr\u00f3nico en cualquier momento."
            )
            speech = f"Tiene recordatorios pendientes de pago y {fee_status.days_remaining_in_cycle if fee_status else 5} d\u00edas para evitar el cargo de mantenimiento."
            prompt = "[K2U_SPA.730.au]"
        else:
            msg = (
                f"\U0001f514 **Upcoming Due Dates & Maintenance Fee Status for {profile.customer_name}:**\n\n"
                f"{reminders_text}\n\n"
                f"\U0001f4a1 *Tip: You can set automated transfer alerts or speak to your concierge to link external balances to ensure waiver compliance.*"
            )
            speech = (
                f"Here are your upcoming reminders. Your credit card payment is due on November 28th, "
                f"and you have {fee_status.days_remaining_in_cycle if fee_status else 5} days remaining in your statement cycle to avoid the $25 maintenance fee."
            )
            prompt = "[K2U_ENG.730.au]"

        return AgentResponse(
            subagent_id=self.agent_id,
            subagent_title=self.title,
            message=msg,
            speech_message=speech,
            audio_prompt_code=prompt,
            fee_reminder_banner=fee_status.alert_message if fee_status and not fee_status.is_fee_waived else None,
            suggested_quick_replies=[
                "Transfer Funds to Waive Fee",
                "Balance Inquiry",
                "Credit Card Statement",
                "Speak to Dedicated Concierge"
            ]
        )
