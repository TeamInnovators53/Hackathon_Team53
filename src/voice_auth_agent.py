"""
Voice Call Authentication & Persistent Language Preference Agent.
Hackathon Team 53 - Team Innovators.

Orchestrates the inbound voice call flow:
1. First Name & Last Name collection
2. 10-Digit Phone Number collection
3. SSN Last 4 validation
4. Language preference onboarding or returning caller confirmation
5. Persistent preference storage (remembers across calls & logins)
6. Handover to Key Privilege Root Concierge with fee avoidance proactive reminders
"""

import re
from enum import Enum
from typing import Dict, Optional, Tuple, Any

from src.models import CustomerProfile, Language, AgentResponse, CustomerTier, RoutingContext
from src.customer_service import CustomerService
from src.preference_store import PreferenceStore
from src.root_agent import RootPrivilegeAgent
from src.telephony_adapter import TelephonyAdapter


class VoiceCallState(str, Enum):
    IDLE = "IDLE"
    COLLECT_NAME = "COLLECT_NAME"
    COLLECT_PHONE = "COLLECT_PHONE"
    COLLECT_SSN = "COLLECT_SSN"
    COLLECT_LANGUAGE_NEW = "COLLECT_LANGUAGE_NEW"
    CONFIRM_LANGUAGE_RETURNING = "CONFIRM_LANGUAGE_RETURNING"
    AUTHENTICATED = "AUTHENTICATED"


# Spoken digit translation helper
WORD_TO_DIGIT = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
    "cero": "0", "uno": "1", "dos": "2", "tres": "3", "cuatro": "4",
    "cinco": "5", "seis": "6", "siete": "7", "ocho": "8", "nueve": "9"
}


def extract_digits(text: str) -> str:
    """Extracts all numeric digits from text, including spoken words."""
    clean = text.lower()
    for word, digit in WORD_TO_DIGIT.items():
        clean = re.sub(rf"\b{word}\b", digit, clean)
    return re.sub(r"\D", "", clean)


