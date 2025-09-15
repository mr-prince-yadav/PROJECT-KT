import streamlit as st
import datetime
from typing import Dict, Tuple

def inject_css():
    """Inject enhanced WhatsApp-like CSS styles (light/dark mode ready)"""
    st.markdown(
        """
        <style>
        /* Hide Streamlit default button style */
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
            border: 1px solid #666;
            border-radius: 16px;
            overflow: hidden;
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
        @keyframes pulse {0%{opacity:1;}50%{opacity:0.5;}100%{opacity:1;}}

        /* Scrollable chat window */
        .chat-window {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            scrollbar-width: thin;
            scrollbar-color: rgba(0,0,0,0.2) transparent;
        }
        .chat-window::-webkit-scrollbar { width: 6px; }
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
            animation: slideIn 0.2s ease-out;
        }
        @keyframes slideIn {
            from { opacity:0; transform:translateY(10px);}
            to { opacity:1; transform:translateY(0);}
        }

       /* Light mode */
        @media (prefers-color-scheme: light) {
            .chat-room { background:#fff; }
            .sender { background:#dcf8c6; color:#000; border:1px solid #b8e6b8; }
            .receiver { background:#ffffff; color:#000; border:1px solid #ddd; }
            .date-separator { color:#666; background:rgba(255,255,255,0.9);}
            .time { color:#555; }
        }
        
        /* Dark mode */
        @media (prefers-color-scheme: dark) {
            .chat-room { background:#121212; }  /* darker background */
            .sender { background:#075e54; color:#fff; border:1px solid #0b8b80; }
            .receiver { background:#2a3942; color:#eaeaea; border:1px solid #3a4b53; }
            .date-separator { color:#ccc; background:#2f3b43;}
            .time { color:#aaa; }
        }


        .message-status { position:absolute; bottom:2px; right:6px; font-size:10px; color:#667781;}
        .edited-indicator { font-style:italic; font-size:10px; }
        .deleted-message { font-style:italic; opacity:0.7; }

        .date-separator {
            align-self:center;
            font-size:11px;
            font-weight:500;
            padding:4px 12px;
            border-radius:12px;
            margin:12px 0 8px 0;
        }

        /* Input area */
        .chat-input { display:flex; padding:12px 16px; border-top:1px solid #ddd; gap:8px; }
        .stTextInput > div > div > input {
            border-radius:20px !important;
            padding:10px 16px !important;
            font-size:14px !important;
        }
        .send-button {
            background:#25d366 !important;
            color:white !important;
            border-radius:50% !important;
            width:60px !important; height:60px !important;
        }

        /* Responsive */
        @media (max-width:768px) {
            .chat-bubble { max-width:85%; font-size:13px; }
            .chat-container { max-height:60vh; }
        }
        </style>
        """, unsafe_allow_html=True
    )

# ---------- helpers (unchanged) ----------

def format_timestamp(dt_str: str) -> Tuple[str, str]:
    try:
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
        return dt.strftime("%B %d, %Y"), dt.strftime("%I:%M %p")
    except:
        parts = dt_str.split(" ")
        return parts[0], " ".join(parts[1:]) if len(parts) > 1 else ""

def get_message_status_icon(is_me: bool, delivered: bool = True, read: bool = False) -> str:
    if not is_me: return ""
    if read: return "✓✓"
    elif delivered: return "✓✓"
    return "✓"

def chat_header(title: str = "💬 Chat", show_online: bool = True):
    online = '<div class="online-indicator"></div>' if show_online else ''
    st.markdown(f"<div class='chat-header'><h3>{title}</h3>{online}</div>", unsafe_allow_html=True)

def date_separator(date_str: str):
    st.markdown(f"<div class='date-separator'>{date_str}</div>", unsafe_allow_html=True)

def chat_bubble(msg_id: int, text: str, is_me: bool, timestamp: str,
                edited: bool=False, deleted: bool=False,
                delivered: bool=True, read: bool=False):
    bubble_class = "sender" if is_me else "receiver"
    display_text = "🚫 Deleted" if deleted else text
    _, time_str = format_timestamp(timestamp)
    status_icon = get_message_status_icon(is_me, delivered, read)
    edited_text = " (edited)" if edited else ""
    st.markdown(
        f"""
        <div class="chat-bubble {bubble_class}" id="msg-{msg_id}">
            {display_text}
            <div class="message-status">
                <span class="timestamp">{time_str}</span>{edited_text}{status_icon}
            </div>
        </div>
        """, unsafe_allow_html=True
    )

def chat_container_start(): st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
def chat_window_start(): st.markdown("<div class='chat-window chat-room' id='chat-window'>", unsafe_allow_html=True)
def chat_input_area_start(): st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
def close_div(): st.markdown("</div>", unsafe_allow_html=True)

def create_message_dict(from_user: str, to_user: str, text: str,
                        delivered: bool=True, read: bool=False) -> Dict:
    return {
        "from": from_user, "to": to_user, "text": text,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p"),
        "edited": False, "deleted": False,
        "delivered": delivered, "read": read
    }


