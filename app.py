import streamlit as st
import requests
from urllib.parse import parse_qs, urljoin

# Page configuration
st.set_page_config(
    page_title="Facebook Login",
    page_icon="📱",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stApp {
        background-color: #f0f2f5;
    }
    .login-container {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .fb-header {
        color: #1877f2;
        font-weight: bold;
    }
    .success-message {
        background-color: #e6f7e6;
        border-left: 4px solid #42b72a;
        padding: 10px;
        border-radius: 4px;
    }
    .error-message {
        background-color: #ffebe9;
        border-left: 4px solid #fa383e;
        padding: 10px;
        border-radius: 4px;
    }
    .cookie-input {
        margin-bottom: 15px;
    }
    .instructions {
        background-color: #f7f8fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .step {
        margin-bottom: 10px;
    }
    .content-viewer {
        background: white;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

def parse_cookies(cookie_string):
    """Parse the cookie string into a dictionary"""
    cookies = {}
    if not cookie_string:
        return cookies
        
    parts = cookie_string.split(';')
    for part in parts:
        part = part.strip()
        if '=' in part:
            name, value = part.split('=', 1)
            cookies[name] = value
    return cookies

def fetch_facebook_content(cookies, url):
    """Fetch Facebook content using the provided cookies"""
    headers = {
        'User-Agent': cookies.get('useragent', 'Mozilla/5.0'),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    try:
        response = session.get(url, headers=headers)
        return response.text if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error fetching content: {str(e)}")
        return None

def check_login_status(cookies):
    """Check if the login is successful using the cookies"""
    if not cookies:
        return False, "Please enter your cookies"
        
    headers = {
        'User-Agent': cookies.get('useragent', 'Mozilla/5.0'),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    session = requests.Session()
    for name, value in cookies.items():
        session.cookies.set(name, value)
    
    try:
        response = session.get('https://www.facebook.com/me', headers=headers, allow_redirects=True)
        if 'login' in response.url or response.status_code != 200:
            return False, "Invalid cookies. Please check your input."
        return True, "Successfully logged in!"
    except Exception as e:
        return False, f"Error checking login status: {str(e)}"

def main():
    st.markdown('<h1 class="fb-header">Facebook Login with Cookies</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Instructions
        st.markdown("""
        <div class="instructions">
            <h3>How to get your Facebook cookies:</h3>
            <div class="step">1. Open Facebook in Chrome and log in</div>
            <div class="step">2. Press F12 to open Developer Tools</div>
            <div class="step">3. Go to Application > Storage > Cookies</div>
            <div class="step">4. Select 'https://www.facebook.com'</div>
            <div class="step">5. Copy all cookies and paste them below</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Cookie input
        st.markdown('<div class="cookie-input">', unsafe_allow_html=True)
        cookies_input = st.text_area(
            "Enter your Facebook cookies:",
            placeholder="Paste your cookies here (e.g., c_user=123456789; xs=abc123...)",
            height=100
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("Login", type="primary"):
                parsed_cookies = parse_cookies(cookies_input)
                success, message = check_login_status(parsed_cookies)
                
                if success:
                    st.session_state.logged_in = True
                    st.session_state.cookies = cookies_input
                    st.session_state.parsed_cookies = parsed_cookies
                else:
                    st.session_state.logged_in = False
                st.session_state.message = message
        
        with col2:
            if 'message' in st.session_state:
                message_class = "success-message" if st.session_state.get('logged_in', False) else "error-message"
                st.markdown(f'<div class="{message_class}">{st.session_state.message}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Facebook content if logged in
    if st.session_state.get('logged_in', False):
        st.markdown("### Facebook Navigation")
        
        # Navigation options
        options = {
            "News Feed": "https://www.facebook.com",
            "Profile": "https://www.facebook.com/me",
            "Friends": "https://www.facebook.com/friends",
            "Messages": "https://www.facebook.com/messages",
            "Notifications": "https://www.facebook.com/notifications"
        }
        
        selected_page = st.selectbox("Select page to view:", options.keys())
        
        if selected_page:
            url = options[selected_page]
            content = fetch_facebook_content(st.session_state.parsed_cookies, url)
            
            if content:
                st.markdown('<div class="content-viewer">', unsafe_allow_html=True)
                st.markdown(f"### Viewing: {selected_page}")
                st.code(content, language="html")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Unable to fetch content. Please check your cookies and try again.")

if __name__ == "__main__":
    main()
