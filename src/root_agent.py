"""
Root Agent / Supervisor Orchestrator for KeyBank Key Privilege Voice & Chat Bot.
Hackathon Team 53 - Team Innovators.

Identifies privileged customers via Relationship Group mapping, evaluates maintenance fee
exemption compliance, and routes intents to specialized domain sub-agents.
"""

from typing import Dict, Any, Optional
from src.models import CustomerProfile, AgentResponse, CustomerTier
from src.customer_service import CustomerService
from src.fee_avoidance_engine import FeeAvoidanceEngine
from src.subagents import (
    CreditCardStatementSubAgent,
    BalanceInquirySubAgent,
    OverdraftAndOffersSubAgent,
    PurchaseHistoryAndRecommendationsSubAgent,
    DueRemindersSubAgent,
    PriorityHandoverSubAgent,
    TraditionalMenuSubAgent,
    LanguageSelectionSubAgent
)


class RootPrivilegeAgent:
    """
    Root Conversational Agent & Dispatcher.
    """

    def __init__(self):
        # Register all 8 domain sub-agents
        self.subagents = {
            "cc_statement": CreditCardStatementSubAgent(),
            "balance_inquiry": BalanceInquirySubAgent(),
            "overdraft_offers": OverdraftAndOffersSubAgent(),
            "purchase_recommendations": PurchaseHistoryAndRecommendationsSubAgent(),
            "due_reminders": DueRemindersSubAgent(),
            "priority_handover": PriorityHandoverSubAgent(),
            "traditional_menu": TraditionalMenuSubAgent(),
            "language_selection": LanguageSelectionSubAgent()
        }

    def initialize_session(self, profile: CustomerProfile) -> AgentResponse:
        """
        Creates initial greeting upon caller authentication, evaluating Relationship Group
        and injecting proactive maintenance fee warnings if the customer is at risk.
        """
        # Recalculate fee avoidance status
        fee_status = FeeAvoidanceEngine.evaluate(profile)
        is_spa = profile.preferred_language.value == "SPA"

        fee_banner = None
        if not fee_status.is_fee_waived:
            fee_banner = fee_status.alert_message

        tier_title = "Key Private Client" if profile.customer_tier == CustomerTier.PRIVATE_CLIENT else "Key Privilege"

        if is_spa:
            welcome_text = (
                f"\U0001f3db\ufe0f **Bienvenido a los Servicios de Concierge {tier_title} de KeyBank.**\n\n"
                f"Hola {profile.customer_name}. Su cuenta ha sido identificada como cliente de **M\u00e1xima Prioridad** "
                f"(Grupo de Relaci\u00f3n `{profile.relationship_group}`).\n\n"
            )
            if not fee_status.is_fee_waived:
                welcome_text += (
                    f"\u26a0\ufe0f **Recordatorio Importante de Cuenta:**\n"
                    f"{fee_status.alert_message}\n\n"
                    f"**Opciones para Exonerar el Cargo de $25.00:**\n"
                    f"{fee_status.actionable_remedy}\n\n"
                )
            welcome_text += "\U0001f399\ufe0f *¿En qué le puedo asistir hoy? Puede hablar con lenguaje natural o pedir el menú de opciones.*"
            speech = f"Bienvenido a KeyBank {tier_title}, {profile.customer_name}. ¿Cómo le podemos asistir hoy?"
            prompt = "[K2U_SPA.700.au]"
        else:
            welcome_text = (
                f"\U0001f3db\ufe0f **Welcome to KeyBank {tier_title} Concierge Services.**\n\n"
                f"Hello, {profile.customer_name}. Your profile has been authenticated with **VIP Priority Treatment** "
                f"(Household Relationship Group `{profile.relationship_group}`).\n\n"
            )
            if not fee_status.is_fee_waived:
                welcome_text += (
                    f"\u26a0\ufe0f **Proactive Service Charge Notice:**\n"
                    f"{fee_status.alert_message}\n\n"
                    f"**How to Avoid the $25.00 Maintenance Fee Before Cycle End:**\n"
                    f"{fee_status.actionable_remedy}\n\n"
                )
            welcome_text += "\U0001f399\ufe0f *How can I assist you today? You can speak naturally, choose a quick action, or press for the traditional menu.*"
            speech = f"Welcome to KeyBank {tier_title}, {profile.customer_name}. How can we assist you today?"
            prompt = "[K2U_ENG.700.au]"

        return AgentResponse(
            subagent_id="root_agent",
            subagent_title=f"{tier_title} Root Supervisor",
            message=welcome_text,
            speech_message=speech,
            audio_prompt_code=prompt,
            fee_reminder_banner=fee_banner,
            structured_data={
                "customer_tier": profile.customer_tier.value,
                "relationship_group": profile.relationship_group,
                "fee_waived": fee_status.is_fee_waived,
                "days_remaining": fee_status.days_remaining_in_cycle
            },
            suggested_quick_replies=[
                "1. Balance Inquiry",
                "2. Credit Card Statement",
                "3. Overdraft & Offers",
                "4. Purchase History & Rewards",
                "5. Due Reminders & Fee Avoidance",
                "6. Speak to Dedicated Concierge",
                "7. Traditional Menu"
            ]
        )

    def route_and_execute(self, profile: CustomerProfile, user_text: str, session_context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Routes user query or DTMF keypress to the best matching domain sub-agent.
        """
        context = session_context or {}
        cleaned_text = user_text.strip()
        lower_text = cleaned_text.lower()

        # Always update fee status
        FeeAvoidanceEngine.evaluate(profile)

        # 1. Check for DTMF single digit shortcuts
        dtmf_mapping = {
            "1": "balance_inquiry",
            "2": "cc_statement",
            "3": "overdraft_offers",
            "4": "purchase_recommendations",
            "5": "due_reminders",
            "6": "priority_handover",
            "7": "language_selection"
        }
        if cleaned_text in dtmf_mapping:
            target_subagent = self.subagents[dtmf_mapping[cleaned_text]]
            return target_subagent.process(profile, user_text, context)

        # 2. Check for explicit fee avoidance inquiry
        if any(kw in lower_text for kw in ["avoid fee", "avoid maintenance", "maintenance fee", "service charge", "avoid a maintenance"]):
            return self.subagents["due_reminders"].process(profile, user_text, context)

        # 3. Evaluate confidence score across all registered sub-agents
        best_agent = None
        highest_score = 0.0

        for agent in self.subagents.values():
            score = agent.can_handle(user_text, context)
            if score > highest_score:
                highest_score = score
                best_agent = agent

        # 4. If confidence threshold met (>= 0.70), dispatch to domain subagent
        if best_agent and highest_score >= 0.70:
            return best_agent.process(profile, user_text, context)

        # 5. Fallback: Present Traditional Menu with embedded fee reminder
        return self.subagents["traditional_menu"].process(profile, user_text, context)
