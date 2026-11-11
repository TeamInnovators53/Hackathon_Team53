"""
Sub-Agent: Overdraft or Customised Offers.
Hackathon Team 53 - Team Innovators.
"""

from typing import Dict, Any
from src.subagents.base_agent import BaseSubAgent
from src.models import CustomerProfile, AgentResponse, AccountType


class OverdraftAndOffersSubAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_id="overdraft_offers",
            title="Overdraft & Customised Privilege Offers",
            description="Manages Key Coverage overdraft protection and presents exclusive high-tier lending and investment offers."
        )

    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        text = user_text.lower()
        keywords = ["overdraft", "od protection", "customised offers", "customized offers", "special offers", "privilege offers", "promotions", "line of credit", "loan rates", "cd rates", "offers"]
        for kw in keywords:
            if kw in text:
                return 0.95
        return 0.0

    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        is_spa = profile.preferred_language.value == "SPA"

        # Check checking account overdraft status
        chk = next((a for a in profile.accounts if a.prod_code == AccountType.CHECKING), None)
        od_status = "Active (Backed by Relationship Savings)"
        if chk and not chk.details.get("overdraft_protection", True):
            od_status = "Standard Overdraft Coverage"

        if is_spa:
            msg = (
                f"\U0001f381 **Protecci\u00f3n Contra Sobregiros y Ofertas Personalizadas para {profile.customer_name}:**\n\n"
                f"• **Estado de Cobertura de Sobregiros (Key Coverage):** **{od_status}**\n"
                f"  *Sin cargos por transferencia autom\u00e1tica para clientes Key Privilege.*\n\n"
                f"\u2b50 **Ofertas Exclusivas Privilege Disponibles Hoy:**\n"
                f"1. **Certificado de Dep\u00f3sito (CD) Relacional a 14 Meses:** **4.85% APY** con bonificaci\u00f3n Privilege exclusiva.\n"
                f"2. **L\u00ednea de Cr\u00e9dito Personal Preaprobada:** Hasta **$35,000** sin comisi\u00f3n anual.\n"
                f"3. **Descuento en Hipoteca KeyBank:** Reducci\u00f3n del **0.25%** en la tasa de inter\u00e9s para nuevos pr\u00e9stamos hipotecarios.\n"
                f"4. **Tarjeta Key Cashback:** Reciba **2.0% ilimitado** de reembolso en todas sus compras."
            )
            speech = "Usted tiene protecci\u00f3n contra sobregiros activa sin cargos, adem\u00e1s de una tasa especial de CD del 4.85% y una l\u00ednea de cr\u00e9dito preaprobada."
            prompt = "[K2U_SPA.720.au]"
        else:
            msg = (
                f"\U0001f381 **Overdraft Protection & Customised Privilege Offers for {profile.customer_name}:**\n\n"
                f"\U0001f6e1\ufe0f **Overdraft Status (Key Coverage):** **{od_status}**\n"
                f"*(As a Key Privilege client, automatic backup transfer fees between checking and savings are $0.00 waivable).*\n\n"
                f"\u2b50 **Personalized VIP Offers for Relationship Tier {profile.relationship_group}:**\n\n"
                f"1. \U0001f4c8 **14-Month Relationship CD:** **4.85% APY** (includes +0.35% Key Privilege Relationship Bonus).\n"
                f"2. \U0001f4b3 **Pre-Approved Executive Line of Credit:** Up to **$35,000** at Prime + 1.99% with zero origination fee.\n"
                f"3. \U0001f3e1 **KeyBank Mortgage Rate Discount:** **0.25% interest rate discount** when payments are auto-deducted from your Privilege Checking (also waives your monthly fee!).\n"
                f"4. \U0001f31f **Key Cashback Credit Card Upgrade:** Unlimited **2.0% Cash Back** on all purchases deposited directly to your Privilege checking."
            )
            speech = (
                f"Your overdraft protection is active with zero transfer fees. We also have two customized offers for you: "
                f"a 4.85 percent relationship CD rate, and a pre-approved $35,000 executive line of credit."
            )
            prompt = "[K2U_ENG.720.au]"

        return AgentResponse(
            subagent_id=self.agent_id,
            subagent_title=self.title,
            message=msg,
            speech_message=speech,
            audio_prompt_code=prompt,
            structured_data={
                "overdraft_status": od_status,
                "offers_count": 4,
                "featured_offer": "14-Month CD at 4.85% APY"
            },
            suggested_quick_replies=[
                "Apply for 4.85% CD",
                "Explore Mortgage Discount",
                "Balance Inquiry",
                "Speak to Dedicated Concierge"
            ]
        )
