import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="UGC Marketplace Pro",
    page_icon="🎬",
    layout="wide"
)

# Initialize Session State
if "users" not in st.session_state:
    st.session_state.users = {
        "creator@test.com": {"password": "123", "role": "Creator", "name": "Talal Akbar"},
        "brand@test.com": {"password": "123", "role": "Brand", "name": "Nike Marketing"}
    }
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "campaigns" not in st.session_state:
    st.session_state.campaigns = [
        {"title": "Fitness App Reel", "brand": "FitLife", "budget": 150, "status": "Active", "creator": "Unassigned", "submission_link": ""},
        {"title": "Skincare Unboxing", "brand": "GlowCo", "budget": 200, "status": "Active", "creator": "Unassigned", "submission_link": ""}
    ]
if "wallet_balance" not in st.session_state:
    st.session_state.wallet_balance = 1250.0

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.title("🎬 UGC Marketplace - Welcome")
    st.write("Please Login or Signup to access your portal.")
    
    auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Signup"])
    
    with auth_tab1:
        st.subheader("Login to your Account")
        login_email = st.text_input("Email Address", key="login_email")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            if login_email in st.session_state.users and st.session_state.users[login_email]["password"] == login_pass:
                st.session_state.logged_in = True
                st.session_state.current_user = st.session_state.users[login_email]["name"]
                st.session_state.user_role = st.session_state.users[login_email]["role"]
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid Email or Password!")
                
    with auth_tab2:
        st.subheader("Create a New Account")
        new_name = st.text_input("Full Name / Brand Name")
        new_email = st.text_input("Email Address", key="signup_email")
        new_pass = st.text_input("Password", type="password", key="signup_pass")
        new_role = st.selectbox("Select Role", ["Creator", "Brand"])
        
        if st.button("Register"):
            if new_email in st.session_state.users:
                st.warning("Email already registered! Please login.")
            elif new_email == "" or new_pass == "":
                st.error("Please fill in all fields.")
            else:
                st.session_state.users[new_email] = {"password": new_pass, "role": new_role, "name": new_name}
                st.success("Account created successfully! Please go to the Login tab.")

# --- MAIN APP ---
else:
    st.sidebar.title(f"Welcome, {st.session_state.current_user}!")
    st.sidebar.markdown(f"**Role:** `{st.session_state.user_role}`")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.rerun()

    st.sidebar.markdown("---")
    
    # 1. CREATOR PORTAL
    if st.session_state.user_role == "Creator":
        st.title("✨ Creator Dashboard")
        st.write("Manage your active gigs, submit your video links, and track earnings.")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Gigs", len([c for c in st.session_state.campaigns if c['status'] == 'Active']))
        col2.metric("Wallet Balance", f"${st.session_state.wallet_balance:,.2f}")
        col3.metric("Rating", "4.9 ⭐", "+0.2 this month")
        
        st.markdown("---")
        st.subheader("📢 Live Brand Briefs & Submission Portal")
        
        for i, camp in enumerate(st.session_state.campaigns):
            if camp['status'] == 'Active':
                with st.container():
                    st.info(f"**{camp['title']}** — Brand: *{camp['brand']}* | Budget: **${camp['budget']}**")
                    
                    # Creator can input their Google Drive / Video Link here
                    video_link = st.text_input(f"Paste your Video / Portfolio Link for '{camp['title']}'", key=f"link_{i}")
                    
                    if st.button(f"Submit Work for Campaign #{i+1}", key=f"apply_{i}"):
                        if video_link.strip() == "":
                            st.warning("Please paste a valid video link before submitting.")
                        else:
                            st.session_state.campaigns[i]['submission_link'] = video_link
                            st.session_state.campaigns[i]['creator'] = st.session_state.current_user
                            st.success(f"Work submitted successfully for '{camp['title']}'! Brand will review your link.")
        
        st.markdown("---")
        st.subheader("💳 Payout & Payment Gateway Mock")
        payout_amt = st.number_input("Withdraw Amount ($)", min_value=10, max_value=int(max(10, st.session_state.wallet_balance)), value=100)
        if st.button("Request Payout via Stripe/Bank"):
            if payout_amt <= st.session_state.wallet_balance:
                st.session_state.wallet_balance -= payout_amt
                st.success(f"Successfully transferred ${payout_amt} to your linked bank account!")
                st.rerun()

    # 2. BRAND PORTAL
    elif st.session_state.user_role == "Brand":
        st.title("📢 Brand Campaign & Submissions Portal")
        st.write("Post new creator briefs and check submitted video links from creators.")
        
        with st.form("campaign_form"):
            st.subheader("Create a New Campaign Brief")
            c_title = st.text_input("Campaign Title (e.g., TikTok Summer Promo)")
            c_budget = st.slider("Budget per Creator ($)", 50, 2000, 250)
            submit_brief = st.form_submit_button("Post Brief & Lock Escrow")
            
            if submit_brief:
                st.session_state.campaigns.append({
                    "title": c_title, 
                    "brand": st.session_state.current_user, 
                    "budget": c_budget, 
                    "status": "Active", 
                    "creator": "Unassigned",
                    "submission_link": "None"
                })
                st.success(f"Campaign '{c_title}' posted successfully with ${c_budget} locked in Escrow!")
        
        st.markdown("---")
        st.subheader("📊 Campaign Submissions & Statuses")
        df_camps = pd.DataFrame(st.session_state.campaigns)
        st.dataframe(df_camps, use_container_width=True)

    # 3. ADMIN PORTAL
    elif st.session_state.user_role == "Admin" or st.session_state.current_user == "Admin":
        st.title("⚡ Enterprise Admin Ledger & Escrow Control")
        st.write("Monitor overall platform activities and payment logs.")
        
        st.subheader("Registered Users Directory")
        users_df = pd.DataFrame([{"Email": k, "Name": v["name"], "Role": v["role"]} for k, v in st.session_state.users.items()])
        st.dataframe(users_df, use_container_width=True)
        
        st.subheader("All Platform Campaigns & Links")
        st.dataframe(pd.DataFrame(st.session_state.campaigns), use_container_width=True)