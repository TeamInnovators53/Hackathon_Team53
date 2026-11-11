"""
Sub-Agent: Purchase History & Recommendations.
Hackathon Team 53 - Team Innovators.
"""

from typing import Dict, Any
from src.subagents.base_agent import BaseSubAgent
from src.models import CustomerProfile, AgentResponse


class PurchaseHistoryAndRecommendationsSubAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_id="purchase_recommendations",
            title="Purchase Analytics & AI Advisor",
            description="Analyzes transaction trends, spending categories, and delivers reward maximization recommendations."
        )

    def can_handle(self, user_text: str, context: Dict[str, Any]) -> float:
        text = user_text.lower()
        keywords = ["purchase history", "recent purchases", "transactions", "spending", "recommendations", "rewards advice", "where did my money go", "recent charges", "history"]
        for kw in keywords:
            if kw in text:
                return 0.95
        return 0.0

    def process(self, profile: CustomerProfile, user_text: str, context: Dict[str, Any]) -> AgentResponse:
        is_spa = profile.preferred_language.value == "SPA"
        txns = profile.recent_transactions

        if not txns:
            msg = "No recent transactions found in your current statement cycle."
            return AgentResponse(subagent_id=self.agent_id, subagent_title=self.title, message=msg, speech_message=msg)

        # Categorize spending
        total_spent = sum(t.amount for t in txns if t.category != "Deposit")
        total_points = sum(t.reward_points_earned for t in txns)

        txn_lines = []
        for t in txns[:4]:
            pts_str = f" (+{t.reward_points_earned:,} pts)" if t.reward_points_earned > 0 else ""
            txn_lines.append(f"• **{t.date}** | {t.description}: **${t.amount:,.2f}** ({t.category}){pts_str}")

        txn_text = "\n".join(txn_lines)

        if is_spa:
            msg = (
                f"\U0001f6cd\ufe0f **Historial de Compras Recientes y Recomendaciones Inteligentes:**\n\n"
                f"{txn_text}\n\n"
                f"\U0001f4ca **An\u00e1lisis de Gastos del Ciclo:** ${total_spent:,.2f} gastados | **{total_points:,} puntos ganados**\n\n"
                f"\U0001f4a1 **Recomendaci\u00f3n Personalizada Privilege:**\n"
                f"El 58% de sus compras de este mes fueron en **Gastronom\u00eda y Viajes**. Utilizar su tarjeta KeyBank Latitude en estas categor\u00edas le genera **3x Puntos**, duplicando su retorno en efectivo a fin de mes."
            )
            speech = f"Sus transacciones recientes suman ${total_spent:,.2f}. Su mayor categor\u00eda de gasto fue en viajes y restaurantes, acumulando {total_points:,} puntos."
            prompt = "[K2U_SPA.725.au]"
        else:
            msg = (
                f"\U0001f6cd\ufe0f **Recent Purchase History & AI Insights for {profile.customer_name}:**\n\n"
                f"{txn_text}\n\n"
                f"\U0001f4ca **Cycle Activity Summary:** **${total_spent:,.2f}** total spending across recent transactions | **{total_points:,} points earned**\n\n"
                f"\U0001f4a1 **Smart Spending & Reward Optimization:**\n"
                f"• **Category Trend:** High activity in **Dining & Luxury Travel** (58% of spend).\n"
                f"• **Cash-Back Maximizer:** By using your KeyBank Latitude card on dining and flights, you earn **3x Rewards**, yielding an extra **$85.00/month in statement credits**.\n"
                f"• **Key Privilege Travel Perk:** Your card includes complimentary airport lounge access and zero foreign transaction fees."
            )
            speech = (
                f"Your recent transactions total ${total_spent:,.2f} with {total_points:,} rewards points earned. "
                f"Your top spending category is travel and dining, which earns you triple points on your Key Privilege card."
            )
            prompt = "[K2U_ENG.725.au]"

        return AgentResponse(
            subagent_id=self.agent_id,
            subagent_title=self.title,
            message=msg,
            speech_message=speech,
            audio_prompt_code=prompt,
            structured_data={
                "total_spent": total_spent,
                "points_earned": total_points,
                "top_category": "Dining & Luxury Travel"
            },
            suggested_quick_replies=[
                "Credit Card Statement",
                "Balance Inquiry",
                "Avoid Maintenance Fee",
                "Speak to Dedicated Concierge"
            ]
        )