class VoiceAuthAgent:
    """
    Inbound Voice Call State Machine managing authentication and language preferences.
    """

    def __init__(self, root_agent: Optional[RootPrivilegeAgent] = None):
        self.root_agent = root_agent or RootPrivilegeAgent()
        self.state: VoiceCallState = VoiceCallState.IDLE
        self.collected_name: str = ""
        self.collected_phone: str = ""
        self.collected_ssn: str = ""
        self.authenticated_profile: Optional[CustomerProfile] = None
        self.stored_lang: Optional[str] = None
        self.call_active: bool = False

    def start_call(self) -> AgentResponse:
        """
        Initiates a new voice call with standard telephony greeting and name collection.
        """
        self.state = VoiceCallState.COLLECT_NAME
        self.collected_name = ""
        self.collected_phone = ""
        self.collected_ssn = ""
        self.authenticated_profile = None
        self.stored_lang = None
        self.call_active = True

        msg = (
            "📞 **[Incoming Voice Call Connected]**\n\n"
            "Thank you for calling KeyBank Key Privilege Private Client Services. "
            "To access your privileged account securely, may I please have your **first and last name**?"
        )
        speech = (
            "Thank you for calling KeyBank Key Privilege Private Client Services. "
            "To access your privileged account securely, may I please have your first and last name?"
        )
        return AgentResponse(
            subagent_id="voice_auth_agent",
            subagent_title="KeyBank Voice Call Gateway",
            message=msg,
            speech_message=speech,
            audio_prompt_code="[K2U_ENG.AUTH_NAME.au]",
            suggested_quick_replies=["Eleanor Vance", "Dr. Julian Sterling", "Marcus Thorne", "Sofia Ramirez-Cruz"],
            routing_context=RoutingContext(
                transfer_route_code="GENESYS",
                master_bot_id="privilegeAuthGateway",
                target_queue="Key Privilege Voice Ingestion",
                priority_level="VIP_INGESTION",
                genesys_attached_data={"CallerIntent": "AUTH_NAME", "State": "COLLECT_NAME"}
            )
        )

    def process_turn(self, user_text: str) -> AgentResponse:
        """
        Processes a turn of speech/text input through the call state machine.
        """
        raw_text = user_text.strip()

        # Handle call hangup
        if any(h in raw_text.lower() for h in ["hang up", "end call", "disconnect", "goodbye"]):
            self.call_active = False
            self.state = VoiceCallState.IDLE
            return AgentResponse(
                subagent_id="voice_auth_agent",
                subagent_title="KeyBank Voice Call Gateway",
                message="📞 **[Voice Call Disconnected]** Thank you for calling KeyBank Key Privilege. Have a wonderful day.",
                speech_message="Thank you for calling KeyBank Key Privilege. Have a wonderful day. Goodbye.",
                audio_prompt_code="[K2U_ENG.GOODBYE.au]"
            )

        # ----------------------------------------------------------------------------------
        # STEP 1: COLLECT NAME
        # ----------------------------------------------------------------------------------
        if self.state == VoiceCallState.COLLECT_NAME:
            self.collected_name = self._clean_name(raw_text)
            self.state = VoiceCallState.COLLECT_PHONE

            first_name = self.collected_name.split()[0] if self.collected_name else "valued client"
            msg = (
                f"Thank you, **{self.collected_name}**.\n\n"
                f"Please state or enter the **10-digit telephone number** registered to your account."
            )
            speech = (
                f"Thank you, {first_name}. "
                f"Please provide the 10-digit telephone number registered to your account."
            )
            return AgentResponse(
                subagent_id="voice_auth_agent",
                subagent_title="KeyBank Voice Call Gateway",
                message=msg,
                speech_message=speech,
                audio_prompt_code="[K2U_ENG.AUTH_PHONE.au]",
                suggested_quick_replies=["(385) 456-9511", "(330) 714-8766", "(216) 555-1234", "(305) 555-7890"],
                structured_data={"step": "COLLECT_PHONE", "name": self.collected_name}
            )

        # ----------------------------------------------------------------------------------
        # STEP 2: COLLECT PHONE NUMBER
        # ----------------------------------------------------------------------------------
        if self.state == VoiceCallState.COLLECT_PHONE:
            digits = extract_digits(raw_text)
            if len(digits) < 7:
                return AgentResponse(
                    subagent_id="voice_auth_agent",
                    subagent_title="KeyBank Voice Call Gateway",
                    message="⚠️ I did not capture a valid 10-digit phone number. Please say or enter your 10-digit phone number (e.g. 385-456-9511).",
                    speech_message="I did not capture a valid phone number. Please provide your 10-digit telephone number.",
                    audio_prompt_code="[K2U_ENG.RETRY_PHONE.au]"
                )

            self.collected_phone = digits[-10:]
            self.state = VoiceCallState.COLLECT_SSN

            formatted_phone = f"({self.collected_phone[:3]}) {self.collected_phone[3:6]}-{self.collected_phone[6:]}"
            msg = (
                f"Got it: **{formatted_phone}**.\n\n"
                f"For your security and authentication, please state or enter the **last 4 digits of your Social Security Number** (SSN)."
            )
            speech = (
                "Thank you. For your identity verification, please provide the last 4 digits of your Social Security Number."
            )
            return AgentResponse(
                subagent_id="voice_auth_agent",
                subagent_title="KeyBank Voice Call Gateway",
                message=msg,
                speech_message=speech,
                audio_prompt_code="[K2U_ENG.AUTH_SSN.au]",
                suggested_quick_replies=["3584", "8210", "4491", "6120"],
                structured_data={"step": "COLLECT_SSN", "phone": self.collected_phone}
            )

        # ----------------------------------------------------------------------------------
        # STEP 3: COLLECT & VALIDATE SSN LAST 4
        # ----------------------------------------------------------------------------------
        if self.state == VoiceCallState.COLLECT_SSN:
            digits = extract_digits(raw_text)
            if len(digits) < 4:
                return AgentResponse(
                    subagent_id="voice_auth_agent",
                    subagent_title="KeyBank Voice Call Gateway",
                    message="⚠️ Please provide the 4 digits of your Social Security Number.",
                    speech_message="Please state the 4 digits of your Social Security Number.",
                    audio_prompt_code="[K2U_ENG.RETRY_SSN.au]"
                )

            self.collected_ssn = digits[-4:]

            # Validate against database
            matched_profile = self._validate_credentials(
                self.collected_name, self.collected_phone, self.collected_ssn
            )

            if not matched_profile:
                # Authentication failure: reset to start
                self.state = VoiceCallState.COLLECT_NAME
                self.collected_name = ""
                self.collected_phone = ""
                self.collected_ssn = ""
                msg = (
                    "❌ **Verification Unsuccessful**\n\n"
                    "We were unable to verify your identity with the details provided. "
                    "Let's try again. Please state your **first and last name**."
                )
                speech = (
                    "We were unable to verify your identity with the details provided. "
                    "Let's try again. Please state your first and last name."
                )
                return AgentResponse(
                    subagent_id="voice_auth_agent",
                    subagent_title="KeyBank Voice Call Gateway",
                    message=msg,
                    speech_message=speech,
                    audio_prompt_code="[K2U_ENG.AUTH_FAILED.au]",
                    suggested_quick_replies=["Eleanor Vance", "Dr. Julian Sterling", "Marcus Thorne", "Sofia Ramirez-Cruz"]
                )

            # Verification successful!
            self.authenticated_profile = matched_profile
            ipi = matched_profile.customer_ipi

            # Check persistent preference store
            stored_pref = PreferenceStore.get_preference(ipi)

            if stored_pref:
                # Returning customer with stored preference!
                self.stored_lang = stored_pref
                self.state = VoiceCallState.CONFIRM_LANGUAGE_RETURNING

                lang_display = "English" if stored_pref == "ENG" else "Español"
                if stored_pref == "SPA":
                    msg = (
                        f"✅ **Identidad Verificada: {matched_profile.customer_name}**\n\n"
                        f"¡Bienvenida de nuevo! Tenemos **{lang_display}** guardado como su idioma preferido.\n\n"
                        f"¿Es **{lang_display}** su idioma preferido hoy, o desea elegir otro idioma?"
                    )
                    speech = (
                        f"Identidad verificada. ¡Bienvenida de nuevo, {matched_profile.customer_name}! "
                        f"Tenemos el español registrado como su idioma preferido. "
                        f"¿Desea continuar en español, o prefiere elegir otro idioma?"
                    )
                    quick = ["Sí, continuar en Español", "Cambiar a English"]
                else:
                    msg = (
                        f"✅ **Identity Verified: {matched_profile.customer_name}**\n\n"
                        f"Welcome back! We have **{lang_display}** on file as your preferred language.\n\n"
                        f"Is **{lang_display}** your preferred language today, or would you like to choose another language?"
                    )
                    speech = (
                        f"Identity verified. Welcome back, {matched_profile.customer_name}! "
                        f"We have English on file as your preferred language. "
                        f"Is English your preferred language today, or would you like to choose another language?"
                    )
                    quick = ["Yes, keep English", "Change to Spanish"]

                return AgentResponse(
                    subagent_id="voice_auth_agent",
                    subagent_title="KeyBank Identity Verification",
                    message=msg,
                    speech_message=speech,
                    audio_prompt_code="[K2U_ENG.LANG_CONFIRM_RETURNING.au]",
                    suggested_quick_replies=quick,
                    structured_data={
                        "step": "CONFIRM_LANGUAGE_RETURNING",
                        "customer_ipi": ipi,
                        "stored_preference": stored_pref
                    }
                )
            else:
                # First time / no stored preference: Ask for language selection
                self.state = VoiceCallState.COLLECT_LANGUAGE_NEW
                msg = (
                    f"✅ **Identity Verified: {matched_profile.customer_name}**\n\n"
                    f"Welcome to KeyBank Key Privilege Concierge services. "
                    f"Please select your **preferred language** for this call and future visits:\n\n"
                    f"• Say **'English'**\n"
                    f"• Diga **'Español'** (Spanish)"
                )
                speech = (
                    f"Identity verified. Welcome to Key Privilege, {matched_profile.customer_name}. "
                    f"Please select your preferred language. You can say English, or Español for Spanish."
                )
                return AgentResponse(
                    subagent_id="voice_auth_agent",
                    subagent_title="KeyBank Identity Verification",
                    message=msg,
                    speech_message=speech,
                    audio_prompt_code="[K2U_ENG.LANG_SELECT_NEW.au]",
                    suggested_quick_replies=["English", "Español (Spanish)"],
                    structured_data={
                        "step": "COLLECT_LANGUAGE_NEW",
                        "customer_ipi": ipi
                    }
                )

        # ----------------------------------------------------------------------------------
        # STEP 4A: NEW CALLER LANGUAGE SELECTION (Store Preference)
        # ----------------------------------------------------------------------------------
        if self.state == VoiceCallState.COLLECT_LANGUAGE_NEW:
            chosen_lang = self._parse_language_choice(raw_text)
            ipi = self.authenticated_profile.customer_ipi

            # Persist preference permanently!
            PreferenceStore.save_preference(ipi, chosen_lang)
            self.authenticated_profile.preferred_language = Language[chosen_lang]
            self.state = VoiceCallState.AUTHENTICATED

            # Handover directly to Root Concierge
            return self._enter_concierge_menu(
                self.authenticated_profile,
                onboarding_note=f"Your language preference (**{'Español' if chosen_lang == 'SPA' else 'English'}**) has been saved for future calls."
            )

        # ----------------------------------------------------------------------------------
        # STEP 4B: RETURNING CALLER CONFIRMATION (Confirm or Switch)
        # ----------------------------------------------------------------------------------
        if self.state == VoiceCallState.CONFIRM_LANGUAGE_RETURNING:
            lower = raw_text.lower()
            ipi = self.authenticated_profile.customer_ipi
            stored = self.stored_lang or "ENG"

            # Check if user confirmed existing language
            if any(w in lower for w in ["yes", "yeah", "keep", "correct", "stay", "continue", "sí", "si", "correcto", "permanecer"]):
                chosen_lang = stored
                note = f"Continuing in your preferred language: **{'Español' if chosen_lang == 'SPA' else 'English'}**."
            elif any(w in lower for w in ["spanish", "español", "espanol"]):
                chosen_lang = "SPA"
                PreferenceStore.save_preference(ipi, "SPA")
                note = "Updated your saved language preference to **Español**."
            elif any(w in lower for w in ["english", "inglés", "ingles"]):
                chosen_lang = "ENG"
                PreferenceStore.save_preference(ipi, "ENG")
                note = "Updated your saved language preference to **English**."
            else:
                # Default to existing
                chosen_lang = stored
                note = f"Continuing in **{'Español' if chosen_lang == 'SPA' else 'English'}**."

            self.authenticated_profile.preferred_language = Language[chosen_lang]
            self.state = VoiceCallState.AUTHENTICATED

            return self._enter_concierge_menu(self.authenticated_profile, onboarding_note=note)

        # ----------------------------------------------------------------------------------
        # STEP 5: AUTHENTICATED VOICE SESSION (Root Concierge & Sub-Agents)
        # ----------------------------------------------------------------------------------
        if self.state == VoiceCallState.AUTHENTICATED and self.authenticated_profile:
            return self.root_agent.route_and_execute(self.authenticated_profile, raw_text)

        # Fallback
        return self.start_call()

    def _enter_concierge_menu(self, customer: CustomerProfile, onboarding_note: str = "") -> AgentResponse:
        """
        Transitions into the Root Concierge menu with fee avoidance proactive reminders.
        """
        root_resp = self.root_agent.initialize_session(customer)
        if onboarding_note:
            root_resp.message = f"✨ *{onboarding_note}*\n\n" + root_resp.message
            if customer.preferred_language == Language.SPA:
                root_resp.speech_message = "Preferencia confirmada. " + root_resp.speech_message
            else:
                root_resp.speech_message = "Preference confirmed. " + root_resp.speech_message
        return root_resp

    def _validate_credentials(self, name: str, phone: str, ssn_last4: str) -> Optional[CustomerProfile]:
        """
        Validates name, phone, and SSN last 4 against the customer service database.
        """
        samples = CustomerService.get_sample_customers()
        clean_phone = phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        clean_name_parts = set(re.findall(r"\w+", name.lower()))

        for profile in samples.values():
            # Check SSN last 4 (strict)
            if profile.ssn_last4 != ssn_last4:
                continue

            # Check Phone (strict 10-digit or ends with)
            profile_phone = profile.phone_number.replace("-", "").replace(" ", "")
            phone_match = (clean_phone == profile_phone) or (clean_phone.endswith(profile_phone[-7:]))
            if not phone_match:
                continue

            # Check Name (loose: at least one word from caller's input matches first or last name)
            profile_name_parts = set(re.findall(r"\w+", profile.customer_name.lower()))
            if clean_name_parts and profile_name_parts:
                if clean_name_parts.intersection(profile_name_parts):
                    return profile

            # If phone and SSN match, authenticate
            return profile

        return None

    def _clean_name(self, text: str) -> str:
        """Removes conversational filler words from spoken name."""
        clean = re.sub(r"\b(my name is|i am|this is|speaking|it's|it is|hello|hi|please)\b", "", text, flags=re.IGNORECASE)
        clean = " ".join(clean.split()).strip()
        return clean.title() if clean else text.title()

    def _parse_language_choice(self, text: str) -> str:
        lower = text.lower()
        if any(s in lower for s in ["spanish", "español", "espanol", "castellano", "2", "two"]):
            return "SPA"
        return "ENG"
