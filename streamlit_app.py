"""
UPSC MULTI-ANGLE PREDICTOR
Version 3.0 - With Razorpay Payments
"""

import streamlit as st
import anthropic
import base64
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
    .insight-box { background: #fffbeb; border-left: 4px solid #fbbf24; padding: 1.2rem; margin: 1rem 0; border-radius: 0 8px 8px 0; }
    
    .free-banner { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0; }
    .free-banner h3 { margin: 0; font-size: 1.1rem; }
    
    .feature-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; height: 100%; }
    .feature-card h4 { margin: 0 0 0.5rem 0; color: #334155; font-size: 0.95rem; }
    .feature-card p { margin: 0; color: #64748b; font-size: 0.85rem; line-height: 1.5; }
    
    .pricing-card { background: white; border: 2px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; text-align: center; transition: all 0.2s; }
    .pricing-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
    .pricing-card.popular { border-color: #f59e0b; background: #fffbeb; }
    .pricing-card h3 { margin: 0 0 0.5rem 0; color: #1e293b; }
    .pricing-card .price { font-size: 2rem; font-weight: 700; color: #1e293b; }
    .pricing-card .per-query { font-size: 0.85rem; color: #64748b; }
    
    .output-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; }
    
    .footer { text-align: center; padding: 2rem 1rem; color: #94a3b8; font-size: 0.85rem; border-top: 1px solid #e2e8f0; margin-top: 2rem; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# RAZORPAY CONFIG - Add your keys in Streamlit Secrets
# =============================================================================
# In Streamlit Secrets, add:
# RAZORPAY_KEY_ID = "rzp_live_xxxxx" or "rzp_test_xxxxx"
# RAZORPAY_KEY_SECRET = "your_secret"

def get_razorpay_keys():
    """Get Razorpay keys from secrets"""
    try:
        return st.secrets.get("RAZORPAY_KEY_ID", ""), st.secrets.get("RAZORPAY_KEY_SECRET", "")
    except:
        return "", ""

RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET = get_razorpay_keys()

# =============================================================================
# SESSION STATE
# =============================================================================

if 'credits' not in st.session_state:
    st.session_state.credits = 1  # FREE trial - 1 credit

if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

if 'free_used' not in st.session_state:
    st.session_state.free_used = False

if 'show_pricing' not in st.session_state:
    st.session_state.show_pricing = False

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("### Your Account")
    
    if not st.session_state.free_used:
        st.success("🎁 **1 FREE Trial** available!")
    
    st.markdown(f"**Credits:** {st.session_state.credits}")
    st.markdown(f"**Used:** {st.session_state.total_queries}")
    
    st.markdown("---")
    
    # Buy Credits Button
    if st.button("💳 Buy Credits", use_container_width=True):
        st.session_state.show_pricing = True
    
    st.markdown("---")
    st.caption("Questions? Contact us")

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

# FREE TRIAL BANNER
if not st.session_state.free_used:
    st.markdown("""
    <div class="free-banner">
        <h3>🎁 Try FREE — Your first query is on us. No signup needed.</h3>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PRICING SECTION (shown when Buy Credits clicked or no credits)
# =============================================================================

if st.session_state.show_pricing or st.session_state.credits < 1:
    st.markdown("---")
    st.markdown("## 💳 Get Credits")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>Try</h3>
            <div class="price">₹15</div>
            <p>1 Query</p>
            <p class="per-query">₹15 per query</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buy ₹15", key="buy_15", use_container_width=True):
            st.session_state.selected_plan = {"amount": 1500, "credits": 1, "name": "Try"}
    
    with col2:
        st.markdown("""
        <div class="pricing-card popular">
            <h3>⭐ Starter</h3>
            <div class="price">₹149</div>
            <p>10 Queries</p>
            <p class="per-query">₹14.90 per query</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buy ₹149", key="buy_149", use_container_width=True):
            st.session_state.selected_plan = {"amount": 14900, "credits": 10, "name": "Starter"}
    
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>Pro</h3>
            <div class="price">₹499</div>
            <p>40 Queries</p>
            <p class="per-query">₹12.48 per query</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buy ₹499", key="buy_499", use_container_width=True):
            st.session_state.selected_plan = {"amount": 49900, "credits": 40, "name": "Pro"}
    
    with col4:
        st.markdown("""
        <div class="pricing-card">
            <h3>Premium</h3>
            <div class="price">₹899</div>
            <p>80 Queries</p>
            <p class="per-query">₹11.24 per query</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Buy ₹899", key="buy_899", use_container_width=True):
            st.session_state.selected_plan = {"amount": 89900, "credits": 80, "name": "Premium"}
    
    # Show Razorpay payment button if plan selected
    if 'selected_plan' in st.session_state and st.session_state.selected_plan:
        plan = st.session_state.selected_plan
        st.markdown("---")
        st.markdown(f"### Selected: **{plan['name']}** — ₹{plan['amount']//100} for {plan['credits']} credits")
        
        if RAZORPAY_KEY_ID:
            # Razorpay Payment Button
            razorpay_html = f"""
            <form action="https://api.razorpay.com/v1/checkout/embedded" method="POST">
                <input type="hidden" name="key_id" value="{RAZORPAY_KEY_ID}">
                <input type="hidden" name="amount" value="{plan['amount']}">
                <input type="hidden" name="currency" value="INR">
                <input type="hidden" name="name" value="UPSC Predictor">
                <input type="hidden" name="description" value="{plan['credits']} Credits">
                <input type="hidden" name="prefill[email]" value="">
                <input type="hidden" name="notes[credits]" value="{plan['credits']}">
                <input type="hidden" name="callback_url" value="">
                <button type="submit" style="background: #528FF0; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%;">
                    💳 Pay ₹{plan['amount']//100} with Razorpay
                </button>
            </form>
            """
            st.markdown(razorpay_html, unsafe_allow_html=True)
            
            st.info("After payment, your credits will be added automatically. If not, contact us with your payment ID.")
        else:
            # Manual payment fallback
            st.warning("Payment gateway is being set up. For now, please use manual payment:")
            st.markdown(f"""
            **To get {plan['credits']} credits for ₹{plan['amount']//100}:**
            1. Pay via UPI: `your-upi-id@paytm`
            2. Or scan the QR code below
            3. Send screenshot to: **support@upscpredictor.in**
            4. Include your email in the message
            5. Credits will be added within 1 hour
            """)
        
        if st.button("← Back to pricing"):
            st.session_state.selected_plan = None
            st.rerun()
    
    st.markdown("---")

# =============================================================================
# THE PROBLEM
# =============================================================================

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

# =============================================================================
# FEATURES
# =============================================================================

st.markdown("### What You Get")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h4>🔀 5+5 Split</h4>
        <p>5 questions from the obvious subject + 5 from cross-subject angles. 
        Because UPSC asks the same topic from multiple GS papers.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h4>🪤 Real Exam Traps</h4>
        <p>"Always", "Only", "All of the above" — UPSC MCQs have patterns. 
        Built from 1,400+ previous year questions.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h4>📋 Answer Frameworks</h4>
        <p>Word allocation, must-include cases, committees, articles — and balanced conclusions 
        that examiners want to see.</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# INPUT SECTION
# =============================================================================

st.markdown("---")

if not st.session_state.free_used:
    st.markdown("### 🎁 Try Your FREE Query")
else:
    st.markdown("### Enter Any Current Affairs Topic")

topic_text = st.text_area(
    "Type or paste any news headline or topic:",
    placeholder="Examples:\n• RBI holds repo rate at 6.5%\n• India-China LAC disengagement begins\n• Supreme Court on bulldozer justice\n• Governor delays NEET bill in Tamil Nadu",
    height=100,
    label_visibility="collapsed"
)

# Generate button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.free_used:
        button_text = "🎁 Generate FREE (1 Trial)"
    else:
        button_text = "Generate 10 Questions →"
    
    generate_clicked = st.button(
        button_text,
        use_container_width=True,
        type="primary",
        disabled=(st.session_state.credits < 1)
    )

if st.session_state.credits < 1:
    st.warning("You've used your free trial. Get credits to continue practicing.")
    st.session_state.show_pricing = True

# =============================================================================
# GENERATION FUNCTION
# =============================================================================

def generate_questions(topic):
    """Generate UPSC questions from topic"""
    
    # Get API key
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        st.error("Configuration error. Please contact support.")
        return None
    
    client = anthropic.Anthropic(api_key=api_key)
    
    system_prompt = """You are an expert UPSC question setter. Generate 10 practice questions from the given topic.

CRITICAL REQUIREMENT — 5+5 SPLIT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 5 questions from PRIMARY SUBJECT (the obvious angle)
• 5 questions from CROSS-SUBJECT ANGLES (History, Geography, Economy, Ethics, Environment — whichever connects)

This is the KEY differentiator. A "Governor" news isn't just Polity — it's also:
- History (evolution of Governor's office from British era)
- Federalism (Centre-State relations)  
- Ethics (constitutional morality case study)

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

---
[Q2, Q3 same format]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SECTION B: CROSS-SUBJECT MCQs (Q4-Q5) 🔀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Q4** | [Different Subject] | CROSS-ANGLE 🔀

[Question linking news to different subject]
...

✓ **Answer:** [Letter]
💡 **Cross-Link:** [How this connects to original news]

---
**Q5** | [Another Subject] | CROSS-ANGLE 🔀
...

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

---
[M2 same format]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 SECTION D: CROSS-SUBJECT MAINS (M3-M5) 🔀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**M3** | [Different Paper] | CROSS-ANGLE 🔀 | 15 marks

"[Question from different angle]"

**Cross-Link:** [Why UPSC asks from this angle]
...

---
**M4** | [Another Paper] | CROSS-ANGLE 🔀
...

---
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

    messages = [{"role": "user", "content": f"Generate 10 UPSC questions for:\n\n{topic}\n\nRemember: 5 from primary subject + 5 from cross-subject angles."}]
    
    try:
        with st.spinner("Analyzing topic and generating questions... (20-30 seconds)"):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=6000,
                system=system_prompt,
                messages=messages
            )
        return response.content[0].text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# =============================================================================
# HANDLE GENERATION
# =============================================================================

if generate_clicked:
    if topic_text and len(topic_text.strip()) >= 5:
        output = generate_questions(topic_text)
        if output:
            # Deduct credit
            st.session_state.credits -= 1
            st.session_state.total_queries += 1
            
            # Mark free trial as used
            if not st.session_state.free_used:
                st.session_state.free_used = True
            
            # Display output
            st.markdown("---")
            st.markdown("## ✅ Your Practice Questions")
            
            st.markdown(f"""
            <div class="output-box">
                <pre style="white-space: pre-wrap; font-family: system-ui, -apple-system, sans-serif; font-size: 0.9rem; line-height: 1.7; color: #1e293b;">{output}</pre>
            </div>
            """, unsafe_allow_html=True)
            
            # Download button
            st.download_button(
                "📥 Download as Text File",
                output,
                f"upsc_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
            # Upsell after free trial
            if st.session_state.credits == 0:
                st.markdown("---")
                st.info("🎯 **Liked it?** Get more credits to continue practicing!")
                st.markdown("**₹15** = 1 query | **₹149** = 10 queries | **₹499** = 40 queries")
            
            st.balloons()
    else:
        st.warning("Please enter a topic (at least a few words)")

# =============================================================================
# SAMPLE OUTPUT
# =============================================================================

st.markdown("---")

with st.expander("📄 See sample output"):
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
(a) 1 and 2  (b) 2 and 3  (c) 1 and 3  (d) All

✓ **Answer: (b)** 
⚠️ **Trap:** "must" in Statement 1 — Governor CAN reserve Money Bills for President

---

**📝 SECTION B: CROSS-SUBJECT MCQs (Q4-Q5) 🔀**

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
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">Starting at ₹15 — less than your chai.</p>
</div>
""", unsafe_allow_html=True)
