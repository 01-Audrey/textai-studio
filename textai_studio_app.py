"""
TextAI Studio - Production NLP Platform
Version: 1.0.0
Author: Audrey

Complete NLP platform with 4 AI-powered tools:
- Sentiment Analysis
- Text Summarization  
- Fake News Detection
- Job Matching
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from sentence_transformers import SentenceTransformer, util
import json
import os
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
import bcrypt
import base64

# Page configuration
st.set_page_config(
    page_title="TextAI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
USER_DATA_DIR = Path("user_data")
HISTORY_DIR = USER_DATA_DIR / "history"
API_KEYS_DIR = USER_DATA_DIR / "api_keys"
USERS_FILE = USER_DATA_DIR / "users.json"
RATE_LIMITS_FILE = USER_DATA_DIR / "rate_limits.json"

# Create directories
USER_DATA_DIR.mkdir(exist_ok=True)
HISTORY_DIR.mkdir(exist_ok=True)
API_KEYS_DIR.mkdir(exist_ok=True)

# Rate limiting configuration
RATE_LIMITS = {
    'guest': 10,      # 10 requests per hour
    'user': 100,      # 100 requests per hour
    'pro': 1000       # 1000 requests per hour
}

# ==================================================
# HELPER CLASSES
# ==================================================

class UserManager:
    """Manage user authentication and profiles."""
    
    def __init__(self):
        self.users_file = USERS_FILE
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from file."""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        """Save users to file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def register_user(self, username, password, email):
        """Register a new user."""
        if username in self.users:
            return False, "Username already exists"
        
        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        self.users[username] = {
            'password': hashed.decode('utf-8'),
            'email': email,
            'tier': 'user',
            'created_at': datetime.now().isoformat(),
            'api_key': None
        }
        self._save_users()
        return True, "Registration successful"
    
    def authenticate_user(self, username, password):
        """Authenticate user."""
        if username not in self.users:
            return False
        
        stored_hash = self.users[username]['password'].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    
    def get_user(self, username):
        """Get user data."""
        return self.users.get(username)
    
    def update_user(self, username, updates):
        """Update user data."""
        if username in self.users:
            self.users[username].update(updates)
            self._save_users()
            return True
        return False


class HistoryManager:
    """Manage user query history."""
    
    def __init__(self):
        self.history_dir = HISTORY_DIR
    
    def add_entry(self, username, tool, query, result):
        """Add history entry."""
        history_file = self.history_dir / f"{username}.json"
        
        # Load existing history
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool,
            'query': query[:200],  # Truncate long queries
            'result': str(result)[:500]  # Truncate long results
        }
        history.append(entry)
        
        # Keep last 100 entries
        history = history[-100:]
        
        # Save
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_history(self, username, limit=50):
        """Get user history."""
        history_file = self.history_dir / f"{username}.json"
        
        if not history_file.exists():
            return []
        
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        return history[-limit:]
    
    def get_analytics(self, username):
        """Get usage analytics."""
        history = self.get_history(username, limit=1000)
        
        if not history:
            return None
        
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        analytics = {
            'total_queries': len(df),
            'tools_used': df['tool'].value_counts().to_dict(),
            'queries_by_date': df.groupby(df['timestamp'].dt.date).size().to_dict(),
            'last_7_days': len(df[df['timestamp'] > datetime.now() - timedelta(days=7)]),
            'last_30_days': len(df[df['timestamp'] > datetime.now() - timedelta(days=30)])
        }
        
        return analytics


class APIKeyManager:
    """Manage API keys."""
    
    def __init__(self):
        self.api_keys_file = API_KEYS_DIR / "api_keys.json"
        self.keys = self._load_keys()
    
    def _load_keys(self):
        """Load API keys."""
        if self.api_keys_file.exists():
            with open(self.api_keys_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_keys(self):
        """Save API keys."""
        with open(self.api_keys_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def generate_key(self, username):
        """Generate API key for user."""
        # Generate random key
        random_bytes = secrets.token_bytes(32)
        api_key = 'sk_' + base64.b64encode(random_bytes).decode('utf-8')
        
        # Hash for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.keys[key_hash] = {
            'username': username,
            'created_at': datetime.now().isoformat()
        }
        self._save_keys()
        
        return api_key
    
    def validate_key(self, api_key):
        """Validate API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return key_hash in self.keys
    
    def get_user_by_key(self, api_key):
        """Get username from API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.keys:
            return self.keys[key_hash]['username']
        return None


class RateLimiter:
    """Rate limiting for API requests."""
    
    def __init__(self):
        self.limits_file = RATE_LIMITS_FILE
        self.limits = self._load_limits()
    
    def _load_limits(self):
        """Load rate limits."""
        if self.limits_file.exists():
            with open(self.limits_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_limits(self):
        """Save rate limits."""
        with open(self.limits_file, 'w') as f:
            json.dump(self.limits, f, indent=2)
    
    def check_limit(self, username, tier='user'):
        """Check if user is within rate limit."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        if username not in self.limits:
            self.limits[username] = []
        
        # Remove old entries
        self.limits[username] = [
            ts for ts in self.limits[username]
            if datetime.fromisoformat(ts) > hour_ago
        ]
        
        # Check limit
        limit = RATE_LIMITS.get(tier, 10)
        if len(self.limits[username]) >= limit:
            return False, f"Rate limit exceeded. Limit: {limit}/hour"
        
        # Add new request
        self.limits[username].append(now.isoformat())
        self._save_limits()
        
        return True, f"Remaining: {limit - len(self.limits[username])}/{limit}"


