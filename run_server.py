"""
Standalone HTTP Server & REST API for KeyBank Key Privilege Multi-Agent System.
Hackathon Team 53 - Team Innovators.
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from src.root_agent import RootPrivilegeAgent
from src.customer_service import CustomerService
from src.fee_avoidance_engine import FeeAvoidanceEngine
from src.preference_store import PreferenceStore
from src.voice_auth_agent import VoiceAuthAgent
from src.models import Language

PORT = int(os.environ.get("PORT", 8080))
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


class AgentApiHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    agent = RootPrivilegeAgent()
    voice_agent = VoiceAuthAgent(agent)
    active_profile = CustomerService.get_sample_customers()["031379551"] # Default to Eleanor Vance (At-Risk)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/customers":
            customers = CustomerService.get_sample_customers()
            summary = []
            for ipi, c in customers.items():
                fee_stat = FeeAvoidanceEngine.evaluate(c)
                summary.append({
                    "ipi": c.customer_ipi,
                    "name": c.customer_name,
                    "phone": c.phone_number,
                    "tier": c.customer_tier.value,
                    "group": c.relationship_group,
                    "language": c.preferred_language.value,
                    "fee_waived": fee_stat.is_fee_waived,
                    "total_balance": fee_stat.total_combined_balance,
                    "days_remaining": fee_stat.days_remaining_in_cycle
                })
            self._send_json({"customers": summary, "active_ipi": self.active_profile.customer_ipi})
            return

        if parsed.path == "/api/preferences":
            prefs = PreferenceStore.load_all()
            self._send_json({"preferences": prefs})
            return

        if parsed.path == "/api/voice/status":
            va = AgentApiHandler.voice_agent
            self._send_json({
                "call_active": va.call_active,
                "state": va.state.value,
                "collected_name": va.collected_name,
                "collected_phone": va.collected_phone,
                "authenticated_ipi": va.authenticated_profile.customer_ipi if va.authenticated_profile else None,
                "active_language": va.authenticated_profile.preferred_language.value if va.authenticated_profile else None
            })
            return

        if parsed.path == "/api/profile":
            fee_stat = FeeAvoidanceEngine.evaluate(self.active_profile)
            p = self.active_profile
            data = {
                "ipi": p.customer_ipi,
                "name": p.customer_name,
                "phone": p.phone_number,
                "ssn_last4": p.ssn_last4,
                "tier": p.customer_tier.value,
                "relationship_group": p.relationship_group,
                "language": p.preferred_language.value,
                "is_key_at_work": p.is_key_at_work,
                "fee_status": {
                    "monthly_charge": fee_stat.monthly_service_charge,
                    "cycle_end": fee_stat.cycle_end_date,
                    "days_remaining": fee_stat.days_remaining_in_cycle,
                    "is_waived": fee_stat.is_fee_waived,
                    "winning_method": fee_stat.winning_waiver_method,
                    "rule1_balance": fee_stat.total_combined_balance,
                    "rule1_met": fee_stat.rule1_met,
                    "rule2_mortgage_autopay": fee_stat.mortgage_auto_deduction_amount,
                    "rule2_met": fee_stat.rule2_met,
                    "rule3_direct_deposits": fee_stat.cycle_direct_deposits,
                    "rule3_met": fee_stat.rule3_met,
                    "alert_message": fee_stat.alert_message,
                    "remedy": fee_stat.actionable_remedy
                },
                "accounts": [
                    {
                        "account_number": a.account_number,
                        "account_name": a.account_name,
                        "prod_code": a.prod_code.value,
                        "current_balance": a.current_balance,
                        "available_balance": a.available_balance,
                        "details": a.details
                    }
                    for a in p.accounts
                ]
            }
            self._send_json(data)
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        if parsed.path == "/api/voice/start":
            resp = AgentApiHandler.voice_agent.start_call()
            self._send_json(self._serialize_response(resp))
            return

        if parsed.path == "/api/voice/turn":
            user_text = payload.get("message", "")
            resp = AgentApiHandler.voice_agent.process_turn(user_text)
            if AgentApiHandler.voice_agent.authenticated_profile:
                AgentApiHandler.active_profile = AgentApiHandler.voice_agent.authenticated_profile
            self._send_json(self._serialize_response(resp))
            return

        if parsed.path == "/api/voice/reset-prefs":
            ipi = payload.get("customer_ipi", "031379551")
            PreferenceStore.clear_preference(ipi)
            self._send_json({"status": "cleared", "customer_ipi": ipi})
            return

        if parsed.path == "/api/session/init":
            ipi = payload.get("customer_ipi", "031379551")
            customers = CustomerService.get_sample_customers()
            if ipi in customers:
                AgentApiHandler.active_profile = customers[ipi]
            resp = self.agent.initialize_session(self.active_profile)
            self._send_json(self._serialize_response(resp))
            return

        if parsed.path == "/api/chat":
            user_text = payload.get("message", "")
            resp = self.agent.route_and_execute(self.active_profile, user_text)
            self._send_json(self._serialize_response(resp))
            return

        if parsed.path == "/api/switch-language":
            lang = payload.get("language", "ENG")
            self.active_profile.preferred_language = Language.SPA if lang == "SPA" else Language.ENG
            resp = self.agent.subagents["language_selection"].process(self.active_profile, f"switch to {lang}", {})
            self._send_json(self._serialize_response(resp))
            return

        self.send_response(404)
        self.end_headers()

    def _serialize_response(self, resp):
        return {
            "subagent_id": resp.subagent_id,
            "subagent_title": resp.subagent_title,
            "message": resp.message,
            "speech_message": resp.speech_message,
            "audio_prompt_code": resp.audio_prompt_code,
            "fee_reminder_banner": resp.fee_reminder_banner,
            "structured_data": resp.structured_data,
            "suggested_quick_replies": resp.suggested_quick_replies,
            "handover_required": resp.handover_required,
            "routing_context": {
                "transfer_route_code": resp.routing_context.transfer_route_code,
                "master_bot_id": resp.routing_context.master_bot_id,
                "target_queue": resp.routing_context.target_queue,
                "priority_level": resp.routing_context.priority_level,
                "genesys_attached_data": resp.routing_context.genesys_attached_data
            } if resp.routing_context else None
        }

    def _send_json(self, data):
        out = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(out)


def run():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, AgentApiHandler)
    print(f"Key Privilege Voice & Chat Multi-Agent Server running at http://127.0.0.1:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    run()
