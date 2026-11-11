"""
Sub-Agent: Handover to Dedicated Agent (Priority Routing).
Hackathon Team 53 - Team Innovators.
"""

from typing import Dict, Any
from src.subagents.base_agent import BaseSubAgent
from src.models import CustomerProfile, AgentResponse, RoutingContext, CustomerTier


class PriorityHandoverSubAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_id="priority_handover",
            title="Dedicated Concierge Priority Handover",
            description="Performs warm transfer and priority queue routing to Key Private Client & Privilege specialists."
        )

    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        text = user_text.lower()
        keywords = ["representative", "human", "agent", "concierge", "private banker", "advisor", "talk to someone", "operator", "speak with agent", "dedicated agent", "handover", "priority routing", "escalate"]
        for kw in keywords:
            if kw in text:
                return 0.98
        return 0.0

    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        is_spa = profile.preferred_language.value == "SPA"

        # Determine Priority Transfer Route Code based on customer tier and language
        if is_spa:
            trc = "MMCCA_SPANISH"
            target_desk = "KeyBank Spanish VIP Concierge Desk"
        elif profile.customer_tier == CustomerTier.PRIVATE_CLIENT:
            trc = "KEY_PRIVATE_CLIENT_TRC"
            target_desk = "Key Private Client Wealth Concierge Queue"
        else:
            trc = "KEYPRIVCCA"
            target_desk = "Key Privilege Priority Relationship Queue"

        # Construct Genesys Attached Data KVPs and Odyssey Context Payload
        fee_risk = "YES" if (profile.fee_status and not profile.fee_status.is_fee_waived) else "NO"
        total_bal = profile.fee_status.total_combined_balance if profile.fee_status else 0.0

        genesys_kvps = {
            "CustomerIPI": profile.customer_ipi,
            "CustomerTier": profile.customer_tier.value,
            "RelationshipGroup": profile.relationship_group,
            "PriorityQueue": "TRUE",
            "StopPayment": "false",
            "MaintenanceFeeAtRisk": fee_risk,
            "TotalCombinedBalance": f"{total_bal:.2f}",
            "LanguageCode": profile.preferred_language.value,
            "TRC": trc,
            "masterBotId": "privilegeConcierge"
        }

        routing_context = RoutingContext(
            transfer_route_code=trc,
            master_bot_id="privilegeConcierge",
            genesys_attached_data=genesys_kvps,
            priority_level="TIER_1_VIP",
            target_queue=target_desk
        )

        chk = profile.accounts[0] if profile.accounts else None
        advisor_info = chk.details.get("dedicated_advisor", "Assigned Privilege Relationship Manager") if chk else "Assigned Relationship Manager"

        if is_spa:
            msg = (
                f"\U0001f4de **Transferencia Prioritaria a su Especialista Dedicado:**\n\n"
                f"Hemos enrutado su llamada con **M\u00e1xima Prioridad** al **{target_desk}**.\n\n"
                f"\U0001f4cb **Datos de Enrutamiento Telef\u00f3nico (Genesys / GVP):**\n"
                f"• **C\u00f3digo de Ruta (TRC):** `{trc}`\n"
                f"• **Grupo de Relaci\u00f3n:** Nivel `{profile.relationship_group}` (Key Privilege)\n"
                f"• **Tiempo Estimado de Espera:** < 15 segundos (L\u00ednea Exclusiva)\n"
                f"• **Contexto de Sesi\u00f3n:** Se ha transferido su historial e identificador IPI `{profile.customer_ipi}` para que no tenga que repetir informaci\u00f3n."
            )
            speech = f"Transfiriendo con m\u00e1xima prioridad a su especialista dedicado en la cola {target_desk}."
            prompt = "[K2U_SPA.750.au]"
        else:
            msg = (
                f"\U0001f4de **Priority Handover to Dedicated Concierge Specialist:**\n\n"
                f"Your request has been routed with **Tier-1 Priority** to the **{target_desk}**.\n\n"
                f"\U0001f4cb **Telephony & Routing Payload (Genesys Attached Data / TRC):**\n"
                f"• **Transfer Route Code (TRC):** `{trc}`\n"
                f"• **Household Relationship Group:** `{profile.relationship_group}` | Tier: **{profile.customer_tier.value}**\n"
                f"• **Dedicated Contact:** {advisor_info}\n"
                f"• **Estimated Queue Wait Time:** **< 20 seconds** (VIP Bypass)\n"
                f"• **Warm Context Transfer:** Full session state, balances (${total_bal:,.2f}), and fee status automatically transmitted to agent desktop."
            )
            speech = (
                f"Connecting you directly to your dedicated Key Privilege specialist with priority routing under code {trc}. "
                f"Your representative will be with you in just a moment."
            )
            prompt = "[K2U_ENG.750.au]"

        return AgentResponse(
            subagent_id=self.agent_id,
            subagent_title=self.title,
            message=msg,
            speech_message=speech,
            audio_prompt_code=prompt,
            routing_context=routing_context,
            handover_required=True,
            structured_data=genesys_kvps,
            suggested_quick_replies=[
                "Cancel Transfer & Return to Menu",
                "Balance Inquiry",
                "Credit Card Statement"
            ]
        )
