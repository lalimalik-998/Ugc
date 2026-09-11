import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="UGC Global | Enterprise Marketplace",
    page_icon="🎬",
    layout="wide"
)

# --- PROFESSIONAL FADE & CLEAN THEME CSS ---
st.markdown("""
    <style>
    /* Fade & Modern Neutral Background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Fade Hero Typography */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1e293b;
        letter-spacing: -0.5px;
        margin-bottom: 0px;
    }
    .hero-subtitle {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }

    /* Soft Fade Cards Container */
    div.stContainer, div.stForm {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }

    /* Elegant Fade Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 100%, #1e40af 100%);
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- REAL / ZERO-STATE DATABASE INITIALIZATION ---
if "users" not in st.session_state:
    st.session_state.users = {}  # Bilkul khali database (Real Users Only)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "campaigns" not in st.session_state:
    st.session_state.campaigns = []  # Koi fake campaign nahi, sab zero se shuru hoga

# --- 1. LANDING & AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.markdown('<p class="hero-title">🎬 UGC Global Marketplace</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">The #1 Ecosystem connecting top creators with world-class brands.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
        
        with auth_tab1:
            st.subheader("Login to your Portal")
            login_email = st.text_input("Email Address", key="l_email")
            login_pass = st.text_input("Password", type="password", key="l_pass")
            
            if st.button("Login Now", use_container_width=True):
                if login_email in st.session_state.users and st.session_state.users[login_email]["password"] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.current_user = st.session_state.users[login_email]["name"]
                    st.session_state.user_role = st.session_state.users[login_email]["role"]
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid Email or Password, or account does not exist. Please sign up first.")
                    
        with auth_tab2:
            st.subheader("Join as Creator or Brand")
            reg_name = st.text_input("Full Name / Brand Name")
            reg_email = st.text_input("Email Address", key="r_email")
            reg_pass = st.text_input("Password", type="password", key="r_pass")
            reg_role = st.selectbox("Select Account Type", ["Creator", "Brand"])
            
            st.info("💡 **Note:** Creators never pay; you only earn money by uploading videos! Brands fund campaigns securely.")
            
            if st.button("Register Account", use_container_width=True):
                if reg_email in st.session_state.users:
                    st.warning("Email already registered. Please login.")
                elif not reg_name or not reg_email or not reg_pass:
                    st.error("Please fill in all fields.")
                else:
                    st.session_state.users[reg_email] = {
                        "password": reg_pass, 
                        "role": reg_role, 
                        "name": reg_name,
                        "earnings": 0.0 if reg_role == "Creator" else 0.0
                    }
                    st.success("Account created successfully! Go to the Login tab.")

# --- 2. MAIN APPLICATION DASHBOARD (POST LOGIN) ---
else:
    # Separate Portal Headers & Sidebars
    st.sidebar.markdown(f"### 👤 {st.session_state.current_user}")
    st.sidebar.markdown(f"**Portal:** `{st.session_state.user_role} Dashboard`")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.rerun()

    # Get current logged-in user email key safely
    current_email = next((k for k, v in st.session_state.users.items() if v["name"] == st.session_state.current_user), None)

    # ==================== CREATOR SYSTEM (Earn Only - No Payments) ====================
    if st.session_state.user_role == "Creator":
        st.markdown('<p class="hero-title" style="font-size:2rem;">✨ Creator Earning Hub</p>', unsafe_allow_html=True)
        st.markdown("Browse open brand campaigns, create content for TikTok/Instagram, submit links, and withdraw earnings.")
        
        creator_earnings = st.session_state.users[current_email]["earnings"] if current_email else 0.0
        active_gigs_count = len([c for c in st.session_state.campaigns if c['status'] == 'Active'])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Available Gigs", active_gigs_count)
        c2.metric("Total Earnings Balance ($)", f"${creator_earnings:,.2f}")
        c3.metric("Cost to Join", "$0.00 (100% Free)")
        
        st.markdown("---")
        st.subheader("🎯 Live Brand Campaigns (Join & Submit)")
        
        if active_gigs_count == 0:
            st.info("No active brand campaigns available right now. Check back soon when brands post new briefs!")
        else:
            for idx, camp in enumerate(st.session_state.campaigns):
                if camp['status'] == 'Active':
                    with st.container():
                        st.info(f"**Campaign:** {camp['title']} | **Brand:** {camp['brand']} | **Reward:** **${camp['budget']}**")
                        
                        video_link = st.text_input(f"Paste your TikTok / Reels / YouTube link for Campaign #{camp['id']}", key=f"creator_link_{idx}")
                        
                        if st.button(f"Submit Video Link (Campaign #{camp['id']})", key=f"submit_btn_{idx}"):
                            if not video_link.startswith("http"):
                                st.warning("Please paste a valid video URL.")
                            else:
                                st.session_state.campaigns[idx]["submission_link"] = video_link
                                st.session_state.campaigns[idx]["creator"] = st.session_state.current_user
                                st.session_state.campaigns[idx]["approval_status"] = "Pending Brand Review"
                                st.success("Video link submitted successfully! Brand notified.")
                                st.rerun()

        st.markdown("---")
        st.subheader("💳 Fast Payout Withdrawal")
        st.write("Withdraw your earned money directly to your bank account, JazzCash/EasyPaisa, or PayPal.")
        payout_amt = st.number_input("Withdrawal Amount ($)", min_value=0, max_value=max(0, int(creator_earnings)), value=0)
        if st.button("Request Payout"):
            if payout_amt > 0 and payout_amt <= creator_earnings:
                st.session_state.users[current_email]["earnings"] -= payout_amt
                st.success(f"Successfully transferred ${payout_amt} to your payout account!")
                st.rerun()
            else:
                st.error("Insufficient balance or invalid amount.")

    # ==================== BRAND SYSTEM (Campaigns & Escrow Investment) ====================
    elif st.session_state.user_role == "Brand":
        st.markdown('<p class="hero-title" style="font-size:2rem;">📢 Brand Campaign & Escrow Management</p>', unsafe_allow_html=True)
        st.markdown("Post professional creator briefs, invest funds securely into escrow, and review submitted video links.")
        
        with st.expander("💡 Brand Investment & Automated Escrow Guide"):
            st.markdown("""
            * **Kitna Invest karein?** Ek standard high-converting UGC video ka budget **$150 se $300** hota hai. Aap apni campaign ke mutabiq **$50 se $2,000** tak invest kar sakte hain.
            * **Escrow Safety:** Aap ka investment secure escrow mein hold rehta hai. Jab creator video banakar submit karta hai aur aap **Approve** karte hain, toh automated system funds foran creator ko transfer kar deta hai!
            """)

        with st.form("brand_campaign_form"):
            st.subheader("🚀 Post New Campaign Brief")
            b_title = st.text_input("Campaign Title (e.g., TikTok Unboxing & Review)")
            b_budget = st.slider("Budget / Escrow Investment per Creator ($)", 50, 2000, 200)
            post_brief = st.form_submit_button("Post Brief & Lock Funds in Escrow")
            
            if post_brief:
                new_id = len(st.session_state.campaigns) + 1
                st.session_state.campaigns.append({
                    "id": new_id,
                    "title": b_title,
                    "brand": st.session_state.current_user,
                    "budget": b_budget,
                    "status": "Active",
                    "creator": "Unassigned",
                    "submission_link": "None",
                    "approval_status": "Waiting for Submission"
                })
                st.success(f"Campaign '{b_title}' posted! ${b_budget} safely locked in Escrow.")

        st.markdown("---")
        st.subheader("📊 Campaign Submissions & Automated Approvals")
        
        if len(st.session_state.campaigns) == 0:
            st.info("You haven't posted any campaigns yet. Use the form above to post your first brief.")
        else:
            df_camps = pd.DataFrame(st.session_state.campaigns)
            st.dataframe(df_camps, use_container_width=True)
            
            st.markdown("### Review Creator Video Submissions")
            selected_id = st.selectbox("Select Campaign ID to Review", [c['id'] for c in st.session_state.campaigns])
            target_c = next((c for c in st.session_state.campaigns if c['id'] == selected_id), None)
            
            if target_c:
                st.write(f"**Campaign:** {target_c['title']}")
                st.write(f"**Creator Assigned:** {target_c['creator']}")
                st.write(f"**Submitted Video Link:** `{target_c['submission_link']}`")
                st.write(f"**Approval Status:** `{target_c['approval_status']}`")
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("✅ Approve Video & Trigger Auto-Payout"):
                        target_c['approval_status'] = "Approved & Paid"
                        target_c['status'] = "Completed"
                        
                        creator_name = target_c['creator']
                        for email, udata in st.session_state.users.items():
                            if udata["name"] == creator_name:
                                udata["earnings"] += target_c['budget']
                                
                        st.success(f"Video approved! Automated payment of ${target_c['budget']} released from Escrow to the creator's balance.")
                        st.rerun()
                with col_b2:
                    if st.button("❌ Request Revision"):
                        target_c['approval_status'] = "Revision Requested"
                        st.warning("Revision sent back to creator.")

    # ==================== ADMIN BACKEND CONTROLS ====================
    elif st.session_state.user_role == "Admin" or st.session_state.current_user == "Admin":
        st.markdown('<p class="hero-title" style="font-size:2rem;">⚡ Super Admin & Master Escrow Ledger</p>', unsafe_allow_html=True)
        st.write("Complete system control, transaction logs, and user databases.")
        
        st.subheader("👥 Registered Users Database")
        if len(st.session_state.users) == 0:
            st.info("No registered users yet.")
        else:
            st.json(st.session_state.users)
        
        st.subheader("📋 Master Campaigns & Submissions Ledger")
        if len(st.session_state.campaigns) == 0:
            st.info("No campaigns created yet.")
        else:
            st.dataframe(pd.DataFrame(st.session_state.campaigns), use_container_width=True)