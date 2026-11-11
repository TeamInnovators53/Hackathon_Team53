/**
 * Client-Side Key Privilege Multi-Agent & Fee Avoidance Engine
 * Enables 100% serverless operation on Firebase Hosting, GCP Cloud Storage, or GitHub Pages.
 * Hackathon Team 53 - Team Innovators.
 */

window.ClientAgentEngine = (() => {
    // 1. Sample Customers
    const customers = {
        "031379551": {
            ipi: "031379551",
            name: "Eleanor Vance",
            phone: "(385) 456-9511",
            ssn_last4: "3584",
            tier: "PRIVILEGED",
            relationship_group: "D",
            language: "ENG",
            is_key_at_work: true,
            accounts: [
                {
                    account_number: "4042250101",
                    account_name: "Key Privilege Checking",
                    prod_code: "DDA",
                    current_balance: 14250.00,
                    available_balance: 14200.00,
                    details: {
                        cycle_start: "2026-10-21",
                        cycle_end: "2026-11-20",
                        days_remaining: 5,
                        mortgage_autopay_enabled: false,
                        mortgage_autopay_amount: 0.0,
                        cycle_direct_deposits: 1200.00,
                        overdraft_protection: true
                    }
                },
                {
                    account_number: "4042257702",
                    account_name: "Relationship High-Yield Savings",
                    prod_code: "SAV",
                    current_balance: 7200.00,
                    available_balance: 7200.00
                },
                {
                    account_number: "5229063980757605",
                    account_name: "KeyBank Latitude Privilege Card",
                    prod_code: "CCA",
                    current_balance: -1840.50,
                    available_balance: 13159.50,
                    details: {
                        credit_limit: 15000.00,
                        statement_balance: 1840.50,
                        minimum_payment_due: 45.00,
                        payment_due_date: "2026-11-28",
                        reward_points: 24850,
                        cashback_available: 248.50
                    }
                }
            ],
            recent_transactions: [
                { date: "2026-11-08", description: "Whole Foods Market", amount: 142.80, category: "Groceries", points: 285 },
                { date: "2026-11-06", description: "Four Seasons Hotel Dining", amount: 385.00, category: "Dining", points: 1155 },
                { date: "2026-11-04", description: "Nordstrom Westlake", amount: 210.45, category: "Luxury Retail", points: 420 },
                { date: "2026-11-09", description: "Delta Air Lines First Class Upgrade", amount: 620.00, category: "Travel", points: 1860 }
            ]
        },
        "004645906": {
            ipi: "004645906",
            name: "Dr. Julian Sterling",
            phone: "(330) 714-8766",
            ssn_last4: "8210",
            tier: "PRIVATE_CLIENT",
            relationship_group: "A",
            language: "ENG",
            is_key_at_work: false,
            accounts: [
                {
                    account_number: "404225056",
                    account_name: "Key Private Client Checking",
                    prod_code: "DDA",
                    current_balance: 45200.00,
                    available_balance: 45200.00,
                    details: {
                        cycle_start: "2026-11-01",
                        cycle_end: "2026-11-30",
                        days_remaining: 19,
                        mortgage_autopay_enabled: false,
                        cycle_direct_deposits: 0.0,
                        dedicated_advisor: "Victoria Reynolds, CFP® (Chagrin Falls Wealth Center)"
                    }
                },
                {
                    account_number: "4042259910",
                    account_name: "Key Private Tier Money Market",
                    prod_code: "MMA",
                    current_balance: 125000.00,
                    available_balance: 125000.00
                },
                {
                    account_number: "5144746867062196",
                    account_name: "KeyBank World Elite Mastercard",
                    prod_code: "CCA",
                    current_balance: -3420.00,
                    available_balance: 46580.00,
                    details: {
                        credit_limit: 50000.00,
                        statement_balance: 3420.00,
                        minimum_payment_due: 75.00,
                        payment_due_date: "2026-12-02",
                        reward_points: 182400,
                        cashback_available: 1824.00
                    }
                }
            ],
            recent_transactions: [
                { date: "2026-11-07", description: "Ritz-Carlton Club & Spa", amount: 1250.00, category: "Luxury Travel", points: 3750 },
                { date: "2026-11-05", description: "Sotheby's Auction Gallery", amount: 4200.00, category: "Art & Collectibles", points: 8400 }
            ]
        },
        "019284752": {
            ipi: "019284752",
            name: "Marcus Thorne",
            phone: "(216) 555-1234",
            ssn_last4: "4491",
            tier: "PRIVILEGED",
            relationship_group: "C",
            language: "ENG",
            is_key_at_work: false,
            accounts: [
                {
                    account_number: "4042251188",
                    account_name: "Key Privilege Checking",
                    prod_code: "DDA",
                    current_balance: 18200.00,
                    available_balance: 18200.00,
                    details: {
                        cycle_start: "2026-10-16",
                        cycle_end: "2026-11-15",
                        days_remaining: 4,
                        mortgage_autopay_enabled: true,
                        mortgage_autopay_amount: 1450.00,
                        cycle_direct_deposits: 0.0
                    }
                }
            ],
            recent_transactions: []
        },
        "048291043": {
            ipi: "048291043",
            name: "Sofia Ramirez-Cruz",
            phone: "(305) 555-7890",
            ssn_last4: "6120",
            tier: "PRIVILEGED",
            relationship_group: "B",
            language: "SPA",
            is_key_at_work: true,
            accounts: [
                {
                    account_number: "4042253399",
                    account_name: "Key Privilege Checking (Español)",
                    prod_code: "DDA",
                    current_balance: 28400.00,
                    available_balance: 28400.00,
                    details: {
                        cycle_start: "2026-10-23",
                        cycle_end: "2026-11-22",
                        days_remaining: 11,
                        mortgage_autopay_enabled: false,
                        cycle_direct_deposits: 3200.00
                    }
                }
            ],
            recent_transactions: []
        }
    };

    let activeIpi = "031379551";

    // 2. Evaluate Fee Avoidance Status
    function evaluateFeeStatus(customer) {
        const depositTypes = ["DDA", "SAV", "MMA", "INV"];
        const totalBal = customer.accounts
            .filter(a => depositTypes.includes(a.prod_code))
            .reduce((sum, a) => sum + (a.current_balance > 0 ? a.current_balance : 0), 0);

        const rule1_met = totalBal >= 25000.00;

        const chk = customer.accounts.find(a => a.prod_code === "DDA");
        const details = chk ? chk.details : {};
        const mortgageAutopay = details.mortgage_autopay_enabled ? (details.mortgage_autopay_amount || 0) : 0;
        const rule2_met = mortgageAutopay >= 500.00;

        const directDeposits = details.cycle_direct_deposits || 0;
        const rule3_met = customer.is_key_at_work && directDeposits >= 2500.00;

        const is_waived = rule1_met || rule2_met || rule3_met;
        let winningMethod = null;
        if (rule1_met) winningMethod = `Combined Balance ($${totalBal.toLocaleString()} >= $25,000)`;
        else if (rule2_met) winningMethod = `Mortgage Auto-Payment ($${mortgageAutopay}/mo >= $500)`;
        else if (rule3_met) winningMethod = `Key@Work Direct Deposits ($${directDeposits} >= $2,500)`;

        const daysRemaining = details.days_remaining || 5;
        const cycleEnd = details.cycle_end || "2026-11-20";

        let alertMsg = "";
        let remedy = "";

        if (!is_waived) {
            const gap = Math.max(0, 25000.00 - totalBal);
            const depGap = customer.is_key_at_work ? Math.max(0, 2500.00 - directDeposits) : null;
            alertMsg = `Action Required: Your Key Privilege Checking account is currently at risk of a $25.00 monthly maintenance service charge for the cycle ending ${cycleEnd} (${daysRemaining} days remaining).`;
            const tips = [`Transfer or deposit $${gap.toLocaleString("en-US", {minimumFractionDigits: 2})} to reach the $25,000 combined balance tier`];
            if (depGap) tips.push(`Ensure remaining direct deposits of $${depGap.toLocaleString("en-US", {minimumFractionDigits: 2})} arrive before ${cycleEnd}`);
            remedy = " • " + tips.join("\n • ");
        } else {
            alertMsg = `Your $25.00 monthly maintenance fee is waived for this cycle via ${winningMethod}.`;
        }

        return {
            monthly_charge: 25.00,
            cycle_end: cycleEnd,
            days_remaining: daysRemaining,
            is_waived: is_waived,
            winning_method: winningMethod,
            rule1_balance: totalBal,
            rule1_met: rule1_met,
            rule2_mortgage_autopay: mortgageAutopay,
            rule2_met: rule2_met,
            rule3_direct_deposits: directDeposits,
            rule3_met: rule3_met,
            alert_message: alertMsg,
            remedy: remedy
        };
    }

    // 3. Sub-Agent Processors
    function handleBalanceInquiry(c, fee) {
        const isSpa = c.language === "SPA";
        const lines = c.accounts.map(a => `• **${a.account_name}** (*${a.account_number.slice(-4)}): **$${Math.abs(a.current_balance).toLocaleString("en-US", {minimumFractionDigits: 2})}**`);
        const total = fee.rule1_balance;

        let feeNote = fee.is_waived
            ? `\n\n🛡️ **Relationship Tier Status:** Your combined balance of **$${total.toLocaleString("en-US", {minimumFractionDigits: 2})}** qualifies for **100% Waived Monthly Service Charges** (Threshold: $25,000.00).`
            : `\n\n⚠️ **Maintenance Fee Advisory:** Your combined balance is **$${total.toLocaleString("en-US", {minimumFractionDigits: 2})}** ($${(25000 - total).toLocaleString("en-US", {minimumFractionDigits: 2})} below the $25,000 fee waiver threshold). You have ${fee.days_remaining} days in your cycle to top up to avoid the $25.00 maintenance fee.`;

        const msg = isSpa
            ? `💰 **Saldos de sus Cuentas Key Privilege para ${c.name}:**\n\n${lines.join("\n")}\n\n**Saldo Total Combinado:** **$${total.toLocaleString("en-US", {minimumFractionDigits: 2})}**${feeNote}`
            : `💰 **Account Balances for ${c.name} (Tier: ${c.tier}):**\n\n${lines.join("\n")}\n\n🏛️ **Total Combined Relationship Holdings:** **$${total.toLocaleString("en-US", {minimumFractionDigits: 2})}**${feeNote}`;

        return {
            subagent_id: "balance_inquiry",
            subagent_title: "Relationship Balance Specialist",
            message: msg,
            speech_message: `Here are your balances. Your checking account balance is $${c.accounts[0].current_balance.toLocaleString()}, and your total combined relationship balance is $${total.toLocaleString()}.`,
            audio_prompt_code: isSpa ? "[K2U_SPA.701.au]" : "[K2U_ENG.701.au]",
            suggested_quick_replies: ["How to Avoid Maintenance Fee", "Credit Card Statement", "Overdraft & Offers", "Speak to Dedicated Concierge"]
        };
    }

    function handleCcStatement(c) {
        const cc = c.accounts.find(a => a.prod_code === "CCA");
        if (!cc) {
            return {
                subagent_id: "cc_statement",
                subagent_title: "Credit Card Statement Specialist",
                message: "No active credit card found under this profile.",
                speech_message: "No active credit card was found.",
                suggested_quick_replies: ["Balance Inquiry", "Check Offers", "Speak to Concierge"]
            };
        }
        const d = cc.details;
        const msg = `✅ **Credit Card Statement Summary for ${cc.account_name} (ending in ${cc.account_number.slice(-4)}):**\n\n• **Statement Balance:** **$${d.statement_balance.toLocaleString("en-US", {minimumFractionDigits: 2})}**\n• **Minimum Payment Due:** **$${d.minimum_payment_due.toLocaleString("en-US", {minimumFractionDigits: 2})}**\n• **Payment Due Date:** **${d.payment_due_date}**\n• **Available Credit:** $${cc.available_balance.toLocaleString("en-US", {minimumFractionDigits: 2})} (Limit: $${d.credit_limit.toLocaleString()})\n• **Privilege Rewards:** **${d.reward_points.toLocaleString()} points** (Cash Value: $${d.cashback_available.toFixed(2)})\n\n📬 *Your November e-Statement is ready. Paperless billing is active.*`;

        return {
            subagent_id: "cc_statement",
            subagent_title: "Credit Card Statement Specialist",
            message: msg,
            speech_message: `Your statement balance is $${d.statement_balance.toLocaleString()} with a minimum payment of $${d.minimum_payment_due} due on ${d.payment_due_date}.`,
            audio_prompt_code: "[K2U_ENG.712.au]",
            suggested_quick_replies: ["Pay Credit Card Bill", "Purchase History & Rewards", "Balance Inquiry", "Avoid Maintenance Fee"]
        };
    }

    function handleOverdraftOffers(c) {
        const msg = `🎁 **Overdraft Protection & Customised Privilege Offers for ${c.name}:**\n\n🛡️ **Overdraft Status (Key Coverage):** **Active (Backed by Savings)**\n*(As a Key Privilege client, automatic backup transfer fees are $0.00 waivable).*\n\n⭐ **Personalized VIP Offers for Relationship Tier ${c.relationship_group}:**\n\n1. 📈 **14-Month Relationship CD:** **4.85% APY** (includes +0.35% Key Privilege Bonus).\n2. 💳 **Pre-Approved Executive Line of Credit:** Up to **$35,000** at Prime + 1.99%.\n3. 🏠 **KeyBank Mortgage Rate Discount:** **0.25% discount** with auto-debit from Privilege checking.\n4. 🌟 **Key Cashback Card Upgrade:** Unlimited **2.0% Cash Back**.`;

        return {
            subagent_id: "overdraft_offers",
            subagent_title: "Overdraft & Customised Privilege Offers",
            message: msg,
            speech_message: "Your overdraft protection is active with zero transfer fees. We also have a 4.85 percent relationship CD and a pre-approved $35,000 line of credit.",
            audio_prompt_code: "[K2U_ENG.720.au]",
            suggested_quick_replies: ["Apply for 4.85% CD", "Explore Mortgage Discount", "Balance Inquiry", "Speak to Dedicated Concierge"]
        };
    }

    function handlePurchaseRecommendations(c) {
        const txns = c.recent_transactions || [];
        const lines = txns.map(t => `• **${t.date}** | ${t.description}: **$${t.amount.toFixed(2)}** (${t.category}) (+${t.points} pts)`);
        const total = txns.reduce((s, t) => s + t.amount, 0);

        const msg = `🛍️ **Recent Purchase History & AI Insights for ${c.name}:**\n\n${lines.join("\n")}\n\n📊 **Cycle Activity Summary:** **$${total.toFixed(2)}** total spending across recent transactions.\n\n💡 **Smart Spending & Reward Optimization:**\n• **Category Trend:** High activity in **Dining & Luxury Travel** (58% of spend).\n• **Cash-Back Maximizer:** By using your KeyBank Latitude card on dining, you earn **3x Rewards**, yielding an extra **$85.00/month**.\n• **Privilege Travel Perk:** Includes complimentary airport lounge access and zero foreign transaction fees.`;

        return {
            subagent_id: "purchase_recommendations",
            subagent_title: "Purchase Analytics & AI Advisor",
            message: msg,
            speech_message: `Your recent transactions total $${total.toFixed(2)}. Your top spending category is travel and dining, which earns you triple points.`,
            audio_prompt_code: "[K2U_ENG.725.au]",
            suggested_quick_replies: ["Credit Card Statement", "Balance Inquiry", "Avoid Maintenance Fee", "Speak to Dedicated Concierge"]
        };
    }

    function handleDueReminders(c, fee) {
        const cc = c.accounts.find(a => a.prod_code === "CCA");
        const ccText = cc ? `• 💳 **Credit Card Payment:** Minimum payment of **$${cc.details.minimum_payment_due.toFixed(2)}** due on **${cc.details.payment_due_date}**.` : "";
        const feeText = fee.is_waived
            ? `• ✅ **Maintenance Fee Waiver Status:** **Waived ($0.00)** for cycle ending ${fee.cycle_end} via ${fee.winning_method}.`
            : `• ⚠️ **URGENT: Maintenance Fee Avoidance Deadline:** **${fee.days_remaining} Days Remaining** (Cycle ends ${fee.cycle_end}).\n  *To avoid the $25.00 monthly service charge, do one of the following before ${fee.cycle_end}:*\n    1. Maintain **$25,000+** combined balance (Currently **$${fee.rule1_balance.toLocaleString()}**; add **$${(25000 - fee.rule1_balance).toLocaleString()}**).\n    2. Auto-deduct **$500+** mortgage payment from Key Privilege Checking.\n    3. Complete direct deposits of **$2,500+** as a Key@Work member.`;

        const msg = `🔔 **Upcoming Due Dates & Maintenance Fee Status for ${c.name}:**\n\n${ccText}\n\n${feeText}\n\n💡 *Tip: You can set automated transfer alerts or speak to your concierge to link external balances to ensure waiver compliance.*`;

        return {
            subagent_id: "due_reminders",
            subagent_title: "Due Dates & Fee Avoidance Reminders",
            message: msg,
            speech_message: `Here are your upcoming reminders. You have ${fee.days_remaining} days remaining in your statement cycle to avoid the $25 maintenance fee.`,
            audio_prompt_code: "[K2U_ENG.730.au]",
            fee_reminder_banner: fee.is_waived ? null : fee.alert_message,
            suggested_quick_replies: ["Transfer Funds to Waive Fee", "Balance Inquiry", "Credit Card Statement", "Speak to Dedicated Concierge"]
        };
    }

    function handlePriorityHandover(c, fee) {
        const isSpa = c.language === "SPA";
        const trc = isSpa ? "MMCCA_SPANISH" : (c.tier === "PRIVATE_CLIENT" ? "KEY_PRIVATE_CLIENT_TRC" : "KEYPRIVCCA");
        const queue = isSpa ? "KeyBank Spanish VIP Concierge Desk" : (c.tier === "PRIVATE_CLIENT" ? "Key Private Client Wealth Concierge Queue" : "Key Privilege Priority Relationship Queue");

        const kvps = {
            "CustomerIPI": c.ipi,
            "CustomerTier": c.tier,
            "RelationshipGroup": c.relationship_group,
            "PriorityQueue": "TRUE",
            "StopPayment": "false",
            "MaintenanceFeeAtRisk": fee.is_waived ? "NO" : "YES",
            "TotalCombinedBalance": fee.rule1_balance.toFixed(2),
            "LanguageCode": c.language,
            "TRC": trc,
            "masterBotId": "privilegeConcierge"
        };

        const msg = `📞 **Priority Handover to Dedicated Concierge Specialist:**\n\nYour request has been routed with **Tier-1 Priority** to the **${queue}**.\n\n📋 **Telephony & Routing Payload (Genesys Attached Data / TRC):**\n• **Transfer Route Code (TRC):** \`${trc}\`\n• **Household Relationship Group:** \`${c.relationship_group}\` | Tier: **${c.tier}**\n• **Estimated Queue Wait Time:** **< 20 seconds** (VIP Bypass)\n• **Warm Context Transfer:** Full session state, balances ($${fee.rule1_balance.toLocaleString()}), and fee status automatically transmitted to agent desktop.`;

        return {
            subagent_id: "priority_handover",
            subagent_title: "Dedicated Concierge Priority Handover",
            message: msg,
            speech_message: `Connecting you directly to your dedicated Key Privilege specialist with priority routing under code ${trc}.`,
            audio_prompt_code: "[K2U_ENG.750.au]",
            handover_required: true,
            routing_context: {
                transfer_route_code: trc,
                target_queue: queue,
                master_bot_id: "privilegeConcierge",
                priority_level: "TIER_1_VIP",
                genesys_attached_data: kvps
            },
            structured_data: kvps,
            suggested_quick_replies: ["Cancel Transfer & Return to Menu", "Balance Inquiry", "Credit Card Statement"]
        };
    }

    function handleTraditionalMenu(c, fee) {
        const reminder = fee.is_waived
            ? "[PRIVILEGE STATUS] Your $25.00 monthly maintenance fee is WAIVED for this cycle."
            : `[IMPORTANT PRIVILEGE REMINDER]: ${fee.days_remaining} days remaining in your statement cycle! Add $${(25000 - fee.rule1_balance).toLocaleString()} in combined balance to avoid the $25.00 service charge.`;

        const msg = `🏛️ **Key Privilege Automated Service Menu:**\n\n🔔 **Proactive Account Maintenance Reminder:**\n> *${reminder}*\n\n**Please select or speak one of the following menu options:**\n\n• **Press 1:** Balance Inquiry *(Checking, Savings & Total Relationship)*\n• **Press 2:** Credit Card Statement *(Balances, Due Dates & e-Statements)*\n• **Press 3:** Overdraft Protection & Customised VIP Offers\n• **Press 4:** Purchase History & AI Rewards Recommendations\n• **Press 5:** Upcoming Due Reminders & Fee Avoidance Checklist\n• **Press 6:** Priority Handover to Dedicated Concierge Specialist\n• **Press 7:** Language Selection *(Español / English)*`;

        return {
            subagent_id: "traditional_menu",
            subagent_title: "Traditional Voice & DTMF Menu",
            message: msg,
            speech_message: `Welcome to Key Privilege Automated Services. ${reminder}. Press 1 for balance, 2 for credit card, 3 for offers, 4 for purchase history, 5 for due reminders, 6 for dedicated concierge, or 7 for language selection.`,
            audio_prompt_code: "[K2U_ENG.700.au]",
            fee_reminder_banner: reminder,
            suggested_quick_replies: [
                "1. Balance Inquiry", "2. Credit Card Statement", "3. Overdraft & Offers",
                "4. Purchase Recommendations", "5. Due Reminders", "6. Dedicated Concierge", "7. Language Selection"
            ]
        };
    }

    function handleLanguageSelection(c) {
        c.language = c.language === "ENG" ? "SPA" : "ENG";
        const isSpa = c.language === "SPA";
        const msg = isSpa
            ? `🌐 **Preferencia de Idioma Actualizada a Español:**\n\nHemos configurado su experiencia y su enrutamiento telefónico en **Español** (\`sessionKey.languageCode = 'SPA'\`).\n\n• Sus transferencias telefónicas prioritarias se dirigirán a la cola de agentes bilingües (\`MMCCA_SPANISH\`).\n• Todos los avisos de voz y estados de cuenta se presentarán en español.`
            : `🌐 **Language Preference Updated to English:**\n\nYour session language has been switched to **English** (\`sessionKey.languageCode = 'ENG'\`).\n\n• Priority transfers will route to the Key Privilege desk (\`KEYPRIVCCA\` / \`KEY_PRIVATE_CLIENT_TRC\`).`;

        return {
            subagent_id: "language_selection",
            subagent_title: "Language Preference Specialist",
            message: msg,
            speech_message: isSpa ? "Su idioma ha sido cambiado a español." : "Your language has been switched to English.",
            audio_prompt_code: isSpa ? "[K2U_SPA.708.au]" : "[K2U_ENG.708.au]",
            suggested_quick_replies: ["Main Menu", "Balance Inquiry", "Credit Card Statement", "Due Reminders"]
        };
    }

    // Public API
    return {
        getCustomers: () => Object.values(customers),
        getActiveProfile: () => {
            const c = customers[activeIpi];
            const fee = evaluateFeeStatus(c);
            return { ...c, fee_status: fee };
        },
        setActiveIpi: (ipi) => {
            if (customers[ipi]) activeIpi = ipi;
        },
        initializeSession: (ipi) => {
            if (ipi) activeIpi = ipi;
            const c = customers[activeIpi];
            const fee = evaluateFeeStatus(c);
            const tier = c.tier === "PRIVATE_CLIENT" ? "Key Private Client" : "Key Privilege";

            let welcome = `🏛️ **Welcome to KeyBank ${tier} Concierge Services.**\n\nHello, ${c.name}. Your profile has been authenticated with **VIP Priority Treatment** (Household Relationship Group \`${c.relationship_group}\`).\n\n`;
            if (!fee.is_waived) {
                welcome += `⚠️ **Proactive Service Charge Notice:**\n${fee.alert_message}\n\n**How to Avoid the $25.00 Maintenance Fee Before Cycle End:**\n${fee.remedy}\n\n`;
            }
            welcome += `🎙️ *How can I assist you today? You can speak naturally, choose a quick action, or press for the traditional menu.*`;

            return {
                subagent_id: "root_agent",
                subagent_title: `${tier} Root Supervisor`,
                message: welcome,
                speech_message: `Welcome to KeyBank ${tier}, ${c.name}. How can we assist you today?`,
                audio_prompt_code: "[K2U_ENG.700.au]",
                fee_reminder_banner: fee.is_waived ? null : fee.alert_message,
                suggested_quick_replies: [
                    "1. Balance Inquiry", "2. Credit Card Statement", "3. Overdraft & Offers",
                    "4. Purchase History & Rewards", "5. Due Reminders & Fee Avoidance",
                    "6. Speak to Dedicated Concierge", "7. Traditional Menu"
                ]
            };
        },
        routeAndExecute: (text) => {
            const c = customers[activeIpi];
            const fee = evaluateFeeStatus(c);
            const lower = text.toLowerCase().trim();

            if (lower === "1" || lower.includes("balance") || lower.includes("how much money")) {
                return handleBalanceInquiry(c, fee);
            }
            if (lower === "2" || lower.includes("statement") || lower.includes("credit card bill")) {
                return handleCcStatement(c);
            }
            if (lower === "3" || lower.includes("overdraft") || lower.includes("offer") || lower.includes("cd rate") || lower.includes("loan")) {
                return handleOverdraftOffers(c);
            }
            if (lower === "4" || lower.includes("purchase") || lower.includes("history") || lower.includes("spending") || lower.includes("transaction")) {
                return handlePurchaseRecommendations(c);
            }
            if (lower === "5" || lower.includes("due") || lower.includes("reminder") || lower.includes("avoid fee") || lower.includes("maintenance fee") || lower.includes("service charge")) {
                return handleDueReminders(c, fee);
            }
            if (lower === "6" || lower.includes("representative") || lower.includes("agent") || lower.includes("concierge") || lower.includes("banker") || lower.includes("human")) {
                return handlePriorityHandover(c, fee);
            }
            if (lower === "7" || lower.includes("language") || lower.includes("spanish") || lower.includes("español")) {
                return handleLanguageSelection(c);
            }

            return handleTraditionalMenu(c, fee);
        }
    };
})();
