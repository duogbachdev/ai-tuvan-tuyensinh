import streamlit as st
import datetime
from g4f.client import Client
from g4f.Provider import FreeGpt
import time
import base64

# Đọc nội dung từ hai file
def read_file(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        st.error(f"Lỗi khi đọc file {file_name}: {str(e)}")
        return f"Không đọc được nội dung file {file_name}"

# Khởi tạo session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'daily_chats' not in st.session_state:
    st.session_state.daily_chats = {}
if 'viewing_past_chat' not in st.session_state:
    st.session_state.viewing_past_chat = False
if 'past_chat_viewing' not in st.session_state:
    st.session_state.past_chat_viewing = []
# Thêm session state cho việc xử lý Enter key
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""

# Set custom page config with dark theme
st.set_page_config(
    page_title="AI Tư vấn tuyển sinh",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gradient button CSS
def get_gradient_button_css():
    return """
    /* Linear gradient for buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6253e1, #04befe) !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.5rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        opacity: 0.9 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
    }
    
    .stButton > button:hover {
        opacity: 1 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(98, 83, 225, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    """

# Custom CSS for dark theme
st.markdown(f"""
<style>
    .main {{
        background-color: #121212;
        color: #F0F2F6;
    }}
    .stTextInput > div > div > input {{
        background-color: #1E1E1E;
        color: white;
        border-radius: 5px;
        border: 1px solid #333;
    }}
    .stTextArea > div > div > textarea {{
        background-color: #1E1E1E;
        color: white;
        border-radius: 5px;
        border: 1px solid #333;
    }}
    
    /* Remove "Nhập câu hỏi của bạn:" background */
    .stTextInput > label {{
        background: transparent !important;
        color: #CCC !important;
    }}
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {{
        background-color: #171717;
    }}
    
    .st-ba {{
        background-color: #202020;
    }}
    
    /* Dropdown select styling */
    div[data-baseweb="select"] > div {{
        background-color: #202020 !important;
        border: 1px solid #333 !important;
    }}
    
    /* Chat messages styling */
    .chat-message {{
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        position: relative;
        font-size: 1rem;
    }}
    
    .user-message {{
        background-color: #2E3759;
    }}
    
    .assistant-message {{
        background-color: #2A3042;
    }}
    
    /* Avatar styling */
    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }}
    
    .user-avatar {{
        background-color: #4B5D8E;
    }}
    
    .assistant-avatar {{
        background-color: #6253e1;
    }}
    
    /* New messages indicator */
    .new-message-indicator {{
        background: linear-gradient(135deg, #6253e1, #04befe);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.7rem;
        position: absolute;
        top: -0.5rem;
        right: -0.5rem;
    }}
    
    /* Input field with icon */
    .input-with-icon {{
        position: relative;
        margin-bottom: 1rem;
    }}
    
    /* Header title styling */
    .app-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .app-title {{
        background: linear-gradient(135deg, #6253e1, #04befe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    /* History label */
    .history-label {{
        font-size: 0.85rem;
        color: #AAA;
        margin-bottom: 0.5rem;
    }}
    
    /* Fix for sidebar selection spacing */
    .sidebar-header {{
        margin-top: 30px;
        margin-bottom: 20px;
    }}
    
    .sidebar-option {{
        margin-top: 15px;
    }}
    
    /* CSS để xử lý Enter key */
    .stTextInput > div > div > input {{
        padding-right: 40px;
    }}
    
    {get_gradient_button_css()}
</style>
""", unsafe_allow_html=True)

# Define icon HTML
def get_icon(icon_name, color="white"):
    icons = {
        "calendar": f"""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="{color}" viewBox="0 0 16 16">
  <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5M1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z"/>
</svg>""",
        "user": f"""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="{color}" viewBox="0 0 16 16">
  <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6m2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0m4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4m-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10s-3.516.68-4.168 1.332c-.678.678-.83 1.418-.832 1.664z"/>
</svg>""",
        "bot": f"""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="{color}" viewBox="0 0 16 16">
  <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a24.8 24.8 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135Z"/>
  <path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"/>
</svg>""",
        "chat": f"""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="{color}" viewBox="0 0 16 16">
  <path d="M5 8a1 1 0 1 1-2 0 1 1 0 0 1 2 0m4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0m3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2"/>
  <path d="m2.165 15.803.02-.004c1.83-.363 2.948-.842 3.468-1.105A9 9 0 0 0 8 15c4.418 0 8-3.134 8-7s-3.582-7-8-7-8 3.134-8 7c0 1.76.743 3.37 1.97 4.6a10.4 10.4 0 0 1-.524 2.318l-.003.011a11 11 0 0 1-.244.637c-.079.186.074.394.273.362a21.8 21.8 0 0 0 .693-.125m.8-3.108a1 1 0 0 0-.287-.801C1.618 10.83 1 9.468 1 8c0-3.192 3.004-6 7-6s7 2.808 7 6-3.004 6-7 6a8 8 0 0 1-2.088-.272 1 1 0 0 0-.711.074c-.387.196-1.24.57-2.634.893a11 11 0 0 0 .398-2"/>
</svg>""",
        "graduation": f"""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="{color}" viewBox="0 0 16 16">
  <path d="M4 11.667v1.88A2.45 2.45 0 0 1 5.189 16h5.622A2.45 2.45 0 0 1 12 13.546v-1.879l-.04-.024-.041-.027A7.03 7.03 0 0 1 8 13a7.03 7.03 0 0 1-3.918-1.386l-.042.028z"/>
  <path d="M0 9.843V4a.5.5 0 0 1 .276-.447l8-4A.5.5 0 0 1 9 0l8 4a.5.5 0 0 1 0 .894l-8 4a.5.5 0 0 1-.448 0L4 6.614v4.784A3 3 0 0 0 6.92 11h2.16A3 3 0 0 0 12 11.397v-4.04a1 1 0 1 1 2 0v4.486a4 4 0 0 1-1.318 2.942 5 5 0 0 1-3.185 1.215h-1.994a5 5 0 0 1-3.185-1.215 4 4 0 0 1-1.318-2.943V6.153l-2.724 1.363A.5.5 0 0 1 0 7.07z"/>
</svg>"""
    }
    return icons.get(icon_name, "")

# Thử đọc files
try:
    file_content_1 = read_file('cau_hoi_thuong_gap.txt')
    file_content_2 = read_file('thong_tin_tuyen_sinh.txt')
except Exception as e:
    st.error(f"Lỗi khi đọc file: {str(e)}")
    file_content_1 = "Không đọc được nội dung file"
    file_content_2 = "Không đọc được nội dung file"

# Kết hợp nội dung của cả hai file
combined_content = f"Nội dung từ file câu hỏi thường gặp:\n{file_content_1}\n\nNội dung từ file thông tin tuyển sinh:\n{file_content_2}"

def stream_data(data):
    for word in data.split():
        yield word + " "
        time.sleep(0.04)

def get_response(prompt):
    try:
        client = Client()
        chat_completion = client.chat.completions.create(
            model=None,
            provider=FreeGpt,  # Chỉ sử dụng FreeGpt
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        response = ""
        for completion in chat_completion:
            if hasattr(completion.choices[0], 'delta') and hasattr(completion.choices[0].delta, 'content'):
                response += completion.choices[0].delta.content or ""
        
        return response
    except Exception as e:
        return f"Lỗi khi sử dụng FreeGpt: {str(e)}"

def save_chat_history():
    # Get today's date as key
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Create entry for today if it doesn't exist
    if today not in st.session_state.daily_chats:
        st.session_state.daily_chats[today] = []
    
    # Add current chat to today's entry
    if st.session_state.chat_history:
        chat_id = f"Chat_{len(st.session_state.daily_chats[today]) + 1}"
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.daily_chats[today].append({
            "id": chat_id,
            "time": timestamp,
            "conversation": st.session_state.chat_history.copy()
        })

# Hàm xử lý submit question
def handle_submit():
    if st.session_state.user_question:
        user_question = st.session_state.user_question
        st.session_state.user_question = ""  # Clear input
        
        # Tạo prompt nhấn mạnh yêu cầu trả lời bằng tiếng Việt
        prompt = f"""
        INSTRUCTIONS: YOU MUST RESPOND IN VIETNAMESE LANGUAGE! DO NOT USE CHINESE OR ANY OTHER LANGUAGE!
        
        Đây là câu hỏi từ người dùng: {user_question}
        
        Đây là thông tin tham khảo:
        {combined_content}
        
        LƯU Ý QUAN TRỌNG:
        1. Bạn PHẢI trả lời bằng tiếng Việt Nam. KHÔNG dùng tiếng Trung, tiếng Anh hay bất kỳ ngôn ngữ nào khác.
        2. Nếu không biết câu trả lời chính xác từ dữ liệu, hãy nói rằng bạn không có thông tin đó.
        3. Câu trả lời cần ngắn gọn, dễ hiểu và đúng trọng tâm.
        """
        
        with st.spinner('Đang xử lý câu hỏi của bạn...'):
            response = get_response(prompt)
        
        # Lưu câu hỏi và câu trả lời vào lịch sử chat
        st.session_state.chat_history.append(("User", user_question))
        st.session_state.chat_history.append(("Assistant", response))
        
        # Lưu chat vào lịch sử theo ngày
        save_chat_history()
        
        # Rerun để cập nhật UI
        st.rerun()

# Sidebar for chat history by date - Chỉ giữ lại phần chọn ngày
with st.sidebar:
    # Added margin-top for proper spacing from top
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.markdown(f'<div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 20px;"><span>{get_icon("calendar")}</span> <h3 style="margin: 0; padding: 0;">Lịch sử theo ngày</h3></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add spacing before selection elements
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    # Add a button to return to current chat if viewing past chat
    if st.session_state.viewing_past_chat:
        st.markdown('<div class="stButton">', unsafe_allow_html=True)
        if st.button(f'Quay lại hội thoại', key='back_btn'):
            st.session_state.viewing_past_chat = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show available dates
    if st.session_state.daily_chats:
        st.markdown('<div class="sidebar-option">', unsafe_allow_html=True)
        st.markdown('<p class="history-label">Chọn ngày:</p>', unsafe_allow_html=True)
        selected_date = st.selectbox(
            "", 
            list(st.session_state.daily_chats.keys()),
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Xóa phần chọn cuộc hội thoại, thay vào đó là hiển thị tất cả
        if selected_date:
            st.markdown('<div class="stButton">', unsafe_allow_html=True)
            if st.button(f'Xem lại', key='view_btn'):
                # Hiển thị tất cả cuộc trò chuyện trong ngày đó
                all_conversations = []
                for chat in st.session_state.daily_chats[selected_date]:
                    all_conversations.extend(chat["conversation"])
                st.session_state.past_chat_viewing = all_conversations
                st.session_state.viewing_past_chat = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# Main content area - Header
st.markdown(f'''
<div class="app-header">
    <div style="display: flex; justify-content: center; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
        <span style="font-size: 2.5rem;">{get_icon("graduation", "#6253e1")}</span>
        <h1 class="app-title">AI Tư vấn tuyển sinh</h1>
    </div>
    <p style="color: #AAA; font-size: 1.1rem;">Hỗ trợ thông tin tuyển sinh và giải đáp thắc mắc</p>
</div>
''', unsafe_allow_html=True)

st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

# Main content
if st.session_state.viewing_past_chat:
    st.markdown(f'''
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
        <span>{get_icon("chat")}</span>
        <h3 style="margin: 0; padding: 0;">Xem lại cuộc trò chuyện</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # Reverse the chat history to show newest messages first
    for idx, (role, message) in enumerate(reversed(st.session_state.past_chat_viewing)):
        if role == "User":
            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown(f'''
                <div class="avatar user-avatar">{get_icon("user")}</div>
                ''', unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='chat-message user-message'>{message}</div>", unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown(f'''
                <div class="avatar assistant-avatar">{get_icon("bot")}</div>
                ''', unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='chat-message assistant-message'>{message}</div>", unsafe_allow_html=True)
else:
    # Callback để xử lý khi Enter được nhấn
    def submit_on_enter():
        handle_submit()

    # Input field that supports Enter key
    user_question = st.text_input(
        "",
        key="user_question", 
        placeholder="Nhập câu hỏi của bạn...", 
        label_visibility="collapsed",
        on_change=submit_on_enter
    )
    
    # Custom button with gradient and icon
    col1, col2, col3 = st.columns([1, 1, 5])
    with col1:
        if st.button(f'Đặt câu hỏi'):
            handle_submit()
    
    if not user_question and st.session_state.user_question:
        # Xử lý khi người dùng đã submit nhưng session state chưa được xóa
        handle_submit()
        
    # Hiển thị lịch sử chat hiện tại với newest messages first
    if st.session_state.chat_history:
        st.markdown(f'''
        <div style="display: flex; align-items: center; gap: 0.5rem; margin: 1.5rem 0 1rem 0;">
            <span>{get_icon("chat")}</span>
            <h3 style="margin: 0; padding: 0;">Lịch sử chat</h3>
        </div>
        ''', unsafe_allow_html=True)
        
        # Reverse the chat history to show newest messages first
        for idx, (role, message) in enumerate(reversed(st.session_state.chat_history)):
            if role == "User":
                col1, col2 = st.columns([1, 20])
                with col1:
                    st.markdown(f'''
                    <div class="avatar user-avatar">{get_icon("user")}</div>
                    ''', unsafe_allow_html=True)
                with col2:
                    if idx == 0:  # Newest message
                        st.markdown(f'''
                        <div class='chat-message user-message'>
                            <span class="new-message-indicator">Mới nhất</span>
                            {message}
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='chat-message user-message'>{message}</div>", unsafe_allow_html=True)
            else:
                col1, col2 = st.columns([1, 20])
                with col1:
                    st.markdown(f'''
                    <div class="avatar assistant-avatar">{get_icon("bot")}</div>
                    ''', unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='chat-message assistant-message'>{message}</div>", unsafe_allow_html=True)