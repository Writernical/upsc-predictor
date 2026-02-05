"""
UPSC MULTI-ANGLE PREDICTOR v5.1
================================
Access code system — no free trial on refresh
Free trial via shareable FREE-XXXX codes
Paid queries via UPSC-XXXX codes

STREAMLIT SECRETS NEEDED:
    ANTHROPIC_API_KEY = "sk-ant-..."
    CREDIT_CODES = "UPSC-79CV,UPSC-ID5E,..."
    FREE_CODES = "FREE-7ZAV,FREE-3945,..."
"""

import streamlit as st
import anthropic
import os
from datetime import datetime

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="UPSC Predictor | News → Questions",
    page_icon="📰",
    layout="wide"
)

# =============================================================================
# CSS
# =============================================================================

st.markdown("""
<style>
    .main { padding: 1rem 2rem; }
    .hero { text-align: center; padding: 1.5rem 0; }
    .hero h1 { font-size: 2rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem; }
    .hero-sub { font-size: 1.05rem; color: #64748b; max-width: 650px; margin: 0 auto; }
    .problem-box { background: #fef2f2; border-left: 4px solid #f87171; padding: 1.2rem; margin: 1.5rem 0; border-radius: 0 8px 8px 0; }
    .problem-box p { margin: 0; color: #7f1d1d; }
    .insight-box { background: #fffbeb; border-left: 4px solid #fbbf24; padding: 1.2rem; margin: 1rem 0; border-radius: 0 8px 8px 0; }
    .insight-box p { margin: 0; color: #78350f; }
    .paid-banner { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0; }
    .paid-banner h3 { margin: 0; font-size: 1.1rem; }
    .pay-box { background: #fffbeb; border: 2px solid #f59e0b; border-radius: 12px; padding: 2rem; text-align: center; margin: 2rem 0; }
    .pay-box h3 { margin: 0 0 0.5rem 0; color: #92400e; font-size: 1.3rem; }
    .pay-box p { margin: 0.5rem 0; color: #78350f; }
    .feature-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; height: 100%; }
    .feature-card h4 { margin: 0 0 0.5rem 0; color: #334155; font-size: 0.95rem; }
    .feature-card p { margin: 0; color: #64748b; font-size: 0.85rem; line-height: 1.5; }
    .output-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; }
    .upi-box { background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 1rem; margin-top: 1rem; text-align: center; }
    .code-box { background: #f0f9ff; border: 2px solid #38bdf8; border-radius: 12px; padding: 1.5rem; text-align: center; margin: 1.5rem 0; }
    .footer { text-align: center; padding: 2rem 1rem; color: #94a3b8; font-size: 0.85rem; border-top: 1px solid #e2e8f0; margin-top: 2rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_all_valid_codes():
    """Load all valid codes (paid + free) from Streamlit secrets."""
    all_codes = set()
    try:
        codes_str = st.secrets.get("CREDIT_CODES", "")
        all_codes.update(code.strip() for code in codes_str.split(",") if code.strip())
    except (KeyError, FileNotFoundError):
        pass
    try:
        free_str = st.secrets.get("FREE_CODES", "")
        all_codes.update(code.strip() for code in free_str.split(",") if code.strip())
    except (KeyError, FileNotFoundError):
        pass
    return all_codes


def validate_access_code(code):
    """Check if access code is valid and unused."""
    code = code.strip().upper()
    valid_codes = get_all_valid_codes()
    
    if code not in valid_codes:
        return False, "❌ Invalid code. Please check and try again."
    
    if code in st.session_state.used_codes:
        return False, "❌ This code has already been used."
    
    return True, "✅ Code accepted! You have 1 query ready."


def generate_questions(topic):
    """Generate 10 UPSC questions using Claude API."""
    
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        st.error("⚠️ API not configured. Contact support on WhatsApp.")
        return None
    
    client = anthropic.Anthropic(api_key=api_key)
    
    system_prompt = """You are an expert UPSC question setter. Generate 10 practice questions from the given topic.

CRITICAL REQUIREMENT — 5+5 SPLIT:
• 5 questions from PRIMARY SUBJECT (the obvious angle)
• 5 questions from CROSS-SUBJECT ANGLES (History, Geography, Economy, Ethics, Environment — whichever connects)

DISTRIBUTE AS:
- MCQ 1-3: Primary Subject
- MCQ 4-5: Cross-Subject Angles (DIFFERENT subjects)
- MAINS 1-2: Primary Subject
- MAINS 3-5: Cross-Subject Angles (include Ethics case study)

FORMAT:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 TOPIC ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Topic:** [News item]
**Primary Subject:** [GS-I/II/III/IV] — [Subject name]

**Cross-Subject Angles:**
• [Angle 1] — [Different GS Paper] — [Connection]
• [Angle 2] — [Different GS Paper] — [Connection]
• [Angle 3] — [Different GS Paper] — [Connection]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SECTION A: PRIMARY MCQs (Q1-Q3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Q1** | [Primary Subject] | PRIMARY

[Question]
(a) [Option]
(b) [Option]
(c) [Option]
(d) [Option]

✓ **Answer:** [Letter]
⚠️ **Trap:** [Explain the trap]
💡 **Key Point:** [1-2 lines]

-----

[Q2, Q3 same format]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SECTION B: CROSS-SUBJECT MCQs (Q4-Q5) 🔀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Q4** | [Different Subject] | CROSS-ANGLE 🔀

[Question linking news to different subject]
(a)-(d) options

✓ **Answer:** [Letter]
💡 **Cross-Link:** [How this connects to original news]

-----

**Q5** | [Another Subject] | CROSS-ANGLE 🔀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SECTION C: PRIMARY MAINS (M1-M2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**M1** | [Primary Paper] | PRIMARY | 15 marks

"[Question]"

**Answer Framework (250 words):**
• **Intro (30 words):** [Approach]
• **Body (150 words):** [Key points]
• **Conclusion (40 words):** [Balanced ending]

**Must Include:** [Cases, committees, articles]
**Avoid:** [Common mistakes]

-----

[M2 same format]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SECTION D: CROSS-SUBJECT MAINS (M3-M5) 🔀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**M3** | [Different Paper] | CROSS-ANGLE 🔀 | 15 marks
**Cross-Link:** [Why UPSC asks from this angle]

-----

**M4** | [Another Paper] | CROSS-ANGLE 🔀

-----

**M5** | GS-IV | Ethics | CROSS-ANGLE 🔀 | Case Study

[Ethics case study based on the topic]
**Ethical Dimensions:** [Values at stake]
**Framework:** [How to approach]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULES:
1. Exactly 5 primary + 5 cross-subject questions
2. Cross-subject must be GENUINELY different subjects
3. Use real UPSC trap patterns
4. All cases/committees must be REAL
5. Balanced conclusions always"""

    try:
        with st.spinner("🧠 Analyzing topic and generating questions… (20-30 seconds)"):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=6000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Generate 10 UPSC questions for:\n\n{topic}\n\nRemember: 5 from primary subject + 5 from cross-subject angles."
                }]
            )
        return response.content[0].text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def show_payment_section():
    """Display UPI payment instructions."""
    st.markdown("""
    <div class="pay-box">
        <h3>☕ ₹15 — That's less than your chai</h3>
        <p>Pay once. Get 10 practice questions instantly.<br/>
        5 MCQs with traps + 5 Mains with answer frameworks.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("#### Step 1: Pay ₹15 via UPI")
        st.markdown('<div class="upi-box"><p style="margin:0; color:#166534;"><strong>UPI ID</strong></p></div>', unsafe_allow_html=True)
        st.code("writernical@sbi", language=None)
        
        wa_msg = "Hi, I paid ₹15 for UPSC Predictor. Sending screenshot."
        st.link_button(
            "💬 Step 2: Send Screenshot on WhatsApp",
            f"https://wa.me/919150801098?text={wa_msg.replace(' ', '%20')}",
            use_container_width=True
        )
        st.caption("You'll receive an access code within 15 minutes.")


def show_code_entry():
    """Display the access code entry box."""
    st.markdown("""
    <div class="code-box">
        <p style="margin:0; color:#0369a1; font-size: 1rem;"><strong>🔑 Have a code? Enter below to unlock your questions.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        code_input = st.text_input(
            "access_code",
            placeholder="e.g. UPSC-79CV or FREE-7ZAV",
            label_visibility="collapsed",
            max_chars=10
        )
        
        if st.button("🔓 Redeem Code", use_container_width=True, type="primary"):
            if code_input:
                valid, msg = validate_access_code(code_input)
                if valid:
                    st.session_state.credits += 1
                    st.session_state.used_codes.add(code_input.strip().upper())
                    st.session_state.just_paid = True
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Please enter your access code.")


# =============================================================================
# SESSION STATE
# =============================================================================

if 'credits' not in st.session_state:
    st.session_state.credits = 0  # No free credit on load

if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

if 'just_paid' not in st.session_state:
    st.session_state.just_paid = False

if 'used_codes' not in st.session_state:
    st.session_state.used_codes = set()


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("### Your Session")
    if st.session_state.credits > 0:
        st.success(f"✅ **{st.session_state.credits}** query ready")
    else:
        st.warning("⚡ No queries left")
    st.markdown(f"Queries used: **{st.session_state.total_queries}**")
    st.markdown("---")
    st.markdown("**₹15 per query**")
    st.markdown("---")
    st.markdown("[💬 WhatsApp Support](https://wa.me/919150801098)")


# =============================================================================
# HERO
# =============================================================================

st.markdown("""
<div class="hero">
    <h1>From Today's Newspaper to Tomorrow's Answer Sheet</h1>
    <p class="hero-sub">
        You read current affairs daily. But there's a gap between what you read and how UPSC asks. 
        This tool bridges that gap.
    </p>
</div>
""", unsafe_allow_html=True)


# Status banner
if st.session_state.just_paid:
    st.markdown('<div class="paid-banner"><h3>✅ Code redeemed! Enter your topic below.</h3></div>', unsafe_allow_html=True)
    st.session_state.just_paid = False


# =============================================================================
# PROBLEM + FEATURES (show when no queries done yet)
# =============================================================================

if st.session_state.total_queries == 0:
    st.markdown("""
    <div class="problem-box">
        <p><strong>The frustration you know too well:</strong> You read about "Governor delays NEET Bill" and file it under Polity. 
        Then in the exam, UPSC asks the same topic from History (evolution of Governor's office), Federalism (Centre-State friction), 
        and Ethics (constitutional morality). You knew the news. You just didn't know the angles.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-box">
        <p><strong>What toppers understand:</strong> UPSC doesn't test news. They test concepts through news. 
        One headline can appear in GS-I, II, III, and IV — each time from a different angle.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What You Get")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="feature-card"><h4>🔀 5+5 Split</h4><p>5 questions from the obvious subject + 5 from cross-subject angles. Because UPSC asks the same topic from multiple GS papers.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="feature-card"><h4>🪤 Real Exam Traps</h4><p>"Always", "Only", "All of the above" — UPSC MCQs have patterns. Built from 1,400+ previous year questions.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="feature-card"><h4>📋 Answer Frameworks</h4><p>Word allocation, must-include cases, committees, articles — and balanced conclusions that examiners want to see.</p></div>', unsafe_allow_html=True)
    
    # Free trial codes
    st.markdown("""
    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 1.2rem; border-radius: 10px; text-align: center; margin: 1.5rem 0;">
        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.1rem;">🎁 Try it FREE — use one of these codes below</h3>
        <p style="margin: 0; font-size: 1.3rem; font-weight: 700; letter-spacing: 2px;">FREE-7ZAV &nbsp; &nbsp; FREE-3945</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.9;">Limited codes • First come, first served</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN: CODE ENTRY → INPUT → GENERATE  or  PAYMENT
# =============================================================================

st.markdown("---")

# Always show the code entry box at top
show_code_entry()

if st.session_state.credits > 0:
    # ── HAS CREDITS: SHOW INPUT ──
    st.markdown("---")
    st.markdown("### Enter Any Current Affairs Topic")
    
    topic_text = st.text_area(
        "topic",
        placeholder="Examples:\n• RBI holds repo rate at 6.5%\n• India-China LAC disengagement begins\n• Supreme Court on bulldozer justice\n• Governor delays NEET bill in Tamil Nadu",
        height=100,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        clicked = st.button("🚀 Generate 10 Questions", use_container_width=True, type="primary")
    
    if clicked:
        if not topic_text or len(topic_text.strip()) < 5:
            st.warning("Please enter a topic (at least a few words)")
        else:
            output = generate_questions(topic_text)
            if output:
                st.session_state.credits -= 1
                st.session_state.total_queries += 1
                
                st.markdown("---")
                st.markdown("## ✅ Your Practice Questions")
                st.markdown(f'<div class="output-box"><pre style="white-space:pre-wrap; font-family:system-ui,-apple-system,sans-serif; font-size:0.9rem; line-height:1.7; color:#1e293b;">{output}</pre></div>', unsafe_allow_html=True)
                
                st.download_button(
                    "📥 Download as Text File", output,
                    f"upsc_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                if st.session_state.credits == 0:
                    st.markdown("---")
                    st.info("🎯 **Liked it?** Pay ₹15 for your next set of 10 questions.")
                    show_payment_section()
                
                st.balloons()
else:
    # ── NO CREDITS: SHOW PAYMENT ──
    st.markdown("---")
    show_payment_section()


# =============================================================================
# SAMPLE OUTPUT
# =============================================================================

st.markdown("---")
with st.expander("📄 See a sample output — what you get for ₹15"):
    st.markdown("""
**Input:** *Governor returns NEET bill*

---

**📌 TOPIC ANALYSIS**

**Primary Subject:** GS-II (Polity & Governance)

**Cross-Subject Angles:**
• **History (GS-I)** — Evolution of Governor's office from British era
• **Federalism (GS-II)** — Centre-State tensions, Sarkaria Commission
• **Ethics (GS-IV)** — Constitutional morality vs political loyalty

---

**📝 SECTION A: PRIMARY MCQs (Q1-Q3)**

**Q1 | Polity | PRIMARY**

*Consider the following about Governor's power on bills:*

1. Governor must give assent to all Money Bills
2. Governor can return a Bill only once
3. No time limit for Governor to act on Bills

Which is correct?
(a) 1 and 2 &nbsp; (b) 2 and 3 &nbsp; (c) 1 and 3 &nbsp; (d) All

✓ **Answer: (b)**
⚠️ **Trap:** "must" in Statement 1 — Governor CAN reserve Money Bills for President

---

**📝 SECTION B: CROSS-SUBJECT MCQs 🔀**

**Q4 | History | CROSS-ANGLE 🔀**

*The office of Governor in British India was established under:*
(a) Regulating Act, 1773
(b) Charter Act, 1833
(c) Government of India Act, 1858
(d) Indian Councils Act, 1909

✓ **Answer: (a)**
💡 **Cross-Link:** Current debates trace back to colonial design of the office

---

**📝 SECTION D: CROSS-SUBJECT MAINS 🔀**

**M5 | GS-IV | Ethics | Case Study**

*You are a newly appointed Governor. The ruling party at Centre asks you to delay a state bill that could embarrass them politically. The bill has popular support. What would you do?*

**Ethical Dimensions:** Constitutional duty vs political pressure, Integrity vs loyalty
""")


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("""
<div class="footer">
    <p><strong>UPSC Multi-Angle Predictor</strong></p>
    <p>For aspirants who read the newspaper but want exam-ready practice.</p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">₹15 per query — less than your chai ☕</p>
</div>
""", unsafe_allow_html=True)
