"""
Sub-Agent: Traditional IVR DTMF Menu.
Hackathon Team 53 - Team Innovators.

Provides classic voice/touch-tone menu with proactive Maintenance Service Charge
avoidance reminders embedded directly into the menu flow.
"""

from typing import Dict, Any
from src.subagents.base_agent import BaseSubAgent
from src.models import CustomerProfile, AgentResponse
from src.fee_avoidance_engine import FeeAvoidanceEngine


class TraditionalMenuSubAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_id="traditional_menu",
            title="Traditional Voice & DTMF Menu",
            description="Presents touch-tone / numbered audio menu with proactive maintenance fee announcements."
        )

    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        text = user_text.lower().strip()
        keywords = ["menu", "main menu", "options", "traditional menu", "ivr", "touch tone", "dtmf", "press 1", "press 2", "go back to menu", "start over"]
        for kw in keywords:
            if kw in text:
                return 0.95
        if text in {"1", "2", "3", "4", "5", "6", "7", "0", "*"}:
            return 0.90
        return 0.0

    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        is_spa = profile.preferred_language.value == "SPA"
        fee_status = profile.fee_status
        concise_reminder = FeeAvoidanceEngine.get_concise_menu_reminder(fee_status, profile.preferred_language.value) if fee_status else ""

        if is_spa:
            msg = (
                f"\U0001f3db\ufe0f **Men\u00fa Principal de Voz / Marcaci\u00f3n Key Privilege:**\n\n"
                f"\U0001f514 **Recordatorio del Sistema para Mantener su Beneficio:**\n"
                f"> *{concise_reminder}*\n\n"
                f"Por favor presione o diga una de las siguientes opciones:\n\n"
                f"• **Presione 1:** Consulta de Saldos de Cuentas\n"
                f"• **Presione 2:** Estado de Cuenta de Tarjeta de Cr\u00e9dito\n"
                f"• **Presione 3:** Protecci\u00f3n de Sobregiros y Ofertas Personalizadas\n"
                f"• **Presione 4:** Historial de Compras y Recomendaciones Inteligentes\n"
                f"• **Presione 5:** Recordatorios de Vencimiento y C\u00f3mo Evitar Cargos\n"
                f"• **Presione 6:** Transferencia Prioritaria con su Especialista Dedicado\n"
                f"• **Presione 7:** Cambiar Idioma a Ingl\u00e9s (Language Selection)"
            )
            speech = (
                f"Bienvenido a Key Privilege. {concise_reminder}. "
                f"Presione 1 para saldos, 2 para estado de tarjeta, 3 para ofertas, 4 para historial de compras, "
                f"5 para recordatorios de vencimiento, 6 para hablar con su especialista dedicado, o 7 para cambiar idioma."
            )
            prompt = "[K2U_SPA.700.au]"
        else:
            msg = (
                f"\U0001f3db\ufe0f **Key Privilege Automated Service Menu:**\n\n"
                f"\U0001f514 **Proactive Account Maintenance Reminder:**\n"
                f"> *{concise_reminder}*\n\n"
                f"**Please select or speak one of the following menu options:**\n\n"
                f"• **Press 1:** Balance Inquiry *(Checking, Savings & Total Relationship)*\n"
                f"• **Press 2:** Credit Card Statement *(Balances, Due Dates & e-Statements)*\n"
                f"• **Press 3:** Overdraft Protection & Customised VIP Offers\n"
                f"• **Press 4:** Purchase History & AI Rewards Recommendations\n"
                f"• **Press 5:** Upcoming Due Reminders & Fee Avoidance Checklist\n"
                f"• **Press 6:** Priority Handover to Dedicated Concierge Specialist\n"
                f"• **Press 7:** Language Selection *(Espa\u00f1ol / English)*"
            )
            speech = (
                f"Welcome to Key Privilege Automated Services. {concise_reminder}. "
                f"Press 1 for balance inquiry. Press 2 for credit card statement. Press 3 for overdraft and offers. "
                f"Press 4 for purchase history and recommendations. Press 5 for due reminders and fee avoidance. "
                f"Press 6 for dedicated concierge priority handover. Or press 7 for Spanish language selection."
            )
            prompt = "[K2U_ENG.700.au]"

        return AgentResponse(
            subagent_id=self.agent_id,
            subagent_title=self.title,
            message=msg,
            speech_message=speech,
            audio_prompt_code=prompt,
            fee_reminder_banner=concise_reminder,
            structured_data={"menu_options_count": 7},
            suggested_quick_replies=[
                "1. Balance Inquiry",
                "2. Credit Card Statement",
                "3. Overdraft & Offers",
                "4. Purchase Recommendations",
                "5. Due Reminders",
                "6. Dedicated Concierge",
                "7. Language Selection"
            ]
        )
