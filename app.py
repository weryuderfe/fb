import streamlit as st
import requests
from urllib.parse import parse_qs
import json

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
    .cookie-info {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
        font-size: 0.9em;
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
            cookies[name.strip()] = value.strip()
    return cookies

def validate_cookies(cookies):
    """Validate that required Facebook cookies are present"""
    required_cookies = ['c_user', 'xs', 'fr']
    missing_cookies = [cookie for cookie in required_cookies if cookie not in cookies]
    return len(missing_cookies) == 0, missing_cookies

def fetch_facebook_content(cookies, url):
    """Fetch content from Facebook using requests"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        session = requests.Session()
        response = session.get(url, cookies=cookies, headers=headers, allow_redirects=True)
        
        return {
            'status_code': response.status_code,
            'url': response.url,
            'headers': dict(response.headers),
            'content_type': response.headers.get('content-type', ''),
            'is_redirect': len(response.history) > 0,
            'history': [{'url': r.url, 'status_code': r.status_code} for r in response.history]
        }
    except requests.exceptions.RequestException as e:
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
        
        **Note:** Make sure to include essential cookies (c_user, xs, fr) for proper authentication.
        """)
        
        # Cookie input
        cookies_input = st.text_area(
            "Enter your Facebook cookies:",
            height=100,
            help="Paste your Facebook cookies here (including c_user, xs, and fr cookies)"
        )
        
        # Navigation options
        options = {
            "News Feed": "https://www.facebook.com",
            "Profile": "https://www.facebook.com/me",
            "Friends": "https://www.facebook.com/friends",
            "Messages": "https://www.facebook.com/messages"
        }
        
        selected_page = st.selectbox("Select content to view:", options.keys())
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fetch_button = st.button("Fetch Content", type="primary")
        
        if fetch_button:
            if cookies_input:
                parsed_cookies = parse_cookies(cookies_input)
                valid_cookies, missing_cookies = validate_cookies(parsed_cookies)
                
                if not valid_cookies:
                    st.error(f"Missing required cookies: {', '.join(missing_cookies)}")
                else:
                    with st.spinner("Fetching Facebook content..."):
                        result = fetch_facebook_content(parsed_cookies, options[selected_page])
                        
                        st.markdown('<div class="content-container">', unsafe_allow_html=True)
                        
                        if 'error' in result:
                            st.error(f"Error fetching content: {result['error']}")
                        else:
                            if result['status_code'] == 200:
                                st.success("Successfully connected to Facebook")
                            else:
                                st.warning("Connection established but might not be authenticated")
                            
                            st.markdown("### Response Information")
                            st.markdown('<div class="response-info">', unsafe_allow_html=True)
                            
                            response_info = {
                                'Status Code': result['status_code'],
                                'Final URL': result['url'],
                                'Content Type': result['content_type'],
                                'Redirected': result['is_redirect']
                            }
                            
                            if result['is_redirect']:
                                st.markdown("#### Redirect History")
                                for hist in result['history']:
                                    st.markdown(f"- {hist['status_code']}: {hist['url']}")
                            
                            st.json(response_info)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Display cookie information
                            st.markdown("### Cookie Information")
                            st.markdown('<div class="cookie-info">', unsafe_allow_html=True)
                            st.markdown(f"Number of cookies: {len(parsed_cookies)}")
                            st.markdown("Essential cookies present:")
                            st.markdown("- c_user: ✅" if 'c_user' in parsed_cookies else "- c_user: ❌")
                            st.markdown("- xs: ✅" if 'xs' in parsed_cookies else "- xs: ❌")
                            st.markdown("- fr: ✅" if 'fr' in parsed_cookies else "- fr: ❌")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Please enter your Facebook cookies first")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
