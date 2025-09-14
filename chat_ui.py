# chat_ui.py
import streamlit as st

def inject_css():
    """Inject WhatsApp-like CSS styles into Streamlit app"""
    st.markdown(
        """
        <style>
        /* Chat container */
        .chat-room {
            width: 100%;
            height: auto;             /* grows naturally with content */
            max-height: 65vh;         /* but will not exceed 80% of screen */
            overflow-y: auto;         /* scroll only if too many messages */
            border: 1px solid #ccc;
            padding: 12px;
            border-radius: 12px;
            background: #f9f9f9;
        }

        /* Chat messages area */
        .chat-window {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            
        }

        /* Message bubble */
        .chat-bubble {
            max-width: 70%;
            padding: 8px 12px;
            border-radius: 10px;
            margin: 6px;
            font-size: 14px;
            word-wrap: break-word;
            position: relative;
            box-shadow: 0 1px 1px rgba(0,0,0,0.1);
        }

        /* Sent (right side) */
        .sender {
            background: #dcf8c6;
            align-self: flex-end;
            border-bottom-right-radius: 0;
            margin-left: 20%;
        }

        /* Received (left side) */
        .receiver {
            background: #fff;
            align-self: flex-start;
            border-bottom-left-radius: 0;
            margin-right: 20%;
        }

        /* Time below each bubble */
        .time {
            font-size: 11px;
            color: #666;
            margin-top: 3px;
            text-align: right;
        }

        /* Date separator */
        .date-separator {
            text-align: center;
            margin: 10px 0;
            font-size: 12px;
            color: #8696a0;
        }

        /* Dropdown menu button (⋮) */
        .menu-btn {
            position: absolute;
            left: -25px;
            top: 5px;
            font-size: 14px;
            cursor: pointer;
            color: #999;
        }

        /* Input area */
        .chat-input {
            border-top: 1px solid #ccc;
            padding: 8px;
            background: white;
            display: flex;
            align-items: center;
            position: sticky;
            bottom: 0;
        }

        .chat-input input {
            flex: 1;
            border-radius: 20px;
            border: 1px solid #ccc;
            padding: 10px;
            outline: none;
        }

        .send-btn {
            background: #25d366;
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: 8px;
            cursor: pointer;
        }

        /* Scroll to bottom helper */
        #scroll-anchor {
            float: left;
            clear: both;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def chat_bubble(msg_id, text, is_me, timestamp, edited=False, deleted=False):
    """
    Render a single chat bubble with timestamp & menu placeholder.
    """
    bubble_class = "sender" if is_me else "receiver"
    if deleted:
        text = "🚫 Message deleted"

    st.markdown(
        f"""
        <div class="chat-bubble {bubble_class}">
            <span class="menu-btn">⋮</span>
            {text}
            <div class="time">{timestamp}{' ✏️' if edited else ''}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Invisible anchor to keep scroll at bottom
    st.markdown("<div id='scroll-anchor'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <script>
        var chatWindow = window.parent.document.querySelector('.chat-window');
        if(chatWindow) {{
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )
