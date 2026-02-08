"""
UPSC MULTI-ANGLE PREDICTOR v8.0
================================
- Email OTP authentication (free via Resend)
- No phone verification
- ₹12 per query

STREAMLIT SECRETS:
    ANTHROPIC_API_KEY = "sk-ant-..."
    SUPABASE_URL = "https://xxxxx.supabase.co"
    SUPABASE_KEY = "eyJhbG..."
    RESEND_API_KEY = "re_xxxxx"
    RAZORPAY_KEY_ID = "rzp_live_xxxxx"
    RAZORPAY_KEY_SECRET = "xxxxxxxxxxxxx"
    RAZORPAY_PAYMENT_URL = "https://rzp.io/rzp/xxxxx"
"""

import streamlit as st
import anthropic
import requests
import random
import os
import time
from datetime import datetime, timedelta
from supabase import create_client

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="UPSC Predictor | News → Questions",
    page_icon="📰",
    layout="wide"
)

# =============================================================================
# SUPABASE CLIENT
# =============================================================================

@st.cache_resource
def get_supabase_client():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None

supabase = get_supabase_client()

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
    .email-box { background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px; padding: 1.5rem; text-align: center; margin: 1.5rem 0; }
    .footer { text-align: center; padding: 2rem 1rem; color: #94a3b8; font-size: 0.85rem; border-top: 1px solid #e2e8f0; margin-top: 2rem; }
    .social-links { margin-top: 1rem; }
    .social-links a { margin: 0 10px; text-decoration: none; font-size: 1.5rem; }
    .tc-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin: 1rem 0; font-size: 0.85rem; }
    .tc-box ol { margin: 0.5rem 0; padding-left: 1.2rem; }
    .tc-box li { margin: 0.4rem 0; color: #475569; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# EMAIL / OTP FUNCTIONS
# =============================================================================

def generate_otp():
    """Generate 6-digit OTP."""
    return str(random.randint(100000, 999999))


def send_otp_email(email: str, otp: str) -> bool:
    """Send OTP via Resend."""
    try:
        api_key = st.secrets.get("RESEND_API_KEY")
        if not api_key:
            st.error("RESEND_API_KEY not configured in secrets")
            return False
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "UPSC Predictor <noreply@upscpredictor.in>",
                "to": email,
                "subject": "Your OTP for UPSC Predictor",
                "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;">
                    <h2 style="color: #1e293b;">UPSC Predictor</h2>
                    <p>Your verification code is:</p>
                    <div style="background: #f0f9ff; border: 2px solid #38bdf8; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0369a1;">{otp}</span>
                    </div>
                    <p style="color: #64748b; font-size: 14px;">This code expires in 10 minutes.</p>
                    <p style="color: #64748b; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                </div>
                """
            }
        )
        
        if response.status_code != 200:
            st.error(f"Resend error: {response.status_code} - {response.text}")
            return False
        return True
    except Exception as e:
        st.error(f"Email error: {str(e)}")
        return False


def save_otp(email: str, otp: str) -> bool:
    """Save OTP to database."""
    if not supabase:
        return False
    try:
        expires_at = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        supabase.table('otp_codes').insert({
            'email': email.lower().strip(),
            'otp': otp,
            'expires_at': expires_at,
            'used': False
        }).execute()
        return True
    except Exception:
        return False


def verify_otp(email: str, otp: str) -> bool:
    """Verify OTP from database."""
    if not supabase:
        return False
    try:
        email = email.lower().strip()
        result = supabase.table('otp_codes').select('*').eq('email', email).eq('otp', otp).eq('used', False).execute()
        
        if not result.data:
            return False
        
        otp_record = result.data[0]
        expires_at = datetime.fromisoformat(otp_record['expires_at'].replace('Z', '+00:00'))
        
        if datetime.now(expires_at.tzinfo) > expires_at:
            return False
        
        # Mark OTP as used
        supabase.table('otp_codes').update({'used': True}).eq('id', otp_record['id']).execute()
        return True
    except Exception:
        return False


# =============================================================================
# USER FUNCTIONS
# =============================================================================

def get_user_by_email(email: str):
    """Get user by email."""
    if not supabase:
        return None
    try:
        email = email.lower().strip()
        result = supabase.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def create_user(email: str):
    """Create new user with 1 free credit."""
    if not supabase:
        return None
    try:
        email = email.lower().strip()
        result = supabase.table('users').insert({
            'email': email,
            'free_credits': 1,
            'paid_credits': 0,
            'total_queries': 0,
            'email_verified': True
        }).execute()
        return result.data[0] if result.data else None
    except Exception:
        return None


def update_user_credits(email: str, free_credits: int, paid_credits: int, total_queries: int = None):
    """Update user credits."""
    if not supabase:
        return False
    try:
        email = email.lower().strip()
        update_data = {'free_credits': free_credits, 'paid_credits': paid_credits}
        if total_queries is not None:
            update_data['total_queries'] = total_queries
            update_data['last_query_at'] = datetime.utcnow().isoformat()
        supabase.table('users').update(update_data).eq('email', email).execute()
        return True
    except Exception:
        return False


def add_paid_credits(email: str, credits_to_add: int = 1):
    """Add paid credits to user."""
    email = email.lower().strip()
    user = get_user_by_email(email)
    
    if user:
        new_paid = user.get('paid_credits', 0) + credits_to_add
        new_free = user.get('free_credits', 0)
        update_user_credits(email, new_free, new_paid)
        return new_paid
    else:
        # Create user with paid credit (no free credit since they paid first)
        if not supabase:
            return 0
        try:
            supabase.table('users').insert({
                'email': email,
                'free_credits': 0,
                'paid_credits': credits_to_add,
                'total_queries': 0,
                'email_verified': True
            }).execute()
            return credits_to_add
        except Exception:
            return 0


# =============================================================================
# PAYMENT FUNCTIONS
# =============================================================================

def is_payment_processed(payment_id: str) -> bool:
    """Check if payment already processed."""
    if not supabase:
        return payment_id in st.session_state.get('processed_payments', set())
    try:
        result = supabase.table('payments').select('razorpay_payment_id').eq('razorpay_payment_id', payment_id).execute()
        return len(result.data) > 0
    except Exception:
        return False


def record_payment(payment_id: str, email: str, amount: int = 12):
    """Record payment in database."""
    if not supabase:
        st.session_state.setdefault('processed_payments', set()).add(payment_id)
        return True
    try:
        supabase.table('payments').insert({
            'razorpay_payment_id': payment_id,
            'email': email.lower().strip(),
            'amount': amount,
            'status': 'success'
        }).execute()
        return True
    except Exception:
        return False


def check_and_credit_pending_payments(email: str) -> int:
    """Check Razorpay for recent payments by email and credit if not processed."""
    try:
        key_id = st.secrets["RAZORPAY_KEY_ID"]
        key_secret = st.secrets["RAZORPAY_KEY_SECRET"]
        
        # Fetch recent payments from Razorpay (last 24 hours)
        from_timestamp = int(time.time()) - 86400  # 24 hours ago
        
        response = requests.get(
            f"https://api.razorpay.com/v1/payments",
            auth=(key_id, key_secret),
            params={
                'from': from_timestamp,
                'count': 50
            }
        )
        
        if response.status_code != 200:
            return 0
        
        payments = response.json().get('items', [])
        credits_added = 0
        
        for payment in payments:
            # Check if this payment matches user's email and is captured
            payment_email = payment.get('email', '').lower().strip()
            payment_id = payment.get('id', '')
            status = payment.get('status', '')
            
            if payment_email == email.lower().strip() and status == 'captured':
                # Check if already processed
                if not is_payment_processed(payment_id):
                    # Record and credit
                    if record_payment(payment_id, email):
                        add_paid_credits(email, 1)
                        credits_added += 1
        
        return credits_added
    except Exception as e:
        return 0


def fetch_email_from_payment(payment_id: str) -> str:
    """Fetch email from Razorpay payment."""
    try:
        key_id = st.secrets["RAZORPAY_KEY_ID"]
        key_secret = st.secrets["RAZORPAY_KEY_SECRET"]
        
        response = requests.get(
            f"https://api.razorpay.com/v1/payments/{payment_id}",
            auth=(key_id, key_secret)
        )
        
        if response.status_code == 200:
            payment = response.json()
            email = payment.get('email', '').lower().strip()
            return email if email else None
        return None
    except Exception:
        return None


def process_razorpay_return():
    """Process Razorpay redirect after payment - auto-login user."""
    params = st.query_params
    
    if 'razorpay_payment_id' not in params:
        return False
    
    payment_id = params.get('razorpay_payment_id', '')
    
    if is_payment_processed(payment_id):
        # Already processed - but still login user
        email = fetch_email_from_payment(payment_id)
        if email:
            user = get_user_by_email(email)
            if user:
                st.session_state.email = email
                st.session_state.free_credits = user.get('free_credits', 0)
                st.session_state.paid_credits = user.get('paid_credits', 0)
                st.session_state.total_queries = user.get('total_queries', 0)
                st.session_state.logged_in = True
        st.query_params.clear()
        return False
    
    # Fetch email from Razorpay
    email = fetch_email_from_payment(payment_id)
    if not email:
        st.query_params.clear()
        return False
    
    # Record payment and add credit
    if record_payment(payment_id, email):
        add_paid_credits(email, 1)
        user = get_user_by_email(email)
        
        if user:
            st.session_state.email = email
            st.session_state.free_credits = user.get('free_credits', 0)
            st.session_state.paid_credits = user.get('paid_credits', 0)
            st.session_state.total_queries = user.get('total_queries', 0)
            st.session_state.logged_in = True
            st.session_state.just_paid = True
        st.query_params.clear()
        return True
    
    st.query_params.clear()
    return False


# =============================================================================
# QUESTION GENERATION
# =============================================================================

def generate_questions(topic):
    """Generate 10 UPSC questions using Claude API."""
    
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        st.error("⚠️ API not configured. Contact support.")
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


# =============================================================================
# UI COMPONENTS
# =============================================================================

def show_terms_and_conditions():
    """Display T&C."""
    st.markdown("""
    <div class="tc-box">
        <strong>Terms & Conditions</strong>
        <ol>
            <li><strong>One free query per email.</strong> No exceptions.</li>
            <li><strong>₹12 = 1 query = 10 questions.</strong> Credits don't expire.</li>
            <li><strong>No refunds</strong> once query is generated. AI costs us money the moment you click generate.</li>
            <li><strong>We've trained our AI on PYQs, UPSC's style of setting traps, UPSC expectations based on topper analysis, and a lot more.</strong> However, we don't guarantee any exact question will appear in actual exam.</li>
            <li><strong>Don't share your account.</strong> One email = one user.</li>
            <li><strong>We store your email</strong> only to track your credits. We won't spam.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)


def show_email_entry():
    """Display email + OTP entry."""
    st.markdown("""
    <div class="email-box">
        <h3 style="margin: 0 0 0.5rem 0; color: #166534;">🎁 Get 1 FREE Query</h3>
        <p style="margin: 0; color: #15803d; font-size: 0.95rem;">New user? Verify email to claim your free query.<br/>
        Returning user? Login to load your credits.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Step 1: Email entry
        email_input = st.text_input(
            "email",
            placeholder="your.email@gmail.com",
            label_visibility="collapsed"
        )
        
        # OTP state management
        if 'otp_sent' not in st.session_state:
            st.session_state.otp_sent = False
        if 'otp_email' not in st.session_state:
            st.session_state.otp_email = None
        
        if not st.session_state.otp_sent:
            # Show T&C and Send OTP button
            show_terms_and_conditions()
            tc_agreed = st.checkbox("I agree to the Terms & Conditions", value=False)
            
            if st.button("📧 Send OTP", use_container_width=True, type="primary"):
                if not tc_agreed:
                    st.warning("Please agree to the Terms & Conditions.")
                elif not email_input or '@' not in email_input or '.' not in email_input:
                    st.error("Please enter a valid email address.")
                else:
                    # Generate and send OTP
                    otp = generate_otp()
                    if save_otp(email_input, otp) and send_otp_email(email_input, otp):
                        st.session_state.otp_sent = True
                        st.session_state.otp_email = email_input.lower().strip()
                        st.rerun()
                    else:
                        st.error("Could not send OTP. Please try again.")
        else:
            # Show OTP entry
            st.success(f"✅ OTP sent to {st.session_state.otp_email}")
            st.markdown("""
            <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 0.75rem; margin: 0.5rem 0;">
                <p style="margin: 0; color: #92400e; font-size: 0.9rem;">📬 <strong>Don't see the email?</strong> Check your <strong>Spam/Junk folder</strong>. The email comes from "UPSC Predictor".</p>
            </div>
            """, unsafe_allow_html=True)
            
            otp_input = st.text_input(
                "otp",
                placeholder="Enter 6-digit OTP",
                label_visibility="collapsed",
                max_chars=6
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✓ Verify OTP", use_container_width=True, type="primary"):
                    if not otp_input or len(otp_input) != 6:
                        st.error("Please enter 6-digit OTP.")
                    elif verify_otp(st.session_state.otp_email, otp_input):
                        # OTP verified - login or create user
                        email = st.session_state.otp_email
                        
                        # Check for pending Razorpay payments BEFORE loading user
                        pending_credits = check_and_credit_pending_payments(email)
                        
                        user = get_user_by_email(email)
                        
                        if user:
                            # Returning user
                            st.session_state.email = email
                            st.session_state.free_credits = user.get('free_credits', 0)
                            st.session_state.paid_credits = user.get('paid_credits', 0)
                            st.session_state.total_queries = user.get('total_queries', 0)
                            st.session_state.logged_in = True
                            if pending_credits > 0:
                                st.session_state.just_paid = True
                        else:
                            # New user
                            create_user(email)
                            st.session_state.email = email
                            st.session_state.free_credits = 1
                            st.session_state.paid_credits = pending_credits
                            st.session_state.total_queries = 0
                            st.session_state.logged_in = True
                            st.session_state.is_new_user = True
                        
                        # Reset OTP state
                        st.session_state.otp_sent = False
                        st.session_state.otp_email = None
                        st.rerun()
                    else:
                        st.error("Invalid or expired OTP. Please try again.")
            
            with col_b:
                if st.button("← Change Email", use_container_width=True):
                    st.session_state.otp_sent = False
                    st.session_state.otp_email = None
                    st.rerun()


def show_payment_section():
    """Display Razorpay payment button."""
    st.markdown("""
    <div class="pay-box">
        <h3>☕ ₹12 — Less than your chai</h3>
        <p>Pay once. Get 10 practice questions instantly.<br/>
        5 MCQs with traps + 5 Mains with answer frameworks.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            razorpay_url = st.secrets["RAZORPAY_PAYMENT_URL"]
            
            # Show user's email if logged in
            if st.session_state.logged_in:
                st.info(f"💡 **Use this email in Razorpay:** {st.session_state.email}")
            
            # Open in new tab using HTML button
            st.markdown(f"""
            <a href="{razorpay_url}" target="_blank" style="
                display: inline-block;
                width: 100%;
                text-align: center;
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;
                text-decoration: none;
                box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
            ">💳 Pay ₹12 — Get 1 Query</a>
            <p style="text-align: center; color: #64748b; font-size: 12px; margin-top: 8px;">
                Opens in new tab • Secure payment via Razorpay
            </p>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("**After payment, come back here and click:**")
            
            # Refresh credits button
            if st.session_state.logged_in:
                if st.button("🔄 Refresh Credits", use_container_width=True, type="primary"):
                    with st.spinner("Checking for payments..."):
                        pending = check_and_credit_pending_payments(st.session_state.email)
                    if pending > 0:
                        user = get_user_by_email(st.session_state.email)
                        if user:
                            st.session_state.free_credits = user.get('free_credits', 0)
                            st.session_state.paid_credits = user.get('paid_credits', 0)
                        st.success(f"✅ Added {pending} credit(s)!")
                        st.session_state.show_payment = False
                        st.rerun()
                    else:
                        st.warning("No new payments found. Make sure you used the same email.")
            
        except (KeyError, FileNotFoundError):
            st.error("Payment not configured. Contact support.")


# =============================================================================
# SESSION STATE
# =============================================================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'email' not in st.session_state:
    st.session_state.email = None

if 'free_credits' not in st.session_state:
    st.session_state.free_credits = 0

if 'paid_credits' not in st.session_state:
    st.session_state.paid_credits = 0

if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0

if 'just_paid' not in st.session_state:
    st.session_state.just_paid = False

if 'is_new_user' not in st.session_state:
    st.session_state.is_new_user = False


# =============================================================================
# PROCESS RAZORPAY RETURN
# =============================================================================

process_razorpay_return()


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("### Your Session")
    
    if st.session_state.logged_in:
        st.markdown(f"📧 {st.session_state.email}")
        
        total_credits = st.session_state.free_credits + st.session_state.paid_credits
        if total_credits > 0:
            st.success(f"✅ **{total_credits}** query ready")
        else:
            st.warning("⚡ No queries left")
        
        st.markdown(f"🎁 Free: **{st.session_state.free_credits}**")
        st.markdown(f"💳 Paid: **{st.session_state.paid_credits}**")
        st.markdown(f"📊 Used: **{st.session_state.total_queries}**")
        
        st.markdown("---")
        
        # Direct payment link (opens in new tab)
        try:
            razorpay_url = st.secrets["RAZORPAY_PAYMENT_URL"]
            st.markdown(f"""
            <a href="{razorpay_url}" target="_blank" style="
                display: block;
                width: 100%;
                text-align: center;
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
                text-decoration: none;
                margin-bottom: 8px;
            ">💳 Buy Credits (₹12)</a>
            """, unsafe_allow_html=True)
            st.caption(f"Use email: {st.session_state.email}")
        except:
            pass
        
        # Refresh credits button
        if st.button("🔄 Refresh Credits", use_container_width=True):
            with st.spinner("Checking..."):
                pending = check_and_credit_pending_payments(st.session_state.email)
            if pending > 0:
                user = get_user_by_email(st.session_state.email)
                if user:
                    st.session_state.free_credits = user.get('free_credits', 0)
                    st.session_state.paid_credits = user.get('paid_credits', 0)
                st.success(f"✅ +{pending} credit(s)!")
                st.rerun()
            else:
                st.info("No new payments")
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.email = None
            st.session_state.free_credits = 0
            st.session_state.paid_credits = 0
            st.session_state.otp_sent = False
            st.session_state.otp_email = None
            st.rerun()
    else:
        st.markdown("👇 **Enter email below to start**")
        st.markdown("---")
        st.markdown("**₹12 per query**")
        st.markdown("*1 FREE query for new users*")
    
    st.markdown("---")
    st.markdown("**Follow Us**")
    st.markdown("[📺 YouTube](https://www.youtube.com/channel/UCMVxFvBmNwIdLFdq65yqTFg) • [📸 Instagram](https://www.instagram.com/upscpredictor.in)")


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


# Status banners
if st.session_state.just_paid:
    st.markdown('<div class="paid-banner"><h3>✅ Payment successful! Credit added to your account.</h3></div>', unsafe_allow_html=True)
    st.session_state.just_paid = False

if st.session_state.get('is_new_user'):
    st.markdown('<div class="paid-banner"><h3>🎁 Welcome! You have 1 FREE query. Use it wisely!</h3></div>', unsafe_allow_html=True)
    st.session_state.is_new_user = False


# =============================================================================
# MAIN CONTENT
# =============================================================================

if not st.session_state.logged_in:
    # ── NOT LOGGED IN ──
    
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
    
    st.markdown("---")
    show_email_entry()

else:
    # ── LOGGED IN ──
    
    total_credits = st.session_state.free_credits + st.session_state.paid_credits
    
    if total_credits > 0:
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
                    # Deduct credit - free first, then paid
                    if st.session_state.free_credits > 0:
                        st.session_state.free_credits -= 1
                    else:
                        st.session_state.paid_credits -= 1
                    
                    st.session_state.total_queries += 1
                    
                    # Update database
                    update_user_credits(
                        st.session_state.email,
                        st.session_state.free_credits,
                        st.session_state.paid_credits,
                        st.session_state.total_queries
                    )
                    
                    st.markdown("---")
                    st.markdown("## ✅ Your Practice Questions")
                    st.markdown(f'<div class="output-box"><pre style="white-space:pre-wrap; font-family:system-ui,-apple-system,sans-serif; font-size:0.9rem; line-height:1.7; color:#1e293b;">{output}</pre></div>', unsafe_allow_html=True)
                    
                    st.download_button(
                        "📥 Download as Text File", output,
                        f"upsc_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    
                    new_total = st.session_state.free_credits + st.session_state.paid_credits
                    if new_total == 0:
                        st.markdown("---")
                        st.info("🎯 **Liked it?** Buy more credits from the sidebar menu (₹12 each).")
                    
                    st.balloons()
    
    else:
        # No credits left
        st.markdown("### You're out of credits!")
        st.markdown("""
        <div class="pay-box">
            <h3>Get more queries</h3>
            <p>Open the <strong>sidebar menu</strong> (☰ top left on mobile) and click <strong>Buy Credits</strong>.</p>
            <p style="margin-top: 1rem;">₹12 per query • 10 questions each</p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# SAMPLE OUTPUT
# =============================================================================

st.markdown("---")
with st.expander("📄 See a sample output — what you get"):
    st.markdown("""
**Input:** *Governor returns NEET bill*

---

**📌 TOPIC ANALYSIS**

**Topic:** Governor returns NEET bill in Tamil Nadu  
**Primary Subject:** GS-II — Polity & Governance

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
💡 **Key Point:** Article 200 gives Governor 4 options but no time limit specified

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

**📝 SECTION C: PRIMARY MAINS (M1-M2)**

**M1 | GS-II | Polity | PRIMARY | 15 marks**

*"The office of Governor has become a tool for Centre-State confrontation rather than cooperation." Critically examine with recent examples.*

**Answer Framework (250 words):**

• **Intro (30 words):** Define Governor's constitutional role under Article 153-162. Acknowledge recent controversies have reignited debate on gubernatorial discretion.

• **Body (180 words):**
  - Constitutional position: Agent of Centre, not elected, serves at pleasure
  - Areas of friction: Bill assent delays, dissolution advice, President's rule
  - Recent examples: Tamil Nadu NEET bill, Kerala ordinance row, Punjab budget session
  - Sarkaria Commission view: Should be detached figure, not political agent
  - Punchhi Commission: Fixed 6-month timeline for bill action recommended

• **Conclusion (40 words):** Balanced view — Governor's discretion needed for constitutional safeguards, but must not become instrument of partisan politics. Codification of timelines could resolve ambiguity.

**Must Include:** Nabam Rebia case, Sarkaria Commission, Article 200  
**Avoid:** One-sided criticism of either Centre or States

---

**📝 SECTION D: CROSS-SUBJECT MAINS (M3-M5) 🔀**

**M5 | GS-IV | Ethics | CROSS-ANGLE 🔀 | Case Study**

*You are a newly appointed Governor. The ruling party at Centre asks you to delay a state bill that could embarrass them politically. The bill has popular mandate and passed with 2/3rd majority. What would you do?*

**Ethical Dimensions:** Constitutional duty vs political loyalty, Integrity vs career preservation

**Framework:**
• Identify stakeholders: Centre, State govt, citizens, Constitution
• Values at stake: Constitutional morality, integrity, impartiality
• Options: Comply with Centre, follow Constitution, seek legal opinion
• Decision: Act per Article 200 — assent, return once, or reserve for President with reasons
• Justify: Oath of office binds to Constitution, not political masters
""")


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("""
<div class="footer">
    <p><strong>UPSC Multi-Angle Predictor</strong></p>
    <p>For aspirants who read the newspaper but want exam-ready practice.</p>
    <div class="social-links">
        <a href="https://www.youtube.com/channel/UCMVxFvBmNwIdLFdq65yqTFg" target="_blank">📺 YouTube</a>
        <a href="https://www.instagram.com/upscpredictor.in" target="_blank">📸 Instagram</a>
    </div>
    <p style="font-size: 0.8rem; margin-top: 1rem;">₹12 per query — less than your chai ☕</p>
</div>
""", unsafe_allow_html=True)
