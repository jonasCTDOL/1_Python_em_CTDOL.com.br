import streamlit as st
import time
import os
import sqlite3

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'username' not in st.session_state:
    st.session_state.username = None

# Database setup
DATABASE = 'chat_history.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_message(username, message):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))
    conn.commit()
    conn.close()

def get_messages():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT username, message FROM messages ORDER BY timestamp')
    messages = cursor.fetchall()
    conn.close()
    return [{'username': row[0], 'message': row[1]} for row in messages]

# Initialize the database if it doesn't exist
if not os.path.exists(DATABASE):
    init_db()

# Load message history on startup
# In Streamlit, the script reruns on user interaction.
# We load messages here so they are available in the session state.
st.session_state.messages = get_messages()


st.title("Real-time Chat Application")

# Check if username is set
if st.session_state.username is None:
    # Display username input
    username_input = st.text_input("Enter your username:", key="username_input")
    # Save username on input
    if username_input:
        st.session_state.username = username_input
        # Update users dictionary (simplified for now)
        st.session_state.users[st.session_state.username] = st.session_state.username # Using username as key and value for simplicity
        st.experimental_rerun() # Rerun to show the chat interface

# Display welcome message and chat interface if username is set
if st.session_state.username:
    st.write(f"Welcome, {st.session_state.username}!")

    # Container for messages
    message_container = st.container()

    # Message input and send button
    col1, col2 = st.columns([4, 1])
    with col1:
        # Use a form to clear the input after sending without a full rerun
        with st.form(key='send_form', clear_on_submit=True):
            message_input_form = st.text_input("Type your message here...", key="message_input_form", label_visibility="collapsed")
            send_button = st.form_submit_button("Send")

            if send_button and message_input_form:
                add_message(st.session_state.username, message_input_form) # Save message to database
                # Since we are not using a continuous polling loop,
                # we don't need to append to session_state.messages here.
                # The message will appear after the next rerun triggered by user interaction
                # or manual page refresh.
                pass


    # Display messages from the database (which is loaded into session state)
    with message_container:
        for message in st.session_state.messages:
             st.write(f"**{message['username']}**: {message['message']}")

    # Display the list of users
    st.sidebar.title("Online Users")
    # Note: User list management in Streamlit without a continuous backend is limited.
    # This currently just reflects users who have entered a username in their active session
    # on this specific instance/run of the app.
    user_list = list(st.session_state.users.values())
    for user in user_list:
        st.sidebar.write(user)

    # Note: To see messages sent by other users, you will need to
    # interact with the app (e.g., send a message) or manually refresh the page.
    # Streamlit's execution model reruns the script on user interaction.
    # A more advanced real-time update would require a different architecture.
