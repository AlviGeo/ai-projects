import streamlit as st
import sqlite3
from datetime import datetime
import requests
import re

st.set_page_config(page_title="Find Your Dream Travel Destination", page_icon="🤖", layout="centered")

DB_PATH = "chat_history.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS chat_rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    room_name TEXT NOT NULL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    room_id INTEGER,
    model TEXT,
    message TEXT,
    response TEXT,
    timestamp TEXT
)''')
conn.commit()

def register_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty."
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', password):
        return False, "Password must have at least 1 uppercase, 1 lowercase, 1 number, and not empty."
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True, "Registered successfully."
    except sqlite3.IntegrityError:
        return False, "Username already taken."
    
def login_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty."
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if c.fetchone():
        return True, "Login successful."
    else:
        return False, "Invalid credentials."

def create_room(username, room_name):
    c.execute("INSERT INTO chat_rooms (username, room_name) VALUES (?, ?)", (username, room_name))
    conn.commit()
    return c.lastrowid

def room_exists(username, room_name):
    c.execute("SELECT 1 FROM chat_rooms WHERE username = ? AND room_name = ?", (username, room_name.strip()))
    return c.fetchone() is not None

def get_rooms(username):
    c.execute("SELECT id, room_name FROM chat_rooms WHERE username=?", (username,))
    return c.fetchall()

def delete_room(room_id):
    c.execute("DELETE FROM chat_rooms WHERE id=?", (room_id,))
    c.execute("DELETE FROM chats WHERE room_id=?", (room_id,))
    conn.commit()

def store_chat(username, room_id, model, message, response):
    c.execute("INSERT INTO chats (username, room_id, model, message, response, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (username, room_id, model, message, response, datetime.now().isoformat()))
    conn.commit()

def get_chat_history(username, room_id):
    c.execute("SELECT model, message, response, timestamp FROM chats WHERE username=? AND room_id=? ORDER BY id ASC", (username, room_id))
    return c.fetchall()

def clear_chat_history(username, room_id):
    c.execute("DELETE FROM chats WHERE username=? AND room_id=?", (username, room_id))
    conn.commit()

def init_session():
    # Login and auth state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # App settings and UI state
    defaults = {
        "show_password": False,
        "api_key": "",
        "theme": "Light",
        "current_model": "mistralai/mistral-7b-instruct",
        "room_id": None,
        "room_name": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def auth_form():
    st.title("🔐 Login or Register")
    auth_mode = st.radio("Choose mode", ["Login", "Register"])
    username = st.text_input("Username", key="auth_username_input")
    password = st.text_input("Password", key="password_input", type="password" if not st.session_state.show_password else "default")
    

    if auth_mode == "Register":
        if st.button("Register"):
            valid, msg = register_user(username, password)
            if valid:
                st.success(msg + " Please login.")
            else:
                st.error(msg)
    else:
        if st.button("Login"):
            valid, msg = login_user(username, password)
            if valid:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error(msg)

def sidebar():
    st.sidebar.title("💬 Chat Rooms")
    rooms = get_rooms(st.session_state.username)
    room_names = [r[1] for r in rooms]
    room_ids = [r[0] for r in rooms]
    if rooms:
        selected = st.sidebar.radio("Select Room", room_names, index=room_names.index(st.session_state.room_name) if st.session_state.room_name in room_names else 0)
        st.session_state.room_name = selected
        st.session_state.room_id = room_ids[room_names.index(selected)]
        if st.sidebar.button("Delete Room", key="delete_room"):
            delete_room(st.session_state.room_id)
            st.session_state.room_id = None
            st.session_state.room_name = ""
            st.rerun()
    else:
        st.sidebar.info("No chat rooms. Create one!")
        st.session_state.room_id = None
        st.session_state.room_name = ""
    new_room = st.sidebar.text_input("New Room Name", key="new_room")
    
    if st.sidebar.button("Create Room"):
        if not new_room.strip():
            st.sidebar.error("Room name cannot be empty.")
        elif room_exists(st.session_state.username, new_room):
            st.sidebar.error("Room name already exists under your account. Choose another.")
        else:
            room_id = create_room(st.session_state.username, new_room.strip())
            st.session_state.room_id = room_id
            st.session_state.room_name = new_room.strip()
            st.rerun()
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.api_key = ""
        st.session_state.room_id = None
        st.session_state.room_name = ""
        st.rerun()

def chatbot_ui():
    st.title(f"🤖 AI Chatbot - {st.session_state.room_name}")
    st.caption(f"Logged in as: {st.session_state.username}")
    
    # Fetch chat history for this room
    chat_history = get_chat_history(st.session_state.username, st.session_state.room_id)

    # Ask for API Key if not already stored and no chat history
    if not st.session_state.get("api_key"):
        api_key = st.text_input("🔑 Enter OpenRouter API Key", type="password")
        if api_key:
            if len(api_key) < 40:
                st.warning("API key is too short. Please enter a valid OpenRouter API key.")
                st.stop()
            st.session_state.api_key = api_key
            st.rerun()
        else:
            st.warning("Enter your API key to start chatting.")
            st.stop()

    # Ask for model selection
    model_options = {
        "Mistral 7B": "mistralai/mistral-7b-instruct",
        "Llama 2 70B": "meta-llama/llama-3.3-70b-instruct",
        "GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
        "Mixtral 8x7B": "mistralai/mixtral-8x7b-instruct"
    }
    # 2. Set default model in session state if not already set
    if "current_model" not in st.session_state:
        st.session_state.current_model = model_options["Mistral 7B"]

    # 3. Reverse lookup to get current model name
    reverse_model_options = {v: k for k, v in model_options.items()}
    current_model_name = reverse_model_options.get(st.session_state.current_model, "Mistral 7B")

    # 4. Show dropdown and store result temporarily
    model_name = st.selectbox("Choose a model", list(model_options.keys()), index=list(model_options.keys()).index(current_model_name))

    # 5. If changed, update session state and force rerun
    selected_model = model_options[model_name]
    if st.session_state.current_model != selected_model:
        st.session_state.current_model = selected_model
        st.rerun()
    model = st.session_state.current_model

    # Chat bubbles
    st.markdown("<div style='height:100%;overflow-y:auto;'>", unsafe_allow_html=True)
    for i, (model, user_msg, ai_msg, ts) in enumerate(chat_history):
        try:
            formatted_ts = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_ts = ts[:19]
        
        # User bubble
        st.markdown(f"""
        <div style='display:flex;justify-content:flex-end;margin-bottom:6px;'>
        <div style='background-color:#DCF8C6;border-radius:15px;padding:10px 15px;max-width:70%;box-shadow:0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size:0.75em;color:#666;text-align:right;'>👩🏻‍💻 {formatted_ts}</div>
            <div style='font-size:1em;'>{user_msg}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AI bubble
        st.markdown(f"""
        <div style='display:flex;justify-content:flex-start;margin-bottom:16px;'>
        <div style='background-color:#F1F0F0;border-radius:15px;padding:10px 15px;max-width:70%;box-shadow:0 1px 3px rgba(0,0,0,0.1);'>
            <div style='font-size:0.75em;color:#666;'>🧠 {model_name} &nbsp;•&nbsp; {formatted_ts}</div>
            <div style='font-size:1em;'>{ai_msg}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


    prompt = st.chat_input("Type your message...")
    if chat_history and any(msg[1].strip() for msg in chat_history):
        clear_clicked = st.button("Clear Room Chat", use_container_width=True, type="primary")
        if clear_clicked:
            clear_chat_history(st.session_state.username, st.session_state.room_id)
            st.rerun()

    # Handle sending the message
    if prompt and prompt.strip():
        messages = [{"role": "user", "content": prompt.strip()}]
        headers = {
            "Authorization": f"Bearer {st.session_state.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        with st.spinner("Generating response..."):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                if response.status_code == 200:
                    response_data = response.json()
                    ai_response = response_data["choices"][0]["message"]["content"]
                else:
                    ai_response = f"[Error {response.status_code}] {response.text}"
            except Exception as e:
                ai_response = f"[Exception] {str(e)}"
        store_chat(st.session_state.username, st.session_state.room_id, model, prompt.strip(), ai_response)
        st.rerun()

init_session()
if st.session_state.get("logged_in"):
    sidebar()
    if st.session_state.get("room_id"):
        chatbot_ui()
    else:
        st.info("Please create or select a chat room from the sidebar.")
else:
    auth_form()