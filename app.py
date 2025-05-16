import streamlit as st
import requests
from urllib.parse import parse_qs

# Page configuration
st.set_page_config(
    page_title="Facebook Login",
    page_icon="📱",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .stApp { background-color: #f0f2f5; }
    .login-container {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .fb-header { color: #1877f2; font-weight: bold; }
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
    .content-container {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .response-info {
        font-family: monospace;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 4px;
        margin-top: 10px;
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
    """Fetch content from Facebook using requests"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, cookies=cookies, headers=headers, allow_redirects=True)
        return {
            'status_code': response.status_code,
            'url': response.url,
            'headers': dict(response.headers),
            'content_type': response.headers.get('content-type', ''),
            'is_redirect': len(response.history) > 0
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    st.markdown('<h1 class="fb-header">Facebook Content Viewer</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Instructions
        st.markdown("""
        ### How to use:
        1. Enter your Facebook cookies below
        2. Select the content you want to view
        3. Click 'Fetch Content' to retrieve Facebook data
        """)
        
        # Cookie input
        cookies_input = st.text_area(
            "Enter your Facebook cookies:",
            height=100,
            help="Paste your Facebook cookies here"
        )
        
        # Navigation options
        options = {
            "News Feed": "https://www.facebook.com",
            "Profile": "https://www.facebook.com/me",
            "Friends": "https://www.facebook.com/friends",
            "Messages": "https://www.facebook.com/messages"
        }
        
        selected_page = st.selectbox("Select content to view:", options.keys())
        
        if st.button("Fetch Content", type="primary"):
            if cookies_input:
                parsed_cookies = parse_cookies(cookies_input)
                
                with st.spinner("Fetching Facebook content..."):
                    result = fetch_facebook_content(parsed_cookies, options[selected_page])
                    
                    st.markdown('<div class="content-container">', unsafe_allow_html=True)
                    
                    if 'error' in result:
                        st.error(f"Error fetching content: {result['error']}")
                    else:
                        st.success(f"Successfully connected to Facebook")
                        st.markdown("### Response Information")
                        st.markdown('<div class="response-info">', unsafe_allow_html=True)
                        st.json({
                            'Status Code': result['status_code'],
                            'Final URL': result['url'],
                            'Content Type': result['content_type'],
                            'Redirected': result['is_redirect']
                        })
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Please enter your Facebook cookies first")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
