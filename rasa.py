import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- SECURITY FIX: Load API Key from environment variables ---
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Check if the API key is available
if not API_KEY:
    st.error("🚨 OPENROUTER_API_KEY is not set! Please add it to your .env file.")
    st.stop()
# -------------------------------------------------------------

# Set up the page configuration
st.set_page_config(page_title="KrishnaAI Chatbot", layout="centered")

# Inject custom CSS for branding & layout improvements
# (Your CSS is good, no changes needed here)
st.markdown(
    """
    <style>
    /* Set light theme */
    body {
        background-color: rgb(240, 242, 246); /* Light gray/off-white background */
        color: black; /* Dark text */
        font-family: 'Arial', sans-serif;
    }

    /* Fixed "Krishna ai" in top-left corner */
    .fixed-top-left {
        position: fixed;
        top: 10px;
        left: 10px;
        font-size: 14px;
        font-weight: bold;
        color: black; /* Changed to black for contrast on light body */
        background-color: rgb(240, 242, 246); /* Match body background */
        padding: 5px 10px;
        border-radius: 5px;
        z-index: 1000;
    }

    /* Fixed "Made with ❤️ from Sohan" at the bottom-center */
    .fixed-bottom {
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 12px;
        color: black; /* Changed to black for contrast on light body */
        background-color: rgb(240, 242, 246); /* Match body background */
        padding: 5px 10px;
        border-radius: 5px;
        z-index: 1000;
    }

    /* Chat container */
    .chat-container {
        max-width: 700px;
        margin: auto;
        text-align: center;
    }

    /* Message box styling (general, will be overridden by user/ai specific) */
    .message-box {
        background-color: rgb(255, 255, 255); /* White background for messages */
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); /* Add a subtle shadow for depth */
    }

    /* User & AI message styling */
    .user-message {
        background-color: #e0e0e0; /* Light gray for user messages */
        color: black; /* Black text for user messages */
        text-align: right;
        margin-left: 15%; /* Push user messages to the right */
    }

    .ai-message {
        background-color: #ffffff; /* White for AI messages */
        color: black; /* Black text for AI messages */
        text-align: left;
        margin-right: 15%; /* Push AI messages to the left */
        border: 1px solid #ddd; /* Light border for AI messages */
    }

    /* Input box */
    .input-box {
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #cccccc; /* Lighter border */
        background-color: #ffffff; /* White background for input */
        color: black; /* Black text for input */
    }

    /* Send button */
    .send-button {
        background-color: #0A84FF; /* Keep primary blue */
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
    }

    .send-button:hover {
        background-color: #0066CC; /* Slightly darker blue on hover */
    }

    /* Action buttons */
    .action-button {
        background-color: rgb(255, 255, 255); /* White background */
        color: black; /* Black text */
        border: 1px solid #cccccc; /* Lighter border */
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 14px;
        cursor: pointer;
    }

    .action-button:hover {
        background-color: #f0f0f0; /* Very light gray on hover */
    }
    </style>
    <div class="fixed-top-left">Krishna ai</div>
    <div class="fixed-bottom">made with ❤️ from Sohan </div>
    """,
    unsafe_allow_html=True
)

# OpenRouter API details
API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Function to call the OpenRouter API for AI responses
def get_ai_response(user_input):
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": user_input}],
        "max_tokens": 150
    }
    
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # This will raise an exception for 4XX/5XX errors
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        # Specifically catch HTTP errors to provide better feedback
        if e.response.status_code == 401:
            return "Error: Authentication failed. Please check your API key."
        return f"Error: HTTP {e.response.status_code} - {e.response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error: A network error occurred: {e}"

# Title and welcome message
st.markdown("<div class='chat-container'><h1>What can I help with?</h1></div>", unsafe_allow_html=True)

# Chat history container
if 'messages' not in st.session_state:
    st.session_state.messages = []

chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.messages:
        role_class = "user-message" if message["role"] == "user" else "ai-message"
        st.markdown(f"<div class='message-box {role_class}'>{message['content']}</div>", unsafe_allow_html=True)

# # User input box
# user_input = st.text_input("", placeholder="Message Krishna AI...", key="chat_input", help="Type your message here.")

# Send button column layout
# Using a form to handle submission on Enter key
with st.form(key='chat_form'):
    user_input = st.text_input("", placeholder="Message Krishna AI...", key="chat_input_form", label_visibility="collapsed")
    submitted = st.form_submit_button("Send")

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("KrishnaAI is thinking..."):
            ai_response = get_ai_response(user_input)
        st.session_state.messages.append({"role": "AI", "content": ai_response})
        st.rerun()

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
