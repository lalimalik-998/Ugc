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

# Ensure uploads directory exists
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
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_v3 (
        email TEXT PRIMARY KEY,
        password TEXT,
        role TEXT,
        name TEXT,
        phone TEXT,
        country TEXT,
        bio TEXT,
        avatar_path TEXT,
        wallet REAL,
        payout_info TEXT
    )''')
    
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
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    
    # Custom Super Admin Setup
    cursor.execute("SELECT * FROM users_v3 WHERE email = 'admin@skillbridge.com'")
    if not cursor.fetchone():
        cursor.execute("INSERT OR REPLACE INTO users_v3 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                       ("admin@skillbridge.com", hash_password("admin123"), "Admin", "Platform Admin", "+1234567890", "Global", "System Administrator", "", 0.0, "Master Ledger"))
        conn.commit()
    conn.close()

init_db()

# --- ADVANCED CUSTOM CSS FOR FIVERR LOOK ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f8;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #0b221e;
        color: white;
    }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15);
    }
    .fiverr-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e4e5e7;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .fiverr-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 112, 83, 0.1);
        border-color: #0b7053;
    }
    .hero-banner {
        background: linear-gradient(135deg, #0b7053 0%, #013b28 100%);
        padding: 50px;
        border-radius: 16px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(11, 112, 83, 0.2);
        text-align: center;
    }
    .stButton>button {
        background-color: #0b7053;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background-color: #095c43;
        color: white;
    }
    .chat-bubble-sent {
        background-color: #0b7053;
        color: white;
        padding: 12px 18px;
        border-radius: 14px 14px 0px 14px;
        margin: 8px 0;
        max-width: 70%;
        float: right;
        clear: both;
    }
    .chat-bubble-recv {
        background-color: #ffffff;
        color: #1e293b;
        padding: 12px 18px;
        border-radius: 14px 14px 14px 0px;
        margin: 8px 0;
        max-width: 70%;
        float: left;
        clear: both;
        border: 1px solid #e2e8f0;
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
if "chat_target" not in st.session_state:
    st.session_state.chat_target = None
if "active_nav" not in st.session_state:
    st.session_state.active_nav = None

# ==================== AUTHENTICATION / LOGIN PAGE ====================
if not st.session_state.logged_in:
    st.markdown("""
        <div class="hero-banner">
            <h1>⚡ SkillBridge Global Marketplace</h1>
            <p style="font-size: 18px; opacity: 0.9; margin-top: 10px;">Hire top global & Pakistani freelancers or sell your skills securely with escrow protection.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Quick Signup"])
        
        with tab1:
            l_email = st.text_input("Email Address", key="l_email")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("Sign In to Account", use_container_width=True):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users_v3 WHERE email = ? AND password = ?", (l_email, hash_password(l_pass)))
                user = cursor.fetchone()
                conn.close()
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_email = user[0]
                    st.session_state.user_role = user[2]
                    st.session_state.current_user = user[3]
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
                    
        with tab2:
            r_name = st.text_input("Full Name", key="r_name")
            r_email = st.text_input("Email Address", key="r_email_reg")
            r_pass = st.text_input("Password", type="password", key="r_pass_reg")
            
            c_col1, c_col2 = st.columns([1, 2])
            with c_col1:
                r_country = st.selectbox("Country", ["🇵🇰 Pakistan (+92)", "🇺🇸 USA (+1)", "🇬🇧 UK (+44)", "🇦🇪 UAE (+971)", "🇸🇦 KSA (+966)", "🌍 Other"])
            with c_col2:
                r_phone = st.text_input("Phone Number", placeholder="3001234567")
                
            r_role = st.selectbox("I want to join as:", ["Hire Freelancers (Client)", "Sell Services (Freelancer)"])
            
            if st.button("Create Account", use_container_width=True):
                role_mapped = "Global Client" if "Client" in r_role else "Worker / Freelancer"
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users_v3 WHERE email = ?", (r_email,))
                if cursor.fetchone():
                    st.warning("This email is already registered.")
                elif not r_name or not r_email or not r_pass or not r_phone:
                    st.error("Please fill out all required fields.")
                else:
                    full_phone = f"{r_country.split(' ')[0]} {r_phone}"
                    cursor.execute("INSERT INTO users_v3 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                   (r_email, hash_password(r_pass), role_mapped, r_name, full_phone, r_country, "Hi there! I'm using SkillBridge.", "", 0.0, "Not Set"))
                    conn.commit()
                    conn.close()
                    
                    st.session_state.logged_in = True
                    st.session_state.user_email = r_email
                    st.session_state.user_role = role_mapped
                    st.session_state.current_user = r_name
                    st.success("Account created successfully!")
                    st.rerun()

# ==================== MAIN PLATFORM DASHBOARD ====================
else:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_v3 WHERE email = ?", (st.session_state.user_email,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        st.session_state.logged_in = False
        st.rerun()
        
    # Sidebar Navigation Profile Info
    st.sidebar.markdown(f"### 👤 {st.session_state.current_user}")
    st.sidebar.markdown(f"**Role:** `{user_data[2]}`")
    st.sidebar.markdown(f"📍 **Location:** `{user_data[5]}`")
    st.sidebar.markdown(f"📞 **Phone:** `{user_data[4]}`")
    st.sidebar.markdown(f"💰 **Wallet:** `${user_data[8]:,.2f}`")
    st.sidebar.markdown("---")
    
    menu = []
    if user_data[2] == "Global Client":
        menu = ["🔍 Explore Gigs", "💬 Messages / Inbox", "🛒 My Orders", "👤 Edit Profile", "💳 Billing & Payments"]
    elif user_data[2] == "Worker / Freelancer":
        menu = ["📊 Dashboard", "➕ Create Gig", "💬 Messages / Inbox", "💼 Manage Orders", "👤 Edit Profile", "🏦 Payout Settings"]
    elif user_data[2] == "Admin":
        menu = ["⚡ Admin Revenue Panel", "👥 Manage Users", "📋 Master Ledger"]
        
    # Default selection handling if redirected via button
    default_choice_idx = 0
    if st.session_state.active_nav in menu:
        default_choice_idx = menu.index(st.session_state.active_nav)
        st.session_state.active_nav = None # Reset after applying
        
    choice = st.sidebar.radio("Navigation Menu", menu, index=default_choice_idx)
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
            st.info("No gigs published yet.")
        else:
            for g in gigs:
                g_id, w_email, w_name, title, cat, price, desc, days, img_path, feat = g
                
                with st.container():
                    st.markdown('<div class="fiverr-card">', unsafe_allow_html=True)
                    cols = st.columns([1, 2])
                    
                    with cols[0]:
                        if img_path and os.path.exists(img_path):
                            st.image(img_path, use_container_width=True)
                        else:
                            st.image("https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=500&q=80", use_container_width=True)
                            
                    with cols[1]:
                        st.markdown(f"### {title}")
                        st.markdown(f"**Category:** `{cat}` | **Seller:** `{w_name}` | ⏱️ **Delivery:** `{days} Days`")
                        st.markdown(f"{desc}")
                        st.markdown(f"#### Starting at: `${price} USD`")
                        
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    reqs = st.text_area(f"Project Requirements for Gig #{g_id}", placeholder="Describe what you want...", key=f"req_{g_id}")
                    col_b1, col_b2 = st.columns([1, 1])
                    with col_b1:
                        if st.button(f"Order Now (${price})", key=f"buy_{g_id}"):
                            admin_cut = price * st.session_state.admin_commission_rate
                            worker_cut = price - admin_cut
                            
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO orders (gig_id, client_name, worker_name, title, price, admin_commission, worker_payout, status, requirements, delivery_proof) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                         (g_id, st.session_state.current_user, w_name, title, price, admin_cut, worker_cut, "In Progress", reqs, "Pending Delivery"))
                            cursor.execute("UPDATE users_v3 SET wallet = wallet + ? WHERE role = 'Admin'", (admin_cut,))
                            
                            auto_msg = f"Hello! I just ordered your gig: '{title}' (${price}). Requirements: {reqs}"
                            cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                                         (st.session_state.current_user, w_name, auto_msg))
                            
                            conn.commit()
                            conn.close()
                            
                            st.session_state.chat_target = w_name
                            st.session_state.active_nav = "💬 Messages / Inbox"
                            st.success("Order placed successfully! Redirecting to chat with seller...")
                            st.rerun()
                            
                    with col_b2:
                        if st.button(f"💬 Chat with {w_name}", key=f"chat_seller_{g_id}"):
                            st.session_state.chat_target = w_name
                            
                            # Send initial gig reference message automatically
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                                         (st.session_state.current_user, w_name, f"Hi, I'm interested in your gig: '{title}' (${price})"))
                            conn.commit()
                            conn.close()
                            
                            st.session_state.active_nav = "💬 Messages / Inbox"
                            st.success(f"Opening direct chat with {w_name}...")
                            st.rerun()

    # ==================== EDIT PROFILE (PHOTO & BIO) ====================
    elif choice == "👤 Edit Profile":
        st.markdown("<h2>Manage Your Profile</h2>", unsafe_allow_html=True)
        st.write("Aap jab chahein apni profile photo aur bio update kar sakte hain.")
        
        current_bio = user_data[6] if user_data[6] else ""
        current_avatar = user_data[7] if user_data[7] else ""
        
        if current_avatar and os.path.exists(current_avatar):
            st.image(current_avatar, width=150)
            
        with st.form("profile_edit_form"):
            new_bio = st.text_area("Professional Bio / Description", value=current_bio, placeholder="Tell clients or freelancers about yourself...")
            new_avatar_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            
            update_btn = st.form_submit_button("Save Profile Changes")
            if update_btn:
                avatar_path = current_avatar
                if new_avatar_file is not None:
                    avatar_path = os.path.join("uploads", f"avatar_{st.session_state.user_email.replace('@','_')}.png")
                    with open(avatar_path, "wb") as f:
                        f.write(new_avatar_file.getbuffer())
                
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users_v3 SET bio = ?, avatar_path = ? WHERE email = ?", (new_bio, avatar_path, st.session_state.user_email))
                conn.commit()
                conn.close()
                st.success("Profile updated successfully!")
                st.rerun()

    # ==================== CHAT & MESSAGING SYSTEM ====================
    elif choice == "💬 Messages / Inbox":
        st.markdown("<h2>Fiverr-Style Direct Inbox & Deal Chat</h2>", unsafe_allow_html=True)
        
        conn = get_connection()
        cursor = conn.cursor()
        # Strictly exclude Platform Admin from standard user list
        cursor.execute("SELECT name FROM users_v3 WHERE name != ? AND role != 'Admin'", (st.session_state.current_user,))
        all_users = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT worker_name FROM gigs WHERE worker_name != ? AND worker_name != 'Platform Admin'", (st.session_state.current_user,))
        gig_workers = [row[0] for row in cursor.fetchall()]
        
        combined_users = list(set(all_users + gig_workers))
        conn.close()
        
        if not combined_users:
            st.info("No other freelancers or clients available to chat with yet.")
        else:
            default_index = 0
            if st.session_state.chat_target in combined_users:
                default_index = combined_users.index(st.session_state.chat_target)
                
            selected_chat_user = st.selectbox("Select User to Chat With", combined_users, index=default_index)
            st.session_state.chat_target = selected_chat_user
            
            st.markdown("---")
            st.subheader(f"Conversation with {selected_chat_user}")
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sender, message, timestamp FROM messages 
                WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
                ORDER BY timestamp ASC
            """, (st.session_state.current_user, selected_chat_user, selected_chat_user, st.session_state.current_user))
            messages = cursor.fetchall()
            conn.close()
            
            chat_container = st.container()
            with chat_container:
                if not messages:
                    st.info(f"No messages yet with {selected_chat_user}. Start the conversation below!")
                else:
                    for sender, msg, time in messages:
                        if sender == st.session_state.current_user:
                            st.markdown(f"""
                            <div style="overflow: auto; margin-bottom: 10px;">
                                <div class="chat-bubble-sent"><b>You:</b> {msg}<br><span style="font-size: 10px; opacity: 0.7;">{time}</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="overflow: auto; margin-bottom: 10px;">
                                <div class="chat-bubble-recv"><b>{sender}:</b> {msg}<br><span style="font-size: 10px; opacity: 0.7;">{time}</span></div>
                            </div>
                            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("chat_form", clear_on_submit=True):
                new_msg = st.text_input("Type message...", placeholder="Discuss project details or custom budget...")
                send_btn = st.form_submit_button("Send Message 🚀")
                if send_btn:
                    if new_msg.strip():
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)",
                                     (st.session_state.current_user, selected_chat_user, new_msg))
                        conn.commit()
                        conn.close()
                        st.rerun()
                    else:
                        st.warning("Message cannot be blank.")

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
                
                col_o1, col_o2 = st.columns([1, 1])
                with col_o1:
                    if st.button(f"💬 Chat with Seller ({worker})", key=f"order_chat_{o_id}"):
                        st.session_state.chat_target = worker
                        st.session_state.active_nav = "💬 Messages / Inbox"
                        st.success(f"Redirecting to chat with {worker}...")
                        st.rerun()
                with col_o2:
                    if status == "Delivered":
                        if st.button(f"✅ Accept Delivery & Release Funds", key=f"accept_{o_id}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE orders SET status = 'Completed' WHERE id = ?", (o_id,))
                            cursor.execute("UPDATE users_v3 SET wallet = wallet + ? WHERE name = ?", (payout, worker))
                            conn.commit()
                            conn.close()
                            st.success("Order completed! Funds released to worker.")
                            st.rerun()

    # ==================== WORKER: DASHBOARD & ORDERS ====================
    elif choice == "📊 Dashboard" or choice == "💼 Manage Orders":
        st.markdown("<h2>Freelancer Command Center</h2>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.metric("Available Earnings", f"${user_data[8]:,.2f}")
        
        conn = get_connection()
        cursor = conn.cursor()
        active_count = len(cursor.execute("SELECT * FROM orders WHERE worker_name = ? AND status = 'In Progress'", (st.session_state.current_user,)).fetchall())
        conn.close()
        c2.metric("Active Escrow Orders", active_count)
        
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
                    <p><b>Client:</b> {client} | <b>Total:</b> ${price} | <b>Your Payout:</b> <b>${payout}</b> | <b>Status:</b> <code>{status}</code></p>
                    <p><b>Requirements:</b> {reqs}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"💬 Chat with Client ({client})", key=f"worker_chat_{o_id}"):
                    st.session_state.chat_target = client
                    st.session_state.active_nav = "💬 Messages / Inbox"
                    st.success(f"Redirecting to chat with {client}...")
                    st.rerun()
                
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
                st.success("Gig successfully published!")

    # ==================== WORKER: PAYOUT SETTINGS ====================
    elif choice == "🏦 Payout Settings":
        st.markdown("<h2>Payout Accounts (Local & International)</h2>", unsafe_allow_html=True)
        st.write("Configure your preferred withdrawal method for your earnings.")
        
        existing_info = user_data[9] if user_data[9] else "Not Set"
        
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
                    cursor.execute("UPDATE users_v3 SET payout_info = ? WHERE email = ?", (formatted_payout, st.session_state.user_email))
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
        admin_bal = cursor.execute("SELECT wallet FROM users_v3 WHERE role = 'Admin'").fetchone()[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Admin Revenue Earned", f"${admin_bal:,.2f}")
        c2.metric("Commission Rate", f"{int(st.session_state.admin_commission_rate * 100)}%")
        c3.metric("Total Users", cursor.execute("SELECT COUNT(*) FROM users_v3").fetchone()[0])
        
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
        users_df = pd.read_sql("SELECT email, role, name, phone, country, wallet FROM users_v3", conn)
        st.dataframe(users_df, use_container_width=True)
        conn.close()
        
    elif choice == "📋 Master Ledger":
        st.markdown("<h2>Financial Master Ledger</h2>", unsafe_allow_html=True)
        conn = get_connection()
        ledger_df = pd.read_sql("SELECT * FROM orders", conn)
        st.dataframe(ledger_df, use_container_width=True)
        conn.close()