/**
 * KeyBank Key Privilege Multi-Agent System - Client Application
 * Hackathon Team 53 - Team Innovators.
 *
 * Includes:
 * 1. Interactive Hands-Free Inbound Voice Call with Identity Verification:
 *    - First Name & Last Name
 *    - 10-Digit Phone Number
 *    - SSN Last 4 Validation
 * 2. Persistent Language Preference Management:
 *    - New Caller: Prompts for English or Spanish, saves preference permanently.
 *    - Returning Caller: Welcomes back, checks stored preference ("We have English/Spanish as your preferred language. Is this your preferred language, or choose another?").
 * 3. Google TTS (Text-to-Speech) Audio Engine with Animated Waveform Sync & Hands-Free Chaining.
 * 4. Dual-Tone Multi-Frequency (DTMF) Web Audio Touch-Tone Dialpad.
 */

document.addEventListener("DOMContentLoaded", () => {
    // State
    let activeCustomerIpi = "031379551";
    let isTtsEnabled = true;
    let recognition = null;
    let isRecording = false;
    let audioCtx = null;
    let isVoiceCallActive = false;
    let activeAudio = null;

    // DOM Elements
    const customerSelect = document.getElementById("customerSelect");
    const langToggleBtn = document.getElementById("langToggleBtn");
    const currentLangLabel = document.getElementById("currentLangLabel");
    const messageStream = document.getElementById("messageStream");
    const userInput = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const micBtn = document.getElementById("micBtn");
    const speechToggleBtn = document.getElementById("speechToggleBtn");
    const ttsIcon = document.getElementById("ttsIcon");
    const quickRepliesBar = document.getElementById("quickRepliesBar");
    const proactiveAlertBanner = document.getElementById("proactiveAlertBanner");
    const proactiveAlertContent = document.getElementById("proactiveAlertContent");
    const voiceWaveform = document.getElementById("voiceWaveform");
    const voiceStatusLabel = document.getElementById("voiceStatusLabel");

    // Voice Call DOM
    const voiceCallBtn = document.getElementById("voiceCallBtn");
    const resetPrefBtn = document.getElementById("resetPrefBtn");
    const endCallBtn = document.getElementById("endCallBtn");
    const voiceCallBanner = document.getElementById("voiceCallBanner");
    const callStateBadge = document.getElementById("callStateBadge");
    const callBannerText = document.getElementById("callBannerText");

    // Profile DOM
    const profName = document.getElementById("profName");
    const profIpi = document.getElementById("profIpi");
    const profPhone = document.getElementById("profPhone");
    const profGroup = document.getElementById("profGroup");
    const profKeyAtWork = document.getElementById("profKeyAtWork");
    const tierBadge = document.getElementById("tierBadge");

    // Fee DOM
    const feeWaiverBadge = document.getElementById("feeWaiverBadge");
    const rule1Current = document.getElementById("rule1Current");
    const rule1Progress = document.getElementById("rule1Progress");
    const rule1Icon = document.getElementById("rule1Icon");
    const rule2Current = document.getElementById("rule2Current");
    const rule2Progress = document.getElementById("rule2Progress");
    const rule2Icon = document.getElementById("rule2Icon");
    const rule3Current = document.getElementById("rule3Current");
    const rule3Progress = document.getElementById("rule3Progress");
    const rule3Icon = document.getElementById("rule3Icon");
    const daysRemainingText = document.getElementById("daysRemainingText");
    const remedyText = document.getElementById("remedyText");
    const remedyBox = document.getElementById("remedyBox");

    // Telephony Inspector DOM
    const activeTrcBadge = document.getElementById("activeTrcBadge");
    const inspectQueue = document.getElementById("inspectQueue");
    const inspectBotId = document.getElementById("inspectBotId");
    const inspectSubagent = document.getElementById("inspectSubagent");
    const inspectPrompt = document.getElementById("inspectPrompt");
    const inspectKvps = document.getElementById("inspectKvps");
    const agentTitle = document.getElementById("agentTitle");

    // DTMF Panel DOM
    const toggleDtmfBtn = document.getElementById("toggleDtmfBtn");
    const closeDtmfBtn = document.getElementById("closeDtmfBtn");
    const dtmfPanel = document.getElementById("dtmfPanel");
    const dtmfDisplay = document.getElementById("dtmfDisplay");

    // =========================================================================
    // 1. Web Audio DTMF Dual-Tone Generator
    // =========================================================================
    function playDtmfTone(key) {
        try {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === "suspended") {
                audioCtx.resume();
            }

            const dtmfFreqs = {
                "1": [697, 1209], "2": [697, 1336], "3": [697, 1477],
                "4": [770, 1209], "5": [770, 1336], "6": [770, 1477],
                "7": [852, 1209], "8": [852, 1336], "9": [852, 1477],
                "*": [941, 1209], "0": [941, 1336], "#": [941, 1477]
            };

            const freqs = dtmfFreqs[key];
            if (!freqs) return;

            const osc1 = audioCtx.createOscillator();
            const osc2 = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc1.type = "sine";
            osc1.frequency.value = freqs[0];
            osc2.type = "sine";
            osc2.frequency.value = freqs[1];

            gain.gain.value = 0.15;
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);

            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(audioCtx.destination);

            osc1.start();
            osc2.start();
            osc1.stop(audioCtx.currentTime + 0.2);
            osc2.stop(audioCtx.currentTime + 0.2);
        } catch (e) {
            console.warn("AudioContext error:", e);
        }
    }

    // =========================================================================
    // 2. Google TTS (Text-to-Speech) Audio Engine
    // =========================================================================
    function playGoogleTTS(text, lang = "ENG", onEndCallback = null) {
        if (!isTtsEnabled || !text) {
            if (onEndCallback) onEndCallback();
            return;
        }

        // Clean text of markdown, badges, and technical tags
        const cleanSpeech = text
            .replace(/[*#`_>]/g, "")
            .replace(/\[K2U_.*?\.au\]/gi, "")
            .replace(/\[.*?\]/g, "")
            .replace(/\$\d+(\.\d+)?/g, (m) => m.replace("$", "") + " dollars")
            .replace(/\n+/g, " ")
            .trim();

        if (!cleanSpeech) {
            if (onEndCallback) onEndCallback();
            return;
        }

        const langCode = (lang === "SPA" || cleanSpeech.toLowerCase().includes("español") || cleanSpeech.toLowerCase().includes("bienvenid")) ? "es" : "en";

        // Activate voice visualizer
        if (voiceWaveform) {
            voiceWaveform.classList.remove("idle", "recording");
            voiceWaveform.classList.add("speaking");
        }
        if (voiceStatusLabel) {
            voiceStatusLabel.textContent = `Google TTS: Speaking (${langCode === "es" ? "Español" : "English"})...`;
        }

        const cleanup = () => {
            if (voiceWaveform) {
                voiceWaveform.classList.remove("speaking");
                voiceWaveform.classList.add("idle");
            }
            if (voiceStatusLabel) {
                voiceStatusLabel.textContent = isVoiceCallActive ? "Voice Call Active • Listening..." : "Voice Concierge Active";
            }
            if (onEndCallback) onEndCallback();
        };

        // Attempt 1: Direct Google Translate Neural Audio Stream
        try {
            if (activeAudio) {
                activeAudio.pause();
                activeAudio = null;
            }
            const encoded = encodeURIComponent(cleanSpeech.slice(0, 200));
            const ttsUrl = `https://translate.google.com/translate_tts?ie=UTF-8&tl=${langCode}&client=tw-ob&q=${encoded}`;
            const audio = new Audio(ttsUrl);
            activeAudio = audio;

            audio.onended = () => cleanup();
            audio.onerror = () => {
                // Fallback to browser Google Neural voice
                playBrowserGoogleVoice(cleanSpeech, langCode, cleanup);
            };

            const playPromise = audio.play();
            if (playPromise !== undefined) {
                playPromise.catch(() => {
                    playBrowserGoogleVoice(cleanSpeech, langCode, cleanup);
                });
            }
        } catch (e) {
            playBrowserGoogleVoice(cleanSpeech, langCode, cleanup);
        }
    }

    function playBrowserGoogleVoice(text, langCode, onEnd) {
        if (!window.speechSynthesis) {
            if (onEnd) onEnd();
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.02;
        utterance.lang = langCode === "es" ? "es-US" : "en-US";

        // Try selecting Google Neural Voice
        const voices = window.speechSynthesis.getVoices();
        const googleVoice = voices.find(v => v.name.includes("Google") && (v.lang.startsWith(langCode) || v.lang.includes(langCode)));
        if (googleVoice) {
            utterance.voice = googleVoice;
        }

        utterance.onend = () => {
            if (onEnd) onEnd();
        };
        utterance.onerror = () => {
            if (onEnd) onEnd();
        };

        window.speechSynthesis.speak(utterance);
    }

    // =========================================================================
    // 3. Speech Recognition (STT) Setup
    // =========================================================================
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            isRecording = true;
            micBtn.classList.add("recording");
            if (voiceWaveform) {
                voiceWaveform.classList.remove("idle", "speaking");
                voiceWaveform.classList.add("recording");
            }
            if (voiceStatusLabel) voiceStatusLabel.textContent = "Listening to caller...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            handleSendMessage();
        };

        recognition.onerror = () => {
            isRecording = false;
            micBtn.classList.remove("recording");
            if (voiceWaveform) {
                voiceWaveform.classList.remove("recording");
                voiceWaveform.classList.add("idle");
            }
            if (voiceStatusLabel) voiceStatusLabel.textContent = isVoiceCallActive ? "Voice Call Active" : "Voice Concierge Active";
        };

        recognition.onend = () => {
            isRecording = false;
            micBtn.classList.remove("recording");
            if (voiceWaveform) {
                voiceWaveform.classList.remove("recording");
                voiceWaveform.classList.add("idle");
            }
            if (voiceStatusLabel) voiceStatusLabel.textContent = isVoiceCallActive ? "Voice Call Active" : "Voice Concierge Active";
        };
    } else {
        micBtn.style.display = "none";
    }

    function listenForSpeech() {
        if (!recognition || isRecording) return;
        try {
            recognition.start();
        } catch (e) {
            console.warn("Recognition start ignored:", e);
        }
    }

    // =========================================================================
    // 4. Inbound Voice Call Flow (Interactive Verification & Preference Logic)
    // =========================================================================
    async function startVoiceCall() {
        isVoiceCallActive = true;
        voiceCallBtn.className = "call-action-btn active-call";
        voiceCallBtn.innerHTML = '<i class="fa-solid fa-phone-slash"></i> <span>End Voice Call</span>';
        voiceCallBanner.classList.remove("hidden");
        callStateBadge.textContent = "STEP 1: CALLER IDENTIFICATION";
        callBannerText.textContent = "Inbound Voice Call • State First & Last Name";

        messageStream.innerHTML = "";
        try {
            let data;
            try {
                const res = await fetch("/api/voice/start", { method: "POST" });
                if (!res.ok) throw new Error("API offline");
                data = await res.json();
            } catch (err) {
                data = window.ClientAgentEngine.voiceAuth.startCall();
            }

            renderAgentResponse(data, () => {
                // When agent finishes asking for name, automatically start listening!
                if (isVoiceCallActive) {
                    setTimeout(listenForSpeech, 400);
                }
            });
        } catch (e) {
            console.error("Failed to start voice call:", e);
        }
    }

    async function endVoiceCall() {
        isVoiceCallActive = false;
        voiceCallBtn.className = "call-action-btn start-call";
        voiceCallBtn.innerHTML = '<i class="fa-solid fa-phone"></i> <span>Start Voice Call (Google TTS)</span>';
        voiceCallBanner.classList.add("hidden");

        if (activeAudio) {
            activeAudio.pause();
            activeAudio = null;
        }
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (recognition && isRecording) recognition.stop();

        try {
            try {
                await fetch("/api/voice/turn", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: "hang up"})
                });
            } catch (e) {
                window.ClientAgentEngine.voiceAuth.processTurn("hang up");
            }
        } catch (e) {}

        const byeBubble = document.createElement("div");
        byeBubble.className = "message-bubble agent";
        byeBubble.innerHTML = `<div class="bubble-meta"><span><i class="fa-solid fa-phone-slash"></i> Call Gateway</span></div><div>📞 **Voice call ended.** Thank you for calling KeyBank Key Privilege.</div>`;
        messageStream.appendChild(byeBubble);
        messageStream.scrollTop = messageStream.scrollHeight;
    }

    async function resetLanguagePreference() {
        try {
            try {
                await fetch("/api/voice/reset-prefs", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({customer_ipi: activeCustomerIpi})
                });
            } catch (e) {
                window.ClientAgentEngine.voiceAuth.clearStoredPreference(activeCustomerIpi);
            }

            const alertBubble = document.createElement("div");
            alertBubble.className = "message-bubble agent";
            alertBubble.innerHTML = `<div class="bubble-meta"><span style="color: #f5c518;"><i class="fa-solid fa-rotate-left"></i> Preference Cleared</span></div><div>🔄 **Language preference reset for Customer IPI \`${activeCustomerIpi}\`.**<br>Next voice call will prompt for language selection as a new caller!</div>`;
            messageStream.appendChild(alertBubble);
            messageStream.scrollTop = messageStream.scrollHeight;
            playGoogleTTS("Language preference has been cleared. The next voice call will prompt for language selection.", "ENG");
        } catch (e) {
            console.error("Reset pref error:", e);
        }
    }

    function updateCallBannerState(data) {
        if (!isVoiceCallActive) return;

        const subId = data.subagent_id || "";
        const step = (data.structured_data && data.structured_data.step) || "";

        if (subId === "root_agent" || data.subagent_title.includes("Supervisor") || subId === "balance_inquiry" || subId === "cc_statement") {
            callStateBadge.textContent = "CONNECTED: KEY PRIVILEGE CONCIERGE";
            callBannerText.textContent = "Authenticated VIP Session • Multi-Agent Concierge Active";
            return;
        }

        if (step === "COLLECT_PHONE" || data.message.includes("10-digit telephone")) {
            callStateBadge.textContent = "STEP 2: TELEPHONE VERIFICATION";
            callBannerText.textContent = "Providing 10-Digit Registered Phone Number";
        } else if (step === "COLLECT_SSN" || data.message.includes("Social Security Number")) {
            callStateBadge.textContent = "STEP 3: SSN VERIFICATION";
            callBannerText.textContent = "Identity Verification • Last 4 Digits of SSN";
        } else if (step === "COLLECT_LANGUAGE_NEW" || data.message.includes("select your preferred language")) {
            callStateBadge.textContent = "STEP 4: NEW LANGUAGE SELECTION";
            callBannerText.textContent = "Selecting Preferred Language (Saved for Future Calls)";
        } else if (step === "CONFIRM_LANGUAGE_RETURNING" || data.message.includes("preferred language today")) {
            callStateBadge.textContent = "STEP 4: RETURNING CALLER CONFIRMATION";
            callBannerText.textContent = "Confirming Stored Language Preference";
        }
    }

    // =========================================================================
    // 5. Customer Profile & UI Rendering
    // =========================================================================
    function formatMarkdown(text) {
        if (!text) return "";
        return text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/`(.*?)`/g, "<code>$1</code>")
            .replace(/^> (.*$)/gim, "<blockquote>$1</blockquote>")
            .replace(/\n\n/g, "<br><br>")
            .replace(/\n/g, "<br>");
    }

    async function loadCustomers() {
        try {
            const res = await fetch("/api/customers");
            if (!res.ok) throw new Error("API not available");
            const data = await res.json();
            customerSelect.innerHTML = "";

            data.customers.forEach(c => {
                const opt = document.createElement("option");
                opt.value = c.ipi;
                const feeText = c.fee_waived ? "Waived ($0)" : "At Risk ($25 Fee)";
                opt.textContent = `${c.name} (${c.tier} - Group ${c.group} | ${feeText})`;
                if (c.ipi === data.active_ipi) opt.selected = true;
                customerSelect.appendChild(opt);
            });

            activeCustomerIpi = data.active_ipi;
            await initSession(activeCustomerIpi);
        } catch (e) {
            console.log("Using ClientAgentEngine for static hosting:", e);
            const customers = window.ClientAgentEngine.getCustomers();
            customerSelect.innerHTML = "";
            customers.forEach((c, idx) => {
                const opt = document.createElement("option");
                opt.value = c.ipi;
                opt.textContent = `${c.name} (${c.tier} - Group ${c.relationship_group})`;
                if (idx === 0) opt.selected = true;
                customerSelect.appendChild(opt);
            });
            activeCustomerIpi = customers[0].ipi;
            await initSession(activeCustomerIpi);
        }
    }

    async function updateProfileUI() {
        try {
            let p;
            try {
                const res = await fetch("/api/profile");
                if (!res.ok) throw new Error("API offline");
                p = await res.json();
            } catch (err) {
                p = window.ClientAgentEngine.getActiveProfile();
            }

            profName.textContent = p.name;
            profIpi.textContent = p.ipi;
            profPhone.textContent = p.phone;
            profGroup.textContent = `Group ${p.relationship_group} (${p.tier === "PRIVATE_CLIENT" ? "Private Wealth" : "Primacy Eligible"})`;
            profKeyAtWork.textContent = p.is_key_at_work ? "YES" : "NO";
            tierBadge.textContent = p.tier;
            currentLangLabel.textContent = p.language;

            // Update Fee Avoidance Card
            const fs = p.fee_status;
            if (fs.is_waived) {
                feeWaiverBadge.textContent = "WAIVED ($0.00)";
                feeWaiverBadge.className = "status-pill waived";
                remedyBox.style.display = "none";
            } else {
                feeWaiverBadge.textContent = "AT RISK ($25 FEE)";
                feeWaiverBadge.className = "status-pill at-risk";
                remedyBox.style.display = "block";
                daysRemainingText.textContent = `${fs.days_remaining} Days Remaining in Statement Cycle`;
                remedyText.textContent = fs.remedy.replace(/•/g, "").trim();
            }

            // Rule 1
            rule1Current.textContent = `$${fs.rule1_balance.toLocaleString("en-US", {minimumFractionDigits: 2})}`;
            const r1Pct = Math.min(100, Math.round((fs.rule1_balance / 25000.0) * 100));
            rule1Progress.style.width = `${r1Pct}%`;
            rule1Progress.className = `meter-fill ${fs.rule1_met ? "pass" : (r1Pct > 70 ? "warning" : "fail")}`;
            rule1Icon.innerHTML = fs.rule1_met ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-circle-xmark"></i>';
            rule1Icon.className = `check-icon ${fs.rule1_met ? "pass" : "fail"}`;

            // Rule 2
            rule2Current.textContent = `$${fs.rule2_mortgage_autopay.toLocaleString("en-US", {minimumFractionDigits: 2})} / mo`;
            const r2Pct = fs.rule2_met ? 100 : (fs.rule2_mortgage_autopay > 0 ? 50 : 0);
            rule2Progress.style.width = `${r2Pct}%`;
            rule2Progress.className = `meter-fill ${fs.rule2_met ? "pass" : "fail"}`;
            rule2Icon.innerHTML = fs.rule2_met ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-circle-xmark"></i>';
            rule2Icon.className = `check-icon ${fs.rule2_met ? "pass" : "fail"}`;

            // Rule 3
            rule3Current.textContent = `$${fs.rule3_direct_deposits.toLocaleString("en-US", {minimumFractionDigits: 2})}`;
            const r3Pct = Math.min(100, Math.round((fs.rule3_direct_deposits / 2500.0) * 100));
            rule3Progress.style.width = `${r3Pct}%`;
            rule3Progress.className = `meter-fill ${fs.rule3_met ? "pass" : (r3Pct > 40 ? "warning" : "fail")}`;
            rule3Icon.innerHTML = fs.rule3_met ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-circle-xmark"></i>';
            rule3Icon.className = `check-icon ${fs.rule3_met ? "pass" : "fail"}`;
        } catch (e) {
            console.error("Failed to update profile UI:", e);
        }
    }

    async function initSession(ipi) {
        if (isVoiceCallActive) return;
        messageStream.innerHTML = "";
        try {
            let data;
            try {
                const res = await fetch("/api/session/init", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({customer_ipi: ipi})
                });
                if (!res.ok) throw new Error("API offline");
                data = await res.json();
            } catch (err) {
                window.ClientAgentEngine.setActiveIpi(ipi);
                data = window.ClientAgentEngine.initializeSession(ipi);
            }
            renderAgentResponse(data);
            await updateProfileUI();
        } catch (e) {
            console.error("Init session error:", e);
        }
    }

    function renderAgentResponse(data, onSpeechEndCallback = null) {
        agentTitle.textContent = data.subagent_title || "Key Privilege Root Supervisor";
        inspectSubagent.textContent = data.subagent_id;
        inspectPrompt.textContent = data.audio_prompt_code || "[K2U_ENG.700.au]";

        // Proactive Fee Banner
        if (data.fee_reminder_banner) {
            proactiveAlertBanner.classList.remove("hidden");
            proactiveAlertContent.textContent = data.fee_reminder_banner;
        } else {
            proactiveAlertBanner.classList.add("hidden");
        }

        // Telephony / Routing Context
        if (data.routing_context) {
            activeTrcBadge.textContent = data.routing_context.transfer_route_code;
            inspectQueue.textContent = data.routing_context.target_queue;
            inspectBotId.textContent = data.routing_context.master_bot_id;
            inspectKvps.textContent = JSON.stringify(data.routing_context.genesys_attached_data, null, 2);
        } else {
            inspectKvps.textContent = JSON.stringify(data.structured_data || {}, null, 2);
        }

        // Message Bubble
        const bubble = document.createElement("div");
        bubble.className = "message-bubble agent";

        const meta = document.createElement("div");
        meta.className = "bubble-meta";
        meta.innerHTML = `<span><i class="fa-solid fa-headset"></i> ${data.subagent_title}</span> <span class="prompt-tag">${data.audio_prompt_code || ""}</span>`;
        bubble.appendChild(meta);

        const content = document.createElement("div");
        content.innerHTML = formatMarkdown(data.message);
        bubble.appendChild(content);

        // Speech Replay Button
        const actions = document.createElement("div");
        actions.className = "bubble-actions";
        const ttsBtn = document.createElement("button");
        ttsBtn.className = "btn-bubble-speech";
        ttsBtn.innerHTML = '<i class="fa-brands fa-google"></i> Google TTS Replay';
        ttsBtn.onclick = () => playGoogleTTS(data.speech_message || data.message, currentLangLabel.textContent);
        actions.appendChild(ttsBtn);
        bubble.appendChild(actions);

        messageStream.appendChild(bubble);
        messageStream.scrollTop = messageStream.scrollHeight;

        // Update Voice Call Banner state
        updateCallBannerState(data);

        // Auto Speak with Google TTS
        playGoogleTTS(data.speech_message || data.message, currentLangLabel.textContent, onSpeechEndCallback);

        // Quick Reply Suggestions
        quickRepliesBar.innerHTML = "";
        if (data.suggested_quick_replies && data.suggested_quick_replies.length > 0) {
            data.suggested_quick_replies.forEach(reply => {
                const chip = document.createElement("button");
                chip.className = "chip-btn";
                chip.textContent = reply;
                chip.onclick = () => {
                    userInput.value = reply;
                    handleSendMessage();
                };
                quickRepliesBar.appendChild(chip);
            });
        }
    }

    // =========================================================================
    // 6. Conversational Message Handling (Voice Call vs Chat)
    // =========================================================================
    async function handleSendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // Render User Bubble
        const userBubble = document.createElement("div");
        userBubble.className = "message-bubble user";
        userBubble.textContent = text;
        messageStream.appendChild(userBubble);
        messageStream.scrollTop = messageStream.scrollHeight;

        userInput.value = "";

        // If in Interactive Voice Call Mode -> route to Voice Auth & Gateway
        if (isVoiceCallActive) {
            try {
                let data;
                try {
                    const res = await fetch("/api/voice/turn", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({message: text})
                    });
                    if (!res.ok) throw new Error("API offline");
                    data = await res.json();
                } catch (err) {
                    data = window.ClientAgentEngine.voiceAuth.processTurn(text);
                }

                renderAgentResponse(data, () => {
                    // Continuous hands-free call: auto-listen after agent finishes speaking
                    if (isVoiceCallActive) {
                        setTimeout(listenForSpeech, 400);
                    }
                });
                await updateProfileUI();
            } catch (e) {
                console.error("Voice turn error:", e);
            }
            return;
        }

        // Standard Chat Mode
        try {
            let data;
            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: text})
                });
                if (!res.ok) throw new Error("API offline");
                data = await res.json();
            } catch (err) {
                data = window.ClientAgentEngine.routeAndExecute(text);
            }
            renderAgentResponse(data);
            await updateProfileUI();
        } catch (e) {
            console.error("Chat error:", e);
        }
    }

    // =========================================================================
    // 7. Event Listeners
    // =========================================================================
    sendBtn.addEventListener("click", handleSendMessage);
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleSendMessage();
    });

    voiceCallBtn.addEventListener("click", () => {
        if (isVoiceCallActive) {
            endVoiceCall();
        } else {
            startVoiceCall();
        }
    });

    endCallBtn.addEventListener("click", endVoiceCall);
    resetPrefBtn.addEventListener("click", resetLanguagePreference);

    customerSelect.addEventListener("change", async (e) => {
        activeCustomerIpi = e.target.value;
        if (isVoiceCallActive) {
            endVoiceCall();
        }
        await initSession(activeCustomerIpi);
    });

    langToggleBtn.addEventListener("click", async () => {
        const newLang = currentLangLabel.textContent === "ENG" ? "SPA" : "ENG";
        try {
            const res = await fetch("/api/switch-language", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({language: newLang})
            });
            const data = await res.json();
            renderAgentResponse(data);
            await updateProfileUI();
        } catch (e) {
            console.error("Lang switch error:", e);
        }
    });

    speechToggleBtn.addEventListener("click", () => {
        isTtsEnabled = !isTtsEnabled;
        if (isTtsEnabled) {
            ttsIcon.className = "fa-solid fa-volume-high";
            speechToggleBtn.title = "Google TTS: Enabled";
        } else {
            ttsIcon.className = "fa-solid fa-volume-xmark";
            speechToggleBtn.title = "Google TTS: Muted";
            if (activeAudio) activeAudio.pause();
            if (window.speechSynthesis) window.speechSynthesis.cancel();
        }
    });

    micBtn.addEventListener("click", () => {
        if (!recognition) return;
        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    // DTMF Keypad Controls
    toggleDtmfBtn.addEventListener("click", () => {
        dtmfPanel.classList.toggle("collapsed");
    });
    closeDtmfBtn.addEventListener("click", () => {
        dtmfPanel.classList.add("collapsed");
    });

    document.querySelectorAll(".key-btn, .dtmf-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const key = btn.getAttribute("data-key");
            playDtmfTone(key);
            dtmfDisplay.textContent = `DTMF Key [${key}] Pressed`;
            userInput.value = key;
            handleSendMessage();
        });
    });

    // Initial Load
    loadCustomers();
});
