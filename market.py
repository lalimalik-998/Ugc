import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import os

# Page Configuration
st.set_page_config(
    page_title="SkillBridge Global | Professional Freelance Marketplace",
    page_icon="⚡",
    layout="wide"
)

# Ensure uploads directory exists for gig images
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# --- PASSWORD HASHING ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- DATABASE SETUP ---
def get_connection():
    conn = sqlite3.connect("global_marketplace.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        name TEXT,
        wallet REAL,
        payout_info TEXT
    )''')
    
    # Gigs Table (Added image_path column)
    cursor.execute('''CREATE TABLE IF NOT EXISTS gigs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_email TEXT,
        worker_name TEXT,
        title TEXT,
        category TEXT,
        price REAL,
        description TEXT,
        delivery_days INTEGER,
        image_path TEXT,
        is_featured INTEGER DEFAULT 0
    )''')
    
    # Orders Table (Fiverr Style Tracking)
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gig_id INTEGER,
        client_name TEXT,
        worker_name TEXT,
        title TEXT,
        price REAL,
        admin_commission REAL,
        worker_payout REAL,
        status TEXT,
        requirements TEXT,
        delivery_proof TEXT
    )''')
    
    conn.commit()
    
    # Default Admin
    cursor.execute("SELECT * FROM users WHERE role = 'Admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                       ("admin@skillbridge.com", hash_password("admin123"), "Admin", "Platform Admin", 0.0, "Master Ledger"))
        conn.commit()
    conn.close()

init_db()

# --- CUSTOM CSS STYLING (Fiverr Look & Feel) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f7f7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .fiverr-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e4e5e7;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .hero-banner {
        background: linear-gradient(135deg, #0b7053 0%, #003912 100%);
        padding: 40px;
        border-radius: 10px;
        color: white;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Persistence Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "admin_commission_rate" not in st.session_state:
    st.session_state.admin_commission_rate = 0.15

# ==================== AUTHENTICATION / LOGIN PAGE ====================
if not st.session_state.logged_in:
    st.markdown("""
        <div class="hero-banner" style="text-align: center;">
            <h1>Find the perfect freelance services for your business</h1>
            <p>Connect with global & Pakistani talent, earn in dollars securely with automated escrow.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Join SkillBridge"])
        
        with tab1:
            l_email = st.text_input("Email", key="l_email")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("Continue", use_container_width=True):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (l_email, hash_password(l_pass)))
                user = cursor.fetchone()
                conn.close()
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_email = user[0]
                    st.session_state.user_role = user[2]
                    st.session_state.current_user = user[3]
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
                    
        with tab2:
            r_name = st.text_input("Full Name", key="r_name")
            r_email = st.text_input("Email", key="r_email_reg")
            r_pass = st.text_input("Password", type="password", key="r_pass_reg")
            r_role = st.selectbox("I want to:", ["Hire Freelancers (Client)", "Sell Services (Freelancer)"])
            
            if st.button("Register Now", use_container_width=True):
                role_mapped = "Global Client" if "Client" in r_role else "Worker / Freelancer"
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (r_email,))
                if cursor.fetchone():
                    st.warning("Email already registered.")
                elif not r_name or not r_email or not r_pass:
                    st.error("Fill out all fields.")
                else:
                    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                                   (r_email, hash_password(r_pass), role_mapped, r_name, 0.0, "Not Set"))
                    conn.commit()
                    conn.close()
                    
                    # Auto login upon registration and direct access to dashboard
                    st.session_state.logged_in = True
                    st.session_state.user_email = r_email
                    st.session_state.user_role = role_mapped
                    st.session_state.current_user = r_name
                    st.success("Account created successfully! Redirecting to dashboard...")
                    st.rerun()

# ==================== MAIN PLATFORM DASHBOARD ====================
else:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (st.session_state.user_email,))
    user_data = cursor.fetchone()
    conn.close()
    
    # Sidebar Navigation
    st.sidebar.markdown(f"### 👤 {st.session_state.current_user}")
    st.sidebar.markdown(f"**Role:** `{st.session_state.user_role}`")
    st.sidebar.markdown(f"💰 **Wallet:** `${user_data[4]:,.2f}`")
    st.sidebar.markdown("---")
    
    menu = []
    if st.session_state.user_role == "Global Client":
        menu = ["🔍 Explore Gigs", "🛒 My Orders", "💳 Billing & Payments"]
    elif st.session_state.user_role == "Worker / Freelancer":
        menu = ["📊 Dashboard", "➕ Create Gig", "💼 Manage Orders", "🏦 Payout Settings"]
    elif st.session_state.user_role == "Admin":
        menu = ["⚡ Admin Revenue Panel", "👥 Manage Users", "📋 Master Ledger"]
        
    choice = st.sidebar.radio("Navigation Menu", menu)
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.session_state.user_email = None
        st.rerun()

    # ==================== CLIENT: EXPLORE GIGS ====================
    if choice == "🔍 Explore Gigs":
        st.markdown("<h2>Explore Professional Gigs</h2>", unsafe_allow_html=True)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gigs")
        gigs = cursor.fetchall()
        conn.close()
        
        if not gigs:
            st.info("No gigs available right now.")
        else:
            for g in gigs:
                g_id, w_email, w_name, title, cat, price, desc, days, img_path, feat = g
                
                with st.container():
                    st.markdown('<div class="fiverr-card">', unsafe_allow_html=True)
                    cols = st.columns([1, 2])
                    
                    with cols[0]:
                        if img_path and os.path.exists(img_path):
                            st.image(img_path, use_column_width=True)
                        else:
                            st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=500&q=80", use_column_width=True)
                            
                    with cols[1]:
                        st.markdown(f"### {title}")
                        st.markdown(f"**Category:** `{cat}` | **Seller:** `{w_name}` | ⏱️ **Delivery:** `{days} Days`")
                        st.markdown(f"{desc}")
                        st.markdown(f"#### Starting at: `${price} USD`")
                        
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    reqs = st.text_area(f"Project Requirements for Gig #{g_id}", placeholder="Describe what you want...", key=f"req_{g_id}")
                    if st.button(f"Order Now (${price})", key=f"buy_{g_id}"):
                        admin_cut = price * st.session_state.admin_commission_rate
                        worker_cut = price - admin_cut
                        
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO orders (gig_id, client_name, worker_name, title, price, admin_commission, worker_payout, status, requirements, delivery_proof) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                     (g_id, st.session_state.current_user, w_name, title, price, admin_cut, worker_cut, "In Progress", reqs, "Pending Delivery"))
                        cursor.execute("UPDATE users SET wallet = wallet + ? WHERE role = 'Admin'", (admin_cut,))
                        conn.commit()
                        conn.close()
                        st.success("Order placed successfully! Funds are secured in Escrow.")
                        st.rerun()

    # ==================== CLIENT: MY ORDERS ====================
    elif choice == "🛒 My Orders":
        st.markdown("<h2>My Placed Orders (Escrow Protected)</h2>", unsafe_allow_html=True)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE client_name = ?", (st.session_state.current_user,))
        orders = cursor.fetchall()
        conn.close()
        
        if not orders:
            st.info("You haven't placed any orders yet.")
        else:
            for o in orders:
                o_id, g_id, client, worker, title, price, comm, payout, status, reqs, proof = o
                st.markdown(f"""
                <div class="fiverr-card">
                    <h4>Order #{o_id}: {title}</h4>
                    <p><b>Freelancer:</b> {worker} | <b>Price:</b> ${price} | <b>Status:</b> <code>{status}</code></p>
                    <p><b>Your Requirements:</b> {reqs}</p>
                    <p><b>Delivery Proof:</b> {proof}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if status == "Delivered":
                    if st.button(f"✅ Accept Delivery & Release Funds for Order #{o_id}", key=f"accept_{o_id}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE orders SET status = 'Completed' WHERE id = ?", (o_id,))
                        cursor.execute("UPDATE users SET wallet = wallet + ? WHERE name = ?", (payout, worker))
                        conn.commit()
                        conn.close()
                        st.success("Order completed! Funds released to worker.")
                        st.rerun()

    # ==================== WORKER: DASHBOARD & ORDERS ====================
    elif choice == "📊 Dashboard" or choice == "💼 Manage Orders":
        st.markdown("<h2>Freelancer Command Center</h2>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.metric("Available Earnings", f"${user_data[4]:,.2f}")
        c2.metric("Active Escrow Orders", len([o for o in sqlite3.connect("global_marketplace.db").cursor().execute("SELECT * FROM orders WHERE worker_name = ? AND status = 'In Progress'", (st.session_state.current_user,)).fetchall()]))
        
        st.markdown("---")
        st.subheader("Client Orders Assigned To You")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE worker_name = ?", (st.session_state.current_user,))
        my_orders = cursor.fetchall()
        conn.close()
        
        if not my_orders:
            st.info("No active orders found.")
        else:
            for o in my_orders:
                o_id, g_id, client, worker, title, price, comm, payout, status, reqs, proof = o
                st.markdown(f"""
                <div class="fiverr-card">
                    <h4>Order #{o_id}: {title}</h4>
                    <p><b>Client:</b> {client} | <b>Total:</b> ${price} | <b>Your Payout (85%):</b> <b>${payout}</b> | <b>Status:</b> <code>{status}</code></p>
                    <p><b>Requirements:</b> {reqs}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if status == "In Progress":
                    delivery_text = st.text_input(f"Submit work link/message for Order #{o_id}", key=f"del_{o_id}")
                    if st.button(f"Deliver Order #{o_id}", key=f"btn_del_{o_id}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE orders SET status = 'Delivered', delivery_proof = ? WHERE id = ?", (delivery_text, o_id))
                        conn.commit()
                        conn.close()
                        st.success("Work delivered to client for review!")
                        st.rerun()

    # ==================== WORKER: CREATE GIG ====================
    elif choice == "➕ Create Gig":
        st.markdown("<h2>Create a New Gig Service</h2>", unsafe_allow_html=True)
        
        title = st.text_input("I will do...")
        cat = st.selectbox("Category", ["Video Editing", "Graphic Design", "Web Development", "Content Writing"])
        price = st.number_input("Price ($ USD)", min_value=5.0, value=25.0)
        days = st.number_input("Delivery Time (Days)", min_value=1, value=3)
        desc = st.text_area("Gig Description")
        uploaded_file = st.file_uploader("Upload Gig Cover Image / Thumbnail", type=["jpg", "jpeg", "png"])
        
        if st.button("Publish Gig", use_container_width=True):
            image_path = ""
            if uploaded_file is not None:
                image_path = os.path.join("uploads", uploaded_file.name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            if not title or not desc:
                st.error("Please fill out the title and description.")
            else:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO gigs (worker_email, worker_name, title, category, price, description, delivery_days, image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (st.session_state.user_email, st.session_state.current_user, title, cat, price, desc, days, image_path))
                conn.commit()
                conn.close()
                st.success("Gig successfully published with image!")

    # ==================== WORKER: PAYOUT SETTINGS ====================
    elif choice == "🏦 Payout Settings":
        st.markdown("<h2>Payout Accounts (Local & International)</h2>", unsafe_allow_html=True)
        st.write("Configure your preferred withdrawal method for your earnings.")
        
        existing_info = user_data[5] if user_data[5] else "Not Set"
        
        with st.form("payout_form"):
            method = st.selectbox("Select Payout Method", ["JazzCash", "EasyPaisa", "Bank Account (IBAN)", "PayPal"])
            account_holder = st.text_input("Account Holder Name", placeholder="e.g. Muhammad Talal")
            account_number = st.text_input("Account / Phone / IBAN Number", placeholder="e.g. 03001234567 or PK00XXXX...")
            
            submitted = st.form_submit_button("Save Payout Destination")
            if submitted:
                if not account_holder or not account_number:
                    st.error("Please fill in all payment details.")
                else:
                    formatted_payout = f"Method: {method} | Holder: {account_holder} | Account/IBAN: {account_number}"
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET payout_info = ? WHERE email = ?", (formatted_payout, st.session_state.user_email))
                    conn.commit()
                    conn.close()
                    st.success("Payout details updated successfully!")
        
        st.markdown("---")
        st.info(f"**Current Saved Payout Info:** `{existing_info}`")

    # ==================== ADMIN PANEL ====================
    elif choice == "⚡ Admin Revenue Panel":
        st.markdown("<h2>Super Admin Revenue Dashboard</h2>", unsafe_allow_html=True)
        conn = get_connection()
        cursor = conn.cursor()
        admin_bal = cursor.execute("SELECT wallet FROM users WHERE role = 'Admin'").fetchone()[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Admin Revenue Earned", f"${admin_bal:,.2f}")
        c2.metric("Commission Rate", f"{int(st.session_state.admin_commission_rate * 100)}%")
        c3.metric("Total Users", cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0])
        
        st.markdown("---")
        with st.form("admin_conf"):
            new_com = st.slider("Commission Percentage (%)", 5, 30, int(st.session_state.admin_commission_rate * 100))
            if st.form_submit_button("Update Commission"):
                st.session_state.admin_commission_rate = new_com / 100.0
                st.success(f"Commission updated to {new_com}%!")
        
        st.subheader("Platform Master Orders Ledger")
        orders_df = pd.read_sql("SELECT * FROM orders", conn)
        st.dataframe(orders_df, use_container_width=True)
        conn.close()

    elif choice == "👥 Manage Users":
        st.markdown("<h2>All Platform Users</h2>", unsafe_allow_html=True)
        conn = get_connection()
        users_df = pd.read_sql("SELECT email, role, name, wallet, payout_info FROM users", conn)
        st.dataframe(users_df, use_container_width=True)
        conn.close()
        
    elif choice == "📋 Master Ledger":
        st.markdown("<h2>Financial Master Ledger</h2>", unsafe_allow_html=True)
        conn = get_connection()
        ledger_df = pd.read_sql("SELECT * FROM orders", conn)
        st.dataframe(ledger_df, use_container_width=True)
        conn.close()