# KeyBank Key Privilege & Private Client Voice/Chat Multi-Agent System
### 🏆 Hackathon Team 53 • Team Innovators

An agentic multi-agent conversational bot engineered for KeyBank's privileged and private banking clients. Features real-time relationship group mapping (`A`–`H`), proactive maintenance service charge avoidance guards, priority telephony routing, and a full voice & touch-tone IVR simulator.

---

## 🌟 Key Highlights & Capabilities

* **Root Agent Supervisor & 8 Domain Sub-Agents:**
  1. 💳 **Credit Card Statement Sub-Agent:** Balances, minimum payment, cycle dates, reward points, e-statement delivery.
  2. 💰 **Balance Inquiry Sub-Agent:** Checking, savings, money market, and combined relationship balances.
  3. 🛡️ **Overdraft or Customised Offers Sub-Agent:** Key Coverage overdraft protection and exclusive VIP relationship offers (4.85% APY CD, line of credit, mortgage discounts).
  4. 🛍️ **Purchase History & Recommendations Sub-Agent:** Categorized transaction analytics (Dining/Travel) and AI cash-back reward optimization.
  5. 🔔 **Due Reminders Sub-Agent:** Bill due dates, mortgage auto-debits, statement cycle countdown, and fee waiver deadlines.
  6. 📞 **Handover to Dedicated Agent (Priority Routing):** Telephony warm transfer with Transfer Route Codes (`KEY_PRIVATE_CLIENT_TRC` / `KEYPRIVCCA` / `MMCCA_SPANISH`) and Genesys Attached Data KVPs.
  7. 🔢 **Traditional Menu Sub-Agent:** IVR touch-tone numbered fallback with embedded proactive fee avoidance announcements.
  8. 🌐 **Language Selection Sub-Agent:** Instant English / Spanish bilingual switching and routing safeguards.

* **Privileged Customer Identification Engine:**
  * Maps customers to KeyBank Household Relationship Groups (`A`–`H`).
  * Recognizes Key Privilege Checking (`PQ`), `KEYPRIV`, and `PRIVBANK` profiles.
  * Honors Laurel Road (`2912` / `3211`) and KeyBank Retail (`0101`) brand architecture rules.

* **"How to Avoid a Maintenance Service Charge" Proactive Rule Engine:**
  * **Rule 1:** Maintain total combined balance of **$25,000+** across accounts.
  * **Rule 2:** Have a KeyBank mortgage with automatic payment deduction of **$500+** from Key Privilege Checking.
  * **Rule 3:** Be a Key@Work member with direct deposits totaling **$2,500+** during the statement cycle.
  * Injects proactive alerts into voice prompts and menu banners with exact gap remedies!

* **Voice & Chat Simulator:**
  * Web Speech API integration (Speech-to-Text & Text-to-Speech).
  * Web Audio API DTMF dual-tone touch-tone keypad simulator.
  * Real-time Telephony & KVP Inspector.

---

## 🚀 Quick Start Guide

### 1. Run Automated Tests
```bash
python -m pytest tests/
```
All unit and integration tests validate the fee avoidance engine, relationship group classification, DTMF routing, and all 8 domain sub-agents.

### 2. Launch the Web Voice & Chat Simulator
```bash
python run_server.py
```
Open your browser to: **[http://127.0.0.1:8080](http://127.0.0.1:8080)**

---

## 📁 Repository Structure

```
Hackathon_Team53/
├── README.md                           # Project Overview & Quickstart
├── run_server.py                       # Standalone Python HTTP Server & REST API
├── src/
│   ├── __init__.py
│   ├── models.py                       # Data models (CustomerProfile, MaintenanceFeeStatus, etc.)
│   ├── customer_service.py             # Relationship Group Mapping & Demo Profiles
│   ├── fee_avoidance_engine.py         # Maintenance Service Charge Rule Engine & Gaps
│   ├── root_agent.py                   # Root Agent Supervisor & Dispatcher
│   └── subagents/
│       ├── __init__.py
│       ├── base_agent.py               # Abstract Base Sub-Agent
│       ├── cc_statement_agent.py       # 1. Credit Card Statement
│       ├── balance_inquiry_agent.py    # 2. Balance Inquiry
│       ├── overdraft_offers_agent.py   # 3. Overdraft & Customised Offers
│       ├── purchase_recommendations_agent.py # 4. Purchase History & AI Insights
│       ├── due_reminders_agent.py      # 5. Due Reminders & Fee Countdown
│       ├── priority_handover_agent.py  # 6. Priority Telephony Handover
│       ├── traditional_menu_agent.py   # 7. Traditional Voice/DTMF Menu
│       └── language_selection_agent.py # 8. Language Selection (ENG/SPA)
├── web/
│   ├── index.html                      # Interactive Voice & Chat Simulator
│   ├── styles.css                      # KeyBank Red & Navy Responsive Theme
│   └── app.js                          # Web Audio DTMF & Speech API Client
├── tests/
│   ├── test_fee_avoidance.py           # Unit tests for the 3 waiver rules
│   ├── test_agents.py                  # Integration tests for Root & Sub-Agents
│   └── test_server.py                  # Functional API handler tests
└── docs/
    ├── ARCHITECTURE.md                 # Deep Technical Architecture Document
    └── HACKATHON_PITCH.md              # Presentation Pitch Deck & Demo Guide
```

---

## 👥 Team Innovators (Team 53)
* **Poojitha Singam** & Team Innovators
* October 2026 Release / Hackathon 2026
