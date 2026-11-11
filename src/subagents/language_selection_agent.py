"""
Sub-Agent: Language Selection.
Hackathon Team 53 - Team Innovators.
"""

from typing import Dict, Any
from src.subagents.base_agent import BaseSubAgent
from src.models import CustomerProfile, AgentResponse, Language


class LanguageSelectionSubAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_id="language_selection",
            title="Language Preference Specialist",
            description="Toggles bilingual experience between English and Spanish, updating telephony routing profiles."
        )

    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        text = user_text.lower().strip()
        keywords = ["language", "spanish", "español", "espanol", "english", "inglés", "ingles", "cambiar idioma", "change language", "select language", "idioma"]
        for kw in keywords:
            if kw in text:
                return 0.95
        if text == "7":
            return 0.90
        return 0.0

    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        text = user_text.lower()

        # Toggle or explicitly set language
        if "spanish" in text or "español" in text or "espanol" in text or "2" in text or profile.preferred_language == Language.ENG:
            profile.preferred_language = Language.SPA
            msg = (
                f"\U0001f310 **Preferencia de Idioma Actualizada a Espa\u00f1ol:**\n\n"
                f"Hemos configurado su experiencia y su enrutamiento telef\u00f3nico en **Espa\u00f1ol** (`sessionKey.languageCode = 'SPA'`).\n\n"
                f"• Sus transferencias telef\u00f3nicas prioritarias se dirigir\u00e1n a la cola de agentes biling\u00fces (`MMCCA_SPANISH`).\n"
                f"• Todos los avisos de voz, recordatorios de comisiones y estados de cuenta se presentar\u00e1n en espa\u00f1ol."
            )
            speech = "Su idioma ha sido cambiado a español. ¿En qué le puedo asistir hoy con sus cuentas Key Privilege?"
            prompt = "[K2U_SPA.708.au]"
        else:
            profile.preferred_language = Language.ENG
            msg = (
                f"\U0001f310 **Language Preference Updated to English:**\n\n"
                f"Your session language and voice prompts have been switched to **English** (`sessionKey.languageCode = 'ENG'`).\n\n"
                f"• Priority transfers will route to the Key Privilege desk (`KEYPRIVCCA` / `KEY_PRIVATE_CLIENT_TRC`).\n"
                f"• All audio prompts and proactive fee notifications are now in English."
            )
            speech = "Your language has been switched to English. How may I assist you with your Key Privilege accounts today?"
            prompt = "[K2U_ENG.708.au]"

        return AgentResponse(
            subagent_id=self.agent_id,
            subagent_title=self.title,
            message=msg,
            speech_message=speech,
            audio_prompt_code=prompt,
            structured_data={"active_language": profile.preferred_language.value},
            suggested_quick_replies=[
                "Main Menu",
                "Balance Inquiry",
                "Credit Card Statement",
                "Due Reminders"
            ]
        )
