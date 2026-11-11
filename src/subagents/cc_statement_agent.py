"""
Sub-Agent: Credit Card Statement.
Hackathon Team 53 - Team Innovators.
"""

from typing import Dict, Any
from src.subagents.base_agent import BaseSubAgent
from src.models import CustomerProfile, AgentResponse, AccountType


class CreditCardStatementSubAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_id="cc_statement",
            title="Credit Card Statement Specialist",
            description="Provides statement balances, minimum payment, cycle dates, and e-statement delivery."
        )

    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        text = user_text.lower()
        keywords = ["statement", "credit card bill", "cc bill", "estatement", "e-statement", "card statement", "minimum payment"]
        for kw in keywords:
            if kw in text:
                return 0.95
        if "credit card" in text and ("bill" in text or "balance" in text or "cycle" in text):
            return 0.85
        return 0.0

    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        # Find credit card account
        cc_acc = next((a for a in profile.accounts if a.prod_code == AccountType.CREDIT_CARD), None)

        if not cc_acc:
            msg = "I was unable to locate an active credit card account under your Key Privilege profile."
            return AgentResponse(
                subagent_id=self.agent_id,
                subagent_title=self.title,
                message=msg,
                speech_message=msg,
                suggested_quick_replies=["Balance Inquiry", "Check Offers", "Speak to Concierge"]
            )

        details = cc_acc.details
        stmt_bal = details.get("statement_balance", abs(cc_acc.current_balance))
        min_due = details.get("minimum_payment_due", 45.00)
        due_date = details.get("payment_due_date", "2026-11-28")
        limit = details.get("credit_limit", 15000.00)
        avail = cc_acc.available_balance
        points = details.get("reward_points", 0)

        is_spa = profile.preferred_language.value == "SPA"
        if is_spa:
            msg = (
                f"\u2705 **Resumen del Estado de Cuenta de su Tarjeta de Cr\u00e9dito ({cc_acc.account_name} terminada en {cc_acc.account_number[-4:]}):**\n"
                f"• **Saldo del Estado de Cuenta:** ${stmt_bal:,.2f}\n"
                f"• **Pago M\u00ednimo Requerido:** ${min_due:,.2f}\n"
                f"• **Fecha L\u00edmite de Pago:** {due_date}\n"
                f"• **Cr\u00e9dito Disponible:** ${avail:,.2f} de un l\u00edmite de ${limit:,.2f}\n"
                f"• **Puntos de Recompensa Privilege Acumulados:** {points:,} pts\n\n"
                f"\U0001f4e7 Su estado de cuenta electr\u00f3nico e-Statement oficial de noviembre est\u00e1 disponible para descarga en PDF en KeyNet/KeyBank Mobile."
            )
            speech = f"El saldo de su estado de cuenta para su tarjeta Privilege es de ${stmt_bal:,.2f}, con un pago m\u00ednimo de ${min_due:,.2f} con vencimiento el {due_date}."
            prompt = "[K2U_SPA.712.au]"
        else:
            msg = (
                f"\u2705 **Credit Card Statement Summary for {cc_acc.account_name} (ending in {cc_acc.account_number[-4:]}):**\n\n"
                f"• **Statement Balance:** **${stmt_bal:,.2f}**\n"
                f"• **Minimum Payment Due:** **${min_due:,.2f}**\n"
                f"• **Payment Due Date:** **{due_date}**\n"
                f"• **Available Credit:** ${avail:,.2f} (Credit Limit: ${limit:,.2f})\n"
                f"• **Accumulated Privilege Rewards:** **{points:,} points** (Cash Value: ${details.get('cashback_available', 0.0):,.2f})\n\n"
                f"\U0001f4e7 *Your November e-Statement is ready. Paperless billing is active and sent to your registered email.*"
            )
            speech = (
                f"Your statement balance for your Key Privilege card is ${stmt_bal:,.2f}, "
                f"with a minimum payment of ${min_due:,.2f} due on {due_date}."
            )
            prompt = "[K2U_ENG.712.au]"

        return AgentResponse(
            subagent_id=self.agent_id,
            subagent_title=self.title,
            message=msg,
            speech_message=speech,
            audio_prompt_code=prompt,
            structured_data={
                "account_name": cc_acc.account_name,
                "account_number": cc_acc.account_number,
                "statement_balance": stmt_bal,
                "minimum_due": min_due,
                "due_date": due_date,
                "available_credit": avail,
                "points": points
            },
            suggested_quick_replies=[
                "Pay Credit Card Bill",
                "Purchase History & Rewards",
                "Balance Inquiry",
                "Avoid Maintenance Fee"
            ]
        )
