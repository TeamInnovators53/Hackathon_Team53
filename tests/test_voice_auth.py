"""
Unit Tests for Inbound Voice Call Authentication & Language Preference Flow.
Hackathon Team 53 - Team Innovators.
"""

import os
import pytest
from src.voice_auth_agent import VoiceAuthAgent, VoiceCallState
from src.preference_store import PreferenceStore
from src.models import Language


@pytest.fixture
def temp_pref_file(tmp_path):
    f = tmp_path / "test_prefs.json"
    return str(f)


@pytest.fixture
def auth_agent(temp_pref_file):
    # Set default store to temp file for isolated testing
    PreferenceStore.DEFAULT_STORE_PATH = temp_pref_file
    return VoiceAuthAgent()


def test_first_time_caller_onboarding(auth_agent):
    """
    Test Step-by-Step Flow:
    1. Caller connects -> Asks for First & Last Name
    2. Caller gives Name -> Asks for Phone
    3. Caller gives Phone -> Asks for SSN
    4. Caller gives SSN -> Validates & Prompts for Language Selection
    5. Caller selects 'Spanish' -> Preference saved, enters Concierge in Spanish
    """
    # 1. Start call
    r1 = auth_agent.start_call()
    assert auth_agent.state == VoiceCallState.COLLECT_NAME
    assert "first and last name" in r1.speech_message

    # 2. Provide Name
    r2 = auth_agent.process_turn("Eleanor Vance")
    assert auth_agent.state == VoiceCallState.COLLECT_PHONE
    assert "10-digit telephone number" in r2.speech_message
    assert "Eleanor" in r2.speech_message

    # 3. Provide Phone Number
    r3 = auth_agent.process_turn("385-456-9511")
    assert auth_agent.state == VoiceCallState.COLLECT_SSN
    assert "last 4 digits of your Social Security Number" in r3.speech_message

    # 4. Provide SSN Last 4
    r4 = auth_agent.process_turn("3584")
    assert auth_agent.state == VoiceCallState.COLLECT_LANGUAGE_NEW
    assert "Identity verified" in r4.speech_message
    assert "Please select your preferred language" in r4.speech_message

    # 5. Select Spanish
    r5 = auth_agent.process_turn("Spanish")
    assert auth_agent.state == VoiceCallState.AUTHENTICATED
    assert auth_agent.authenticated_profile is not None
    assert auth_agent.authenticated_profile.preferred_language == Language.SPA

    # Verify preference was saved to store!
    saved_pref = PreferenceStore.get_preference("031379551")
    assert saved_pref == "SPA"

    # Root agent menu was initialized with Eleanor's fee alert
    assert "Key Privilege" in r5.message


def test_returning_caller_with_stored_preference(auth_agent):
    """
    Test Returning Caller Flow:
    1. Pre-save preference as 'SPA' (Spanish)
    2. Call and authenticate
    3. Bot detects stored preference and asks: "Tenemos el español registrado... ¿Desea continuar en español?"
    4. User confirms "Yes" -> Remains in Spanish
    """
    PreferenceStore.save_preference("031379551", "SPA")

    # Start call & Authenticate
    auth_agent.start_call()
    auth_agent.process_turn("Eleanor Vance")
    auth_agent.process_turn("3854569511")
    r_auth = auth_agent.process_turn("3584")

    # Bot recognized stored language and asked for confirmation!
    assert auth_agent.state == VoiceCallState.CONFIRM_LANGUAGE_RETURNING
    assert "español" in r_auth.speech_message.lower()

    # User confirms: "Sí, continuar"
    r_confirm = auth_agent.process_turn("Sí, continuar")
    assert auth_agent.state == VoiceCallState.AUTHENTICATED
    assert auth_agent.authenticated_profile.preferred_language == Language.SPA


def test_returning_caller_switches_preference(auth_agent):
    """
    Returning caller changes preference from Spanish to English.
    """
    PreferenceStore.save_preference("031379551", "SPA")

    auth_agent.start_call()
    auth_agent.process_turn("Eleanor Vance")
    auth_agent.process_turn("(385) 456-9511")
    auth_agent.process_turn("3584")

    # User requests English switch: "Change to English"
    auth_agent.process_turn("Change to English")
    assert auth_agent.authenticated_profile.preferred_language == Language.ENG

    # Preference updated in store!
    assert PreferenceStore.get_preference("031379551") == "ENG"


def test_invalid_credentials_retry(auth_agent):
    """
    Wrong SSN triggers validation failure and asks caller to restart from name.
    """
    auth_agent.start_call()
    auth_agent.process_turn("Eleanor Vance")
    auth_agent.process_turn("3854569511")
    r_fail = auth_agent.process_turn("9999") # Wrong SSN!

    assert "unable to verify" in r_fail.speech_message.lower()
    assert auth_agent.state == VoiceCallState.COLLECT_NAME
