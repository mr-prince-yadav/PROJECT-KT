import streamlit as st
import datetime
from typing import Dict, List, Set, Tuple

def inject_css():
    """Inject enhanced WhatsApp-like CSS styles into Streamlit app"""
    st.markdown(
        """
        <style>
        /* Hide Streamlit default elements */
        .stButton > button {
            border: none !important;
            background: transparent !important;
            color: #999 !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            font-size: 12px !important;
            margin: 2px !important;
        }
        
        .stButton > button:hover {
            background: #f0f0f0 !important;
            color: #333 !important;
        }

        /* Chat container */
        .chat-container {
            width: 100%;
            max-height: 70vh;
            display: flex;
            flex-direction: column;
            border: 1px solid #ddd;
            border-radius: 16px;
            background: linear-gradient(180deg, #ece5dd 0%, #d9d3c7 100%);
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            position: relative;
        }

        /* Chat header */
        .chat-header {
            background: #128c7e;
            color: white;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #075e54;
        }

        .chat-header h3 {
            margin: 0;
            font-size: 16px;
            font-weight: 500;
        }

        .online-indicator {
            width: 8px;
            height: 8px;
            background: #4fc3f7;
            border-radius: 50%;
            margin-left: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        /* Scrollable chat window */
        .chat-window {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cg fill-opacity='0.03'%3E%3Cpolygon fill='%23000' points='50 0 60 40 100 50 60 60 50 100 40 60 0 50 40 40'/%3E%3C/g%3E%3C/svg%3E");
            scrollbar-width: thin;
            scrollbar-color: rgba(0,0,0,0.2) transparent;
        }

        .chat-window::-webkit-scrollbar {
            width: 6px;
        }

        .chat-window::-webkit-scrollbar-track {
            background: transparent;
        }

        .chat-window::-webkit-scrollbar-thumb {
            background: rgba(0,0,0,0.2);
            border-radius: 3px;
        }

        /* Chat bubbles */
        .chat-bubble {
            max-width: 75%;
            padding: 8px 12px 18px 12px;
            border-radius: 8px;
            margin: 3px 0;
            font-size: 14px;
            line-height: 1.4;
            position: relative;
            word-wrap: break-word;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            animation: slideIn 0.2s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Sent (green bubble, right) */
        .sender {
            background: linear-gradient(135deg, #dcf8c6 0%, #c8e6c9 100%);
            align-self: flex-end;
            border-bottom-right-radius: 2px;
            border: 1px solid #b8e6b8;
        }

        /* Received (white bubble, left) */
        .receiver {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            align-self: flex-start;
            border-bottom-left-radius: 2px;
            border: 1px solid #e0e0e0;
        }

        /* Message status indicators */
        .message-status {
            position: absolute;
            bottom: 2px;
            right: 6px;
            font-size: 10px;
            color: #667781;
            display: flex;
            align-items: center;
            gap: 2px;
        }

        .edited-indicator {
            font-style: italic;
            font-size: 10px;
            color: #999;
        }

        .deleted-message {
            font-style: italic;
            color: #999;
            opacity: 0.7;
        }

        /* Time and date */
        .timestamp {
            font-size: 10px;
            color: #667781;
            margin-right: 12px;
        }

        /* Date separators */
        .date-separator {
            align-self: center;
            background: rgba(255,255,255,0.9);
            color: #333;
            font-size: 11px;
            font-weight: 500;
            padding: 4px 12px;
            border-radius: 12px;
            margin: 12px 0 8px 0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            border: 1px solid rgba(0,0,0,0.05);
        }

        /* Message actions */
        .message-actions {
            position: absolute;
            top: -30px;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 4px 0;
            min-width: 120px;
            z-index: 1000;
        }

        .action-button {
            display: block;
            width: 100%;
            padding: 8px 12px;
            border: none;
            background: transparent;
            text-align: left;
            cursor: pointer;
            font-size: 13px;
            color: #333;
        }

        .action-button:hover {
            background: #f5f5f5;
        }

        /* Chat input area */
        .chat-input {
            display: flex;
            padding: 12px 16px;
            background: #f0f0f0;
            border-top: 1px solid #ddd;
            align-items: flex-end;
            gap: 8px;
        }

        /* Custom input styling */
        .stTextInput > div > div > input {
            border-radius: 20px !important;
            border: 1px solid #ddd !important;
            padding: 10px 16px !important;
            font-size: 14px !important;
            background: white !important;
            outline: none !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #25d366 !important;
            box-shadow: 0 0 0 1px #25d366 !important;
        }

        /* Send button */
        .send-button {
            background: #25d366 !important;
            color: white !important;
            border: none !important;
            border-radius: 50% !important;
            width: 44px !important;
            height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 18px !important;
            cursor: pointer !important;
            transition: background-color 0.2s ease !important;
        }

        .send-button:hover {
            background: #1db954 !important;
        }

        /* Typing indicator */
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 4px;
            color: #999;
            font-size: 12px;
            font-style: italic;
            padding: 8px 16px;
        }

        .typing-dots {
            display: flex;
            gap: 2px;
        }

        .typing-dot {
            width: 4px;
            height: 4px;
            background: #999;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(1) { animation-delay: 0s; }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 60%, 100% { opacity: 0.3; }
            30% { opacity: 1; }
        }

        /* Message reactions */
        .message-reactions {
            position: absolute;
            bottom: -12px;
            right: 8px;
            display: flex;
            gap: 2px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 2px 6px;
            font-size: 10px;
        }

        /* Scroll to bottom button */
        .scroll-to-bottom {
            position: absolute;
            bottom: 80px;
            right: 20px;
            background: #25d366;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 1000;
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
            .chat-bubble {
                max-width: 85%;
                font-size: 13px;
            }
            
            .chat-container {
                max-height: 60vh;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_timestamp(dt_str: str) -> Tuple[str, str]:
    """Format timestamp into date and time components"""
    try:
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
        date_str = dt.strftime("%B %d, %Y")
        time_str = dt.strftime("%I:%M %p")
        return date_str, time_str
    except:
        parts = dt_str.split(" ") if " " in dt_str else [dt_str, ""]
        return parts[0], " ".join(parts[1:]) if len(parts) > 1 else ""


def get_message_status_icon(is_me: bool, delivered: bool = True, read: bool = False) -> str:
    """Get message status icon based on delivery status"""
    if not is_me:
        return ""
    if read:
        return "✓✓"  # Blue double check (read)
    elif delivered:
        return "✓✓"  # Gray double check (delivered)
    else:
        return "✓"   # Single check (sent)


def chat_header(title: str = "💬 Chat with Admin", show_online: bool = True):
    """Render chat header with title and online indicator"""
    online_indicator = '<div class="online-indicator"></div>' if show_online else ''
    
    st.markdown(
        f"""
        <div class="chat-header">
            <h3>{title}</h3>
            {online_indicator}
        </div>
        """,
        unsafe_allow_html=True
    )


def date_separator(date_str: str):
    """Render date separator"""
    st.markdown(
        f"<div class='date-separator'>{date_str}</div>", 
        unsafe_allow_html=True
    )


def chat_bubble(msg_id: int, text: str, is_me: bool, timestamp: str, 
                edited: bool = False, deleted: bool = False, 
                delivered: bool = True, read: bool = False):
    """Render a single chat bubble with enhanced features"""
    
    bubble_class = "sender" if is_me else "receiver"
    display_text = text
    
    if deleted:
        display_text = "🚫 This message was deleted"
        bubble_class += " deleted-message"
    
    date_str, time_str = format_timestamp(timestamp)
    status_icon = get_message_status_icon(is_me, delivered, read)
    edited_text = " (edited)" if edited else ""
    
    # Message bubble
    st.markdown(
        f"""
        <div class="chat-bubble {bubble_class}" id="msg-{msg_id}">
            {display_text}
            <div class="message-status">
                <span class="timestamp">{time_str}</span>
                {f'<span class="edited-indicator">{edited_text}</span>' if edited else ''}
                <span>{status_icon}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def typing_indicator(user_name: str = "Admin", show: bool = False):
    """Render typing indicator"""
    if show:
        st.markdown(
            f"""
            <div class="typing-indicator">
                <span>{user_name} is typing</span>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def message_actions_menu(msg_id: int, is_me: bool, rollno: str, chat_id: str) -> Dict[str, bool]:
    """
    Render message action menu and return dict of actions taken
    Returns: {'edited': bool, 'deleted_all': bool, 'deleted_me': bool}
    """
    menu_key = f"menu_{rollno}_{msg_id}"
    actions = {'edited': False, 'deleted_all': False, 'deleted_me': False}
    
    # Create columns for better layout
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("⋮", key=f"menu_btn_{menu_key}", help="Message options"):
            st.session_state[f"show_menu_{msg_id}"] = not st.session_state.get(f"show_menu_{msg_id}", False)
    
    # Show menu options if menu is open
    if st.session_state.get(f"show_menu_{msg_id}", False):
        with col2:
            if is_me and st.button("✏️", key=f"edit_btn_{menu_key}", help="Edit message"):
                st.session_state[f"editing_{msg_id}"] = True
                st.session_state[f"show_menu_{msg_id}"] = False
                actions['edited'] = True
        
        with col3:
            if st.button("🗑", key=f"delete_all_btn_{menu_key}", help="Delete for everyone"):
                st.session_state.messages[chat_id][msg_id]["deleted"] = True
                st.session_state.messages[chat_id][msg_id]["text"] = ""
                st.session_state[f"show_menu_{msg_id}"] = False
                actions['deleted_all'] = True
        
        with col4:
            if st.button("🙈", key=f"delete_me_btn_{menu_key}", help="Delete for me"):
                hidden = st.session_state.get(f"hidden_msgs_{rollno}", set())
                hidden.add(msg_id)
                st.session_state[f"hidden_msgs_{rollno}"] = hidden
                st.session_state[f"show_menu_{msg_id}"] = False
                actions['deleted_me'] = True
    
    return actions


def edit_message_form(msg_id: int, current_text: str, rollno: str, chat_id: str) -> bool:
    """
    Render message editing form
    Returns: True if message was edited, False otherwise
    """
    edit_key = f"edit_{rollno}_{msg_id}"
    
    with st.form(key=f"edit_form_{edit_key}", clear_on_submit=False):
        new_text = st.text_area(
            "Edit message",
            value=current_text,
            key=f"edit_input_{edit_key}",
            label_visibility="collapsed",
            height=60
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("💾 Save", use_container_width=True):
                if new_text.strip():
                    st.session_state.messages[chat_id][msg_id]["text"] = new_text.strip()
                    st.session_state.messages[chat_id][msg_id]["edited"] = True
                    st.session_state.pop(f"editing_{msg_id}", None)
                    return True
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.pop(f"editing_{msg_id}", None)
                return False
    
    return False


def chat_input_form(rollno: str) -> str:
    """
    Render chat input form
    Returns: message text if submitted, empty string otherwise
    """
    with st.form(key=f"chat_form_{rollno}", clear_on_submit=True):
        col_input, col_send = st.columns([6, 1])
        
        with col_input:
            new_msg = st.text_input(
                "", 
                key=f"msg_input_{rollno}",
                placeholder="Type a message...",
                label_visibility="collapsed"
            )
        
        with col_send:
            submit = st.form_submit_button("➤", use_container_width=True)
        
        if submit and new_msg.strip():
            return new_msg.strip()
    
    return ""


def auto_scroll_script():
    """Add JavaScript to auto-scroll chat to bottom"""
    st.markdown(
        """
        <script>
        setTimeout(function() {
            var chatWindow = document.getElementById('chat-window');
            if(chatWindow) {
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
        }, 100);
        </script>
        """,
        unsafe_allow_html=True,
    )


def chat_container_start():
    """Start chat container div"""
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)


def chat_window_start():
    """Start chat window div"""
    st.markdown("<div class='chat-window' id='chat-window'>", unsafe_allow_html=True)


def chat_input_area_start():
    """Start chat input area div"""
    st.markdown("<div class='chat-input'>", unsafe_allow_html=True)


def close_div():
    """Close div tag"""
    st.markdown("</div>", unsafe_allow_html=True)


def create_message_dict(from_user: str, to_user: str, text: str, 
                       delivered: bool = True, read: bool = False) -> Dict:
    """Create a standardized message dictionary"""
    return {
        "from": from_user,
        "to": to_user,
        "text": text,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p"),
        "edited": False,
        "deleted": False,
        "delivered": delivered,
        "read": read
    }