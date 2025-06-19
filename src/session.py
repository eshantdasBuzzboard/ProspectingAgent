import streamlit as st


def initialize_chat_history():
    """Initialize chat history in session state if it doesn't exist."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.questions = []


def get_chat_history():
    """Get the current chat history."""
    initialize_chat_history()
    return st.session_state.chat_history


def get_last4_chat_history():
    """Get the current chat history."""
    initialize_chat_history()
    return st.session_state.chat_history[:-8]


def get_last_question():
    """Get the last question from the chat history, or return an empty string if none exist."""
    initialize_chat_history()
    if st.session_state.questions:
        return st.session_state.questions[-1]
    return None


def get_all_questions():
    """Get the current chat history."""
    initialize_chat_history()
    return st.session_state.questions


def add_to_chat_history(human_message, ai_message, question):
    """Append a new message to the chat history."""
    initialize_chat_history()
    st.session_state.chat_history.append(human_message)
    st.session_state.chat_history.append(ai_message)
    st.session_state.questions.append(question)