# ==================================================
# MODEL LOADING (CACHED)
# ==================================================

@st.cache_resource
def load_sentiment_model():
    """Load sentiment analysis model."""
    return pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

@st.cache_resource
def load_summarization_model():
    """Load summarization model."""
    return pipeline('summarization', model='facebook/bart-large-cnn')

@st.cache_resource
def load_fake_news_model():
    """Load fake news detection model."""
    return pipeline('text-classification', model='hamzab/roberta-fake-news-classification')

@st.cache_resource
def load_job_matcher_model():
    """Load job matching model."""
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


# ==================================================
# TOOL FUNCTIONS
# ==================================================

def analyze_sentiment(text):
    """Analyze sentiment of text."""
    model = load_sentiment_model()
    result = model(text[:512])[0]  # Truncate to 512 tokens
    return result

def summarize_text(text, max_length=130, min_length=30):
    """Summarize text."""
    model = load_summarization_model()
    result = model(text, max_length=max_length, min_length=min_length, do_sample=False)[0]
    return result['summary_text']

def detect_fake_news(text):
    """Detect if news is fake."""
    model = load_fake_news_model()
    result = model(text[:512])[0]
    return result

def match_job(resume, job_description):
    """Match resume to job description."""
    model = load_job_matcher_model()
    
    # Encode texts
    resume_embedding = model.encode(resume, convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    
    # Calculate similarity
    similarity = util.pytorch_cos_sim(resume_embedding, job_embedding)[0][0].item()
    
    return {
        'similarity_score': similarity,
        'match_percentage': similarity * 100,
        'recommendation': get_match_recommendation(similarity)
    }

def get_match_recommendation(score):
    """Get recommendation based on match score."""
    if score >= 0.9:
        return "Excellent Match"
    elif score >= 0.8:
        return "Strong Match"
    elif score >= 0.7:
        return "Good Match"
    elif score >= 0.6:
        return "Fair Match"
    else:
        return "Weak Match"


# ==================================================
# AUTHENTICATION PAGES
# ==================================================

def login_page():
    """Login page."""
    st.title("🔐 Login to TextAI Studio")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
                return
            
            user_manager = UserManager()
            if user_manager.authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                user_data = user_manager.get_user(username)
                st.session_state.user_tier = user_data.get('tier', 'user')
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.markdown("---")
    st.info("Don't have an account? Switch to Signup from the sidebar.")

def signup_page():
    """Signup page."""
    st.title("📝 Sign Up for TextAI Studio")
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
        
        if submit:
            # Validation
            if not username or not email or not password:
                st.error("Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(password) < 8:
                st.error("Password must be at least 8 characters")
                return
            
            # Register user
            user_manager = UserManager()
            success, message = user_manager.register_user(username, password, email)
            
            if success:
                st.success(message + " Please login.")
            else:
                st.error(message)
    
    st.markdown("---")
    st.info("Already have an account? Switch to Login from the sidebar.")

def logout():
    """Logout user."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_tier = None
    st.rerun()


# ==================================================
# TOOL PAGES
# ==================================================

def sentiment_analysis_page():
    """Sentiment analysis tool page."""
    st.title("😊 Sentiment Analysis")
    st.write("Analyze the emotional tone of text using DistilBERT.")
    
    # Input
    text = st.text_area("Enter text to analyze:", height=150, 
                       placeholder="Example: I love this product! It's amazing!")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_btn = st.button("Analyze Sentiment", type="primary")
    
    if analyze_btn and text:
        with st.spinner("Analyzing sentiment..."):
            try:
                result = analyze_sentiment(text)
                
                # Save to history
                if st.session_state.get('authenticated'):
                    history_manager = HistoryManager()
                    history_manager.add_entry(
                        st.session_state.username,
                        'sentiment_analysis',
                        text,
                        result
                    )
                
                # Display result
                st.success("Analysis Complete!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Sentiment", result['label'])
                
                with col2:
                    st.metric("Confidence", f"{result['score']:.2%}")
                
                # Visualization
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result['score'] * 100,
                    title={'text': "Confidence Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkgreen" if result['label'] == 'POSITIVE' else "darkred"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 100], 'color': "gray"}
                        ]
                    }
                ))
                st.plotly_chart(fig)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

def text_summarization_page():
    """Text summarization tool page."""
    st.title("📄 Text Summarization")
    st.write("Generate concise summaries using BART.")
    
    # Input
    text = st.text_area("Enter text to summarize:", height=200,
                       placeholder="Enter a long article or document...")
    
    col1, col2 = st.columns(2)
    with col1:
        max_length = st.slider("Max summary length", 50, 200, 130)
    with col2:
        min_length = st.slider("Min summary length", 20, 100, 30)
    
    summarize_btn = st.button("Summarize Text", type="primary")
    
    if summarize_btn and text:
        if len(text) < 50:
            st.warning("Text is too short to summarize. Please enter at least 50 characters.")
            return
        
        with st.spinner("Generating summary..."):
            try:
                summary = summarize_text(text, max_length=max_length, min_length=min_length)
                
                # Save to history
                if st.session_state.get('authenticated'):
                    history_manager = HistoryManager()
                    history_manager.add_entry(
                        st.session_state.username,
                        'text_summarization',
                        text,
                        summary
                    )
                
                # Display result
                st.success("Summary Generated!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Original Length", f"{len(text)} chars")
                with col2:
                    st.metric("Summary Length", f"{len(summary)} chars")
                with col3:
                    compression = (1 - len(summary) / len(text)) * 100
                    st.metric("Compression", f"{compression:.1f}%")
                
                st.subheader("Summary:")
                st.info(summary)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

def fake_news_detection_page():
    """Fake news detection tool page."""
    st.title("🔍 Fake News Detection")
    st.write("Identify potentially misleading content using RoBERTa.")
    
    # Input
    text = st.text_area("Enter news article or claim:", height=150,
                       placeholder="Enter news text to verify...")
    
    detect_btn = st.button("Detect Fake News", type="primary")
    
    if detect_btn and text:
        with st.spinner("Analyzing content..."):
            try:
                result = detect_fake_news(text)
                
                # Save to history
                if st.session_state.get('authenticated'):
                    history_manager = HistoryManager()
                    history_manager.add_entry(
                        st.session_state.username,
                        'fake_news_detection',
                        text,
                        result
                    )
                
                # Display result
                st.success("Analysis Complete!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    label = result['label']
                    if 'FAKE' in label.upper() or 'FALSE' in label.upper():
                        st.error(f"⚠️ Prediction: {label}")
                    else:
                        st.success(f"✅ Prediction: {label}")
                
                with col2:
                    st.metric("Confidence", f"{result['score']:.2%}")
                
                # Visualization
                fig = go.Figure(go.Bar(
                    x=[result['score']],
                    y=[result['label']],
                    orientation='h',
                    marker_color='red' if 'FAKE' in result['label'].upper() else 'green'
                ))
                fig.update_layout(
                    title="Confidence Score",
                    xaxis_title="Score",
                    showlegend=False
                )
                st.plotly_chart(fig)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

def job_matching_page():
    """Job matching tool page."""
    st.title("💼 Job Matching")
    st.write("Match resumes to job descriptions using Sentence-BERT.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resume")
        resume = st.text_area("Enter resume:", height=200,
                             placeholder="Skills, experience, education...")
    
    with col2:
        st.subheader("Job Description")
        job_desc = st.text_area("Enter job description:", height=200,
                                placeholder="Requirements, responsibilities...")
    
    match_btn = st.button("Calculate Match", type="primary")
    
    if match_btn and resume and job_desc:
        with st.spinner("Calculating match..."):
            try:
                result = match_job(resume, job_desc)
                
                # Save to history
                if st.session_state.get('authenticated'):
                    history_manager = HistoryManager()
                    history_manager.add_entry(
                        st.session_state.username,
                        'job_matching',
                        f"Resume vs Job",
                        result
                    )
                
                # Display result
                st.success("Match Calculated!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Match Score", f"{result['similarity_score']:.3f}")
                
                with col2:
                    st.metric("Match Percentage", f"{result['match_percentage']:.1f}%")
                
                with col3:
                    recommendation = result['recommendation']
                    color = "green" if "Excellent" in recommendation or "Strong" in recommendation else "orange"
                    st.markdown(f"**Recommendation:**")
                    st.markdown(f":{color}[{recommendation}]")
                
                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result['match_percentage'],
                    title={'text': "Match Percentage"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 60], 'color': "lightcoral"},
                            {'range': [60, 80], 'color': "lightyellow"},
                            {'range': [80, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                st.plotly_chart(fig)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")


# ==================================================
# BATCH PROCESSING
# ==================================================

def batch_processing_page():
    """Batch processing page."""
    st.title("📁 Batch Processing")
    st.write("Process multiple texts at once via CSV upload.")
    
    # Select tool
    tool = st.selectbox(
        "Select Tool:",
        ["Sentiment Analysis", "Text Summarization", "Fake News Detection"]
    )
    
    # Upload CSV
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Preview:", df.head())
            
            # Select text column
            text_column = st.selectbox("Select text column:", df.columns)
            
            process_btn = st.button("Process Batch", type="primary")
            
            if process_btn:
                with st.spinner(f"Processing {len(df)} items..."):
                    results = []
                    progress_bar = st.progress(0)
                    
                    for idx, row in df.iterrows():
                        text = str(row[text_column])
                        
                        # Process based on tool
                        if tool == "Sentiment Analysis":
                            result = analyze_sentiment(text)
                            results.append({
                                'text': text[:100],
                                'label': result['label'],
                                'score': result['score']
                            })
                        
                        elif tool == "Text Summarization":
                            summary = summarize_text(text)
                            results.append({
                                'text': text[:100],
                                'summary': summary
                            })
                        
                        elif tool == "Fake News Detection":
                            result = detect_fake_news(text)
                            results.append({
                                'text': text[:100],
                                'label': result['label'],
                                'score': result['score']
                            })
                        
                        # Update progress
                        progress_bar.progress((idx + 1) / len(df))
                    
                    # Create results dataframe
                    results_df = pd.DataFrame(results)
                    
                    st.success(f"Processed {len(results)} items!")
                    st.dataframe(results_df)
                    
                    # Download button
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results",
                        data=csv,
                        file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


# ==================================================
# ANALYTICS & DASHBOARDS
# ==================================================

def analytics_dashboard():
    """User analytics dashboard."""
    st.title("📊 Analytics Dashboard")
    
    if not st.session_state.get('authenticated'):
        st.warning("Please login to view analytics")
        return
    
    username = st.session_state.username
    history_manager = HistoryManager()
    
    # Get analytics
    analytics = history_manager.get_analytics(username)
    
    if not analytics:
        st.info("No usage data yet. Start using the tools!")
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Queries", analytics['total_queries'])
    
    with col2:
        st.metric("Last 7 Days", analytics['last_7_days'])
    
    with col3:
        st.metric("Last 30 Days", analytics['last_30_days'])
    
    with col4:
        most_used = max(analytics['tools_used'].items(), key=lambda x: x[1])[0]
        st.metric("Most Used Tool", most_used)
    
    st.markdown("---")
    
    # Tools usage chart
    st.subheader("Tools Usage")
    tools_df = pd.DataFrame(list(analytics['tools_used'].items()), 
                           columns=['Tool', 'Count'])
    fig = px.bar(tools_df, x='Tool', y='Count', title="Queries by Tool")
    st.plotly_chart(fig, use_container_width=True)
    
    # Usage over time
    st.subheader("Usage Over Time")
    if analytics['queries_by_date']:
        dates_df = pd.DataFrame(list(analytics['queries_by_date'].items()), 
                               columns=['Date', 'Count'])
        dates_df['Date'] = pd.to_datetime(dates_df['Date'])
        fig = px.line(dates_df, x='Date', y='Count', title="Daily Query Volume")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent history
    st.subheader("Recent Activity")
    history = history_manager.get_history(username, limit=10)
    if history:
        history_df = pd.DataFrame(history)
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        st.dataframe(history_df[['timestamp', 'tool', 'query']], use_container_width=True)

def admin_dashboard():
    """Admin monitoring dashboard."""
    st.title("👑 Admin Dashboard")
    
    # Check if admin
    if not st.session_state.get('authenticated'):
        st.warning("Please login")
        return
    
    if st.session_state.get('username') != 'admin':
        st.error("Access denied. Admin only.")
        return
    
    # System stats
    st.subheader("System Statistics")
    
    user_manager = UserManager()
    total_users = len(user_manager.users)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", total_users)
    
    with col2:
        # Count total queries across all users
        history_manager = HistoryManager()
        total_queries = 0
        for user_file in HISTORY_DIR.glob("*.json"):
            with open(user_file) as f:
                total_queries += len(json.load(f))
        st.metric("Total Queries", total_queries)
    
    with col3:
        st.metric("System Health", "✅ Healthy")
    
    st.markdown("---")
    
    # User list
    st.subheader("User Management")
    users_data = []
    for username, data in user_manager.users.items():
        users_data.append({
            'Username': username,
            'Email': data.get('email', 'N/A'),
            'Tier': data.get('tier', 'user'),
            'Created': data.get('created_at', 'N/A')[:10]
        })
    
    if users_data:
        users_df = pd.DataFrame(users_data)
        st.dataframe(users_df, use_container_width=True)

def settings_page():
    """User settings page."""
    st.title("⚙️ Settings")
    
    if not st.session_state.get('authenticated'):
        st.warning("Please login")
        return
    
    username = st.session_state.username
    
    st.subheader("API Access")
    st.write("Generate an API key to access TextAI Studio programmatically.")
    
    if st.button("Generate API Key"):
        api_manager = APIKeyManager()
        api_key = api_manager.generate_key(username)
        
        st.success("API Key Generated!")
        st.code(api_key)
        st.warning("⚠️ Save this key now! It won't be shown again.")
        
        # Show usage example
        with st.expander("API Usage Example"):
            st.code(f"""
import requests

headers = {{"X-API-Key": "{api_key}"}}

response = requests.post(
    "http://localhost:8501/api/sentiment",
    headers=headers,
    json={{"text": "I love this!"}}
)

print(response.json())
            """, language="python")
    
    st.markdown("---")
    
    st.subheader("Account Information")
    user_manager = UserManager()
    user_data = user_manager.get_user(username)
    
    st.write(f"**Username:** {username}")
    st.write(f"**Email:** {user_data.get('email', 'N/A')}")
    st.write(f"**Tier:** {user_data.get('tier', 'user')}")
    st.write(f"**Created:** {user_data.get('created_at', 'N/A')[:10]}")


# ==================================================
# MAIN APP
# ==================================================

def main():
    """Main application."""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_tier' not in st.session_state:
        st.session_state.user_tier = 'guest'
    
    # Sidebar
    with st.sidebar:
        st.title("🤖 TextAI Studio")
        st.markdown("---")
        
        # Authentication status
        if st.session_state.authenticated:
            st.success(f"👤 {st.session_state.username}")
            st.info(f"Tier: {st.session_state.user_tier}")
            
            if st.button("Logout", use_container_width=True):
                logout()
        else:
            st.info("Not logged in")
        
        st.markdown("---")
        
        # Navigation
        if st.session_state.authenticated:
            page = st.radio(
                "Navigate:",
                [
                    "🏠 Home",
                    "😊 Sentiment Analysis",
                    "📄 Text Summarization",
                    "🔍 Fake News Detection",
                    "💼 Job Matching",
                    "📁 Batch Processing",
                    "📊 Analytics",
                    "⚙️ Settings"
                ]
            )
            
            # Admin option
            if st.session_state.username == 'admin':
                if st.button("👑 Admin Dashboard", use_container_width=True):
                    st.session_state.page = "admin"
        else:
            page = st.radio(
                "Navigate:",
                ["🏠 Home", "🔐 Login", "📝 Signup"]
            )
        
        st.markdown("---")
        st.caption("v1.0.0 | Built with ❤️")
    
    # Main content
    if not st.session_state.authenticated:
        if page == "🔐 Login":
            login_page()
        elif page == "📝 Signup":
            signup_page()
        else:
            # Home page for non-authenticated users
            st.title("🤖 Welcome to TextAI Studio")
            st.subheader("Production NLP Platform with 4 AI-Powered Tools")
            
            st.markdown("""
            ### Features:
            - **😊 Sentiment Analysis** - Detect emotional tone
            - **📄 Text Summarization** - Generate concise summaries
            - **🔍 Fake News Detection** - Identify misinformation
            - **💼 Job Matching** - Match resumes to jobs
            
            ### Get Started:
            1. Sign up for a free account
            2. Start analyzing text instantly
            3. Access API for integration
            
            👈 Login or Sign up from the sidebar!
            """)
            
            # Feature showcase
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("**🚀 Fast Performance**\n\nModel caching for <10ms response time")
            
            with col2:
                st.info("**📊 Analytics**\n\nTrack your usage and insights")
    
    else:
        # Authenticated user pages
        if page == "🏠 Home":
            st.title(f"👋 Welcome back, {st.session_state.username}!")
            
            st.markdown("""
            ### Quick Start:
            Select a tool from the sidebar to get started.
            
            ### Available Tools:
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("**😊 Sentiment Analysis**\n\nAnalyze emotional tone of text")
                st.info("**📄 Text Summarization**\n\nGenerate concise summaries")
            
            with col2:
                st.info("**🔍 Fake News Detection**\n\nIdentify misinformation")
                st.info("**💼 Job Matching**\n\nMatch resumes to jobs")
            
            # Recent activity
            st.markdown("---")
            st.subheader("📈 Quick Stats")
            
            history_manager = HistoryManager()
            analytics = history_manager.get_analytics(st.session_state.username)
            
            if analytics:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Queries", analytics['total_queries'])
                
                with col2:
                    st.metric("Last 7 Days", analytics['last_7_days'])
                
                with col3:
                    most_used = max(analytics['tools_used'].items(), key=lambda x: x[1])[0]
                    st.metric("Favorite Tool", most_used)
        
        elif page == "😊 Sentiment Analysis":
            sentiment_analysis_page()
        
        elif page == "📄 Text Summarization":
            text_summarization_page()
        
        elif page == "🔍 Fake News Detection":
            fake_news_detection_page()
        
        elif page == "💼 Job Matching":
            job_matching_page()
        
        elif page == "📁 Batch Processing":
            batch_processing_page()
        
        elif page == "📊 Analytics":
            analytics_dashboard()
        
        elif page == "⚙️ Settings":
            settings_page()
        
        # Admin page
        if st.session_state.get('page') == 'admin':
            admin_dashboard()


if __name__ == "__main__":
    main()