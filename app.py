import streamlit as st
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
import time

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
    .screenshot-container {
        margin-top: 20px;
        padding: 10px;
        border-radius: 8px;
        background-color: white;
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

def setup_driver():
    """Setup and return a configured Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def capture_facebook_page(driver, cookies, url):
    """Capture a screenshot of the Facebook page"""
    try:
        # Navigate to Facebook
        driver.get("https://www.facebook.com")
        
        # Add cookies
        for name, value in cookies.items():
            driver.add_cookie({
                'name': name,
                'value': value,
                'domain': '.facebook.com'
            })
        
        # Navigate to the specified URL
        driver.get(url)
        time.sleep(3)  # Wait for content to load
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_png()
        return Image.open(io.BytesIO(screenshot))
    except Exception as e:
        st.error(f"Error capturing page: {str(e)}")
        return None

def main():
    st.markdown('<h1 class="fb-header">Facebook Viewer with Selenium</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Instructions
        st.markdown("""
        ### How to use:
        1. Enter your Facebook cookies below
        2. Select a page to view
        3. Click 'Capture Page' to see the Facebook content
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
            "Messages": "https://www.facebook.com/messages",
            "Notifications": "https://www.facebook.com/notifications"
        }
        
        selected_page = st.selectbox("Select page to view:", options.keys())
        
        if st.button("Capture Page", type="primary"):
            if cookies_input:
                parsed_cookies = parse_cookies(cookies_input)
                
                with st.spinner("Loading Facebook page..."):
                    driver = setup_driver()
                    try:
                        screenshot = capture_facebook_page(driver, parsed_cookies, options[selected_page])
                        if screenshot:
                            st.markdown('<div class="screenshot-container">', unsafe_allow_html=True)
                            st.image(screenshot, caption=f"Facebook - {selected_page}", use_column_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                    finally:
                        driver.quit()
            else:
                st.error("Please enter your Facebook cookies first")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
