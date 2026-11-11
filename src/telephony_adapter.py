"""
Odyssey (DFCX / CES) and Genesys Telephony Integration Middleware Adapter.
Hackathon Team 53 - Team Innovators.

Constructs Genesys GVP Attached Data KVPs and Odyssey session context payloads
for Key Privilege & Private Client Priority Routing.
"""

from typing import Dict, Any
from src.models import CustomerProfile, CustomerTier, RoutingContext


class TelephonyAdapter:
    """
    Simulates the contact center telephony bridge between Odyssey (Conversational AI layer)
    and Genesys Orchestration Server (ORS) / SIP GVP.
    """

    PBX_ROUTE_POINTS = {
        "KEY_PRIVATE_CLIENT_TRC": "5554001",   # Key Private Client Dedicated Wealth Desk
        "KEYPRIVCCA": "5554002",               # Key Privilege Priority Queue
        "MMCCA_PRIMACY": "5553001",            # Retail Primacy Queue
        "MMCCA_SPANISH": "5553002",            # Spanish VIP Queue (20-char EDW limit compliant)
        "MMCCA": "5553006",                    # Standard Consumer Queue fallback
        "LR_DEFAULT": "5552912",               # Laurel Road Dedicated Desk
    }

    @classmethod
    def generate_odyssey_session_payload(cls, profile: CustomerProfile, trc: str, intent: str = "privilegeInquiry") -> Dict[str, Any]:
        """
        Builds the Odyssey (DFCX) context payload ('transferData') passed to Genesys via GVP.
        """
        chk = profile.accounts[0] if profile.accounts else None
        active_bank = chk.bank_number if chk else "0101"
        active_prod = chk.prod_code.value if chk else "DDA"

        is_fee_at_risk = "false"
        if profile.fee_status and not profile.fee_status.is_fee_waived:
            is_fee_at_risk = "true"

        total_balance = f"{profile.fee_status.total_combined_balance:.2f}" if profile.fee_status else "0.00"

        return {
            "accountContextPayload": {
                "activeBank": active_bank,
                "activeProdCode": active_prod,
                "accountNumber": chk.account_number if chk else "UNKNOWN",
                "customerIpi": profile.customer_ipi,
                "householdRelationshipGroup": profile.relationship_group,
                "customerTier": profile.customer_tier.value,
            },
            "transferData": {
                "masterBotId": "privilegeConcierge",
                "transferRouteCode": trc,
                "pbxRoutePoint": cls.PBX_ROUTE_POINTS.get(trc, "5554002"),
                "callerIntent": intent,
                "languageCode": profile.preferred_language.value,
                "attachedData": {
                    "CustomerIPI": profile.customer_ipi,
                    "CustomerTier": profile.customer_tier.value,
                    "RelationshipGroup": profile.relationship_group,
                    "PriorityQueue": "TRUE",
                    "StopPayment": "false",
                    "MaintenanceFeeAtRisk": is_fee_at_risk,
                    "TotalCombinedBalance": total_balance,
                    "LanguageCode": profile.preferred_language.value,
                    "TRC": trc,
                    "TargetRoutePoint": cls.PBX_ROUTE_POINTS.get(trc, "5554002")
                }
            }
        }
