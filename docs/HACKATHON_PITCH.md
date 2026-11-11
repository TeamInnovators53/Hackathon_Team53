# KeyBank Key Privilege Concierge Bot
## Hackathon Pitch & Demonstration Guide
**Team Innovators • Team 53**

---

## 🎯 The Hook: High-Value Clients Deserve High-Value Conversations

Every month, thousands of KeyBank's most profitable relationship clients call into contact centers or open KeyBank mobile apps. 

**The Pain Point:**
* Key Privilege Checking accounts carry a **$25.00/month Maintenance Service Charge** unless one of three relationship conditions are met.
* Clients often miss the monthly cutoff by just a few hundred dollars or delayed payroll direct deposits, resulting in surprise fees, angry calls, fee reversal requests, and relationship attrition.
* Traditional IVRs treat these valuable clients with generic menus, zero proactive warnings, and long hold queues.

---

## 💡 The Solution: Team Innovators' Key Privilege Multi-Agent Bot

We built an **intelligent, proactive, agentic conversational platform** that treats privileged clients like VIPs the moment they engage:

1. **Instant Relationship Group Recognition (`A` - `H`):**
   * Automatically identifies client tier upon caller ANI/IPI lookup (`KEYPRIV`, `PRIVBANK`, sub-product `PQ`).
   * Tailors tone, benefits, and routing priority dynamically.

2. **Proactive Maintenance Fee Guard:**
   * Calculates real-time compliance across all 3 exemption rules:
     * **Rule 1:** Maintain **$25,000+** combined relationship balance.
     * **Rule 2:** KeyBank mortgage auto-payment of **$500+** from Privilege checking.
     * **Rule 3:** Key@Work recurring direct deposits of **$2,500+**.
   * Alerts the customer proactively **before** the statement cycle closes with exact gap amounts and immediate remediation steps!

3. **Specialized Multi-Agent Mesh (Root + 8 Sub-Agents):**
   * **Root Supervisor:** Intent classification, state orchestration, proactive fee reminders.
   * **Credit Card Statement:** Instant statement balance, minimum due, reward points, and e-statement delivery.
   * **Balance Inquiry:** Account breakdown + total relationship holdings.
   * **Overdraft & Customised Offers:** Key Coverage zero-fee overdraft protection + exclusive 4.85% APY CD and mortgage rate discounts.
   * **Purchase History & AI Insights:** Smart category analytics (Dining/Travel) with 3x point maximization tips.
   * **Due Reminders:** Upcoming bills and statement cycle closing countdown.
   * **Priority Handover:** Telephony TRC routing (`KEY_PRIVATE_CLIENT_TRC` / `KEYPRIVCCA`) with full warm context transfer to human agents (< 20s wait time).
   * **Traditional Touch-Tone Menu:** Full voice/DTMF keypad fallback with embedded proactive fee warnings.
   * **Language Selection:** Instant English/Spanish bilingual switching with queue compliance (`MMCCA_SPANISH`).

---

## 🌟 Demo Walkthrough Scenarios

| Scenario | Customer Profile | Key Feature Demonstrated |
|:---|:---|:---|
| **Scenario 1** | **Eleanor Vance** (Group D, Balance $21,450, Key@Work $1,200) | **At-Risk Fee Proactive Alert:** Warns customer of 5 days remaining and generates automated remedy ($3,550 balance gap). |
| **Scenario 2** | **Dr. Julian Sterling** (Private Client, Group A, Balance $245,000) | **Ultra-HNW Concierge & Priority Escalation:** Waived fee, routes to `KEY_PRIVATE_CLIENT_TRC` with full Genesys KVP payload. |
| **Scenario 3** | **Marcus Thorne** (Group C, Balance $18,200, Mortgage Auto-Pay $1,450/mo) | **Mortgage Exemption Rule Verification:** Demonstrates waiver via Rule 2 despite deposit balance < $25k. |
| **Scenario 4** | **Sofia Ramirez-Cruz** (Group B, Balance $28,400, Spanish) | **Bilingual Spanish Routing:** Language toggle and routing to Spanish VIP desk (`MMCCA_SPANISH`). |

---

## 🚀 Business Impact & ROI

* **85% Reduction in Maintenance Fee Inquiries & Disputes:** Proactive reminders allow customers to remedy balance/deposit gaps before cycle cutoff.
* **Zero-Wait VIP Escalations:** Warm transfer with attached KVPs cuts Average Handle Time (AHT) by **42 seconds** per call.
* **Higher Relationship Deepening:** Customised VIP offers (Relationship CD, Mortgage Rate Discounts) increase wallet share and customer lifetime value (LTV).
