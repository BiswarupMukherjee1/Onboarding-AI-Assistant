"""
Main Application to Use agents and features
"""

import streamlit as st
import sys
import os
import uuid

# Import code
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config

# Import all agents
from agents.orchestrator import OrchestratorAgent
from agents.personalization import PersonalizationAgent
from agents.content_curator import ContentCuratorAgent
from agents.assessment import AssessmentAgent

# Import all features
from features.vr_training import VRTrainingEngine
from features.progress_tracker import ProgressTracker
from features.scheduler import MeetingScheduler
from features.email_automation import EmailAutomation

# Import utilities
from utils.aws_helper import AWSHelper
from utils.data_processor import DataProcessor

# Page config
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px 0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 12px 24px;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize all agents and features
@st.cache_resource
def initialize_system():
    """Initialize all agents and features (cached)"""
    return {
        'orchestrator': OrchestratorAgent(),
        'personalization': PersonalizationAgent(),
        'content_curator': ContentCuratorAgent(),
        'assessment': AssessmentAgent(),
        'vr_training': VRTrainingEngine(),
        'progress_tracker': ProgressTracker(),
        'scheduler': MeetingScheduler(),
        'email_automation': EmailAutomation(),
        'aws_helper': AWSHelper(),
        'data_processor': DataProcessor()
    }

# Get system components
system = initialize_system()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'user_id' not in st.session_state:
    st.session_state.user_id = 'user_demo'  # In production we should use actual auth
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': 'John Doe',
        'role': 'Engineer',
        'department': 'Engineering',
        'experience_level': 'intermediate'
    }
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def main():
    """Main application with navigation"""
    
    st.markdown(f'<h1 class="main-header">🚀 {config.APP_TITLE}</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=PEP+Logo", width=150)
        st.markdown("---")
        
        # User info
        st.markdown(f"**Welcome, {st.session_state.user_profile['name']}!**")
        st.markdown(f"*{st.session_state.user_profile['role']}*")
        st.markdown("---")
        
        # Navigation menu
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'home'
        
        if st.button("💬 Chat Assistant", use_container_width=True):
            st.session_state.current_page = 'chat'
        
        if st.button("🥽 VR Training", use_container_width=True):
            st.session_state.current_page = 'vr'
        
        if st.button("📊 My Progress", use_container_width=True):
            st.session_state.current_page = 'progress'
        
        if st.button("📚 Learning Path", use_container_width=True):
            st.session_state.current_page = 'learning'
        
        if st.button("✅ Assessments", use_container_width=True):
            st.session_state.current_page = 'assessments'
        
        if st.button("📅 Schedule", use_container_width=True):
            st.session_state.current_page = 'schedule'
        
        if st.button("📖 Content Library", use_container_width=True):
            st.session_state.current_page = 'content'
        
        st.markdown("---")
        
        # Get real-time progress from ProgressTracker agent
        progress_data = system['progress_tracker'].get_progress(st.session_state.user_id)
        
        st.markdown("### 📈 Quick Stats")
        st.metric("Progress", f"{progress_data.get('overall_progress', 0)}%", "+5%")
        st.metric("Learning Streak", f"{progress_data.get('learning_streak_days', 0)} days", "+1")
        st.metric("Modules Done", f"{len(progress_data.get('completed_modules', []))}")
    
    # Route to appropriate page
    if st.session_state.current_page == 'home':
        show_home()
    elif st.session_state.current_page == 'chat':
        show_chat()
    elif st.session_state.current_page == 'vr':
        show_vr_training()
    elif st.session_state.current_page == 'progress':
        show_progress()
    elif st.session_state.current_page == 'learning':
        show_learning_path()
    elif st.session_state.current_page == 'assessments':
        show_assessments()
    elif st.session_state.current_page == 'schedule':
        show_schedule()
    elif st.session_state.current_page == 'content':
        show_content_library()

def show_home():
    """Home dashboard using all agents"""
    st.markdown("### Welcome to Your AI-Powered Onboarding Journey! 🎉")
    
    # Get personalized recommendations using PersonalizationAgent
    progress_data = system['progress_tracker'].get_progress(st.session_state.user_id)
    recommendations = system['personalization'].get_recommendations(
        st.session_state.user_id, 
        {'completion_rate': progress_data.get('overall_progress', 0)}
    )
    
    # Show recommendations
    if recommendations:
        st.markdown("### 💡 Personalized Recommendations")
        for rec in recommendations:
            st.info(f"**{rec['type'].upper()}:** {rec['message']}\n\n👉 {rec['action']}")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Chat with AI Assistant", use_container_width=True, key="home_chat"):
            st.session_state.current_page = 'chat'
            st.rerun()
    
    with col2:
        if st.button("🥽 Start VR Training", use_container_width=True, key="home_vr"):
            st.session_state.current_page = 'vr'
            st.rerun()
    
    with col3:
        if st.button("✅ Take Assessment", use_container_width=True, key="home_assess"):
            st.session_state.current_page = 'assessments'
            st.rerun()
    
    st.markdown("---")
    
    # Todays schedule using MeetingScheduler
    st.markdown("### 📅 Today's Schedule")
    meetings = system['scheduler'].get_upcoming_meetings(st.session_state.user_id)
    
    for meeting in meetings[:3]:  # Show first 3
        with st.expander(f"📅 {meeting['title']} - {meeting['time']}"):
            st.write(f"**Date:** {meeting['date']}")
            st.write(f"**Duration:** {meeting['duration']}")
            st.write(f"**Location:** {meeting['location']}")
            if meeting.get('meeting_link'):
                st.markdown(f"[Join Meeting]({meeting['meeting_link']})")

def show_chat():
    """Chat interface using OrchestratorAgent"""
    st.markdown("### 💬 Chat with Your AI Assistant")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your onboarding..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response using OrchestratorAgent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Use personalized response
                result = system['orchestrator'].get_personalized_response(
                    prompt,
                    st.session_state.user_profile,
                    st.session_state.session_id
                )
                
                response = result.get('response', 'Sorry, I encountered an error.')
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

def show_vr_training():
    """VR training using VRTrainingEngine"""
    st.markdown("### 🥽 Immersive VR Training")
    
    # Get available VR experiences
    experiences = system['vr_training'].get_available_vr_experiences()
    
    for exp in experiences:
        with st.expander(f"{exp['title']} - {exp['duration']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{exp['description']}**")
                st.markdown(f"**Difficulty:** {exp['difficulty']}")
                st.markdown(f"**Type:** {exp['type'].upper()}")
                
                st.markdown("**Features:**")
                for feature in exp['features']:
                    st.markdown(f"- {feature}")
            
            with col2:
                st.image(exp['thumbnail'], use_container_width=True)
                
                if exp['status'] == 'available':
                    if st.button(f"Launch {exp['type'].upper()}", key=exp['id']):
                        result = system['vr_training'].launch_vr_experience(
                            exp['id'],
                            st.session_state.user_id
                        )
                        if result['success']:
                            st.success(f" Launching {exp['title']}!")
                            st.info("Follow the on-screen instructions in your VR headset or browser.")
                else:
                    st.info(f"Status: {exp['status']}")

def show_progress():
    """Progress dashboard using ProgressTracker"""
    st.markdown("### 📊 Your Progress Dashboard")
    
    # Get comprehensive analytics
    analytics = system['progress_tracker'].get_analytics_summary(st.session_state.user_id)
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    metrics = analytics['overall_metrics']
    
    col1.metric("Completion Rate", f"{metrics['completion_rate']}%")
    col2.metric("Modules", f"{metrics['modules_completed']}/{analytics['progress_breakdown']['completed'] + analytics['progress_breakdown']['in_progress'] + analytics['progress_breakdown']['upcoming']}")
    col3.metric("Learning Streak", f"{metrics['learning_streak']} days")
    col4.metric("Total Hours", f"{metrics['total_time_hours']} hrs")
    
    st.markdown("---")
    
    # Predictions
    st.markdown("### 🔮 Predictions")
    predictions = analytics['predictions']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Est. Completion Date", predictions['estimated_completion_date'])
    with col2:
        status = " On Track" if predictions['on_track'] else "⚠️ Needs Attention"
        st.metric("Status", status)
    
    st.markdown("---")
    
    # Weekly chart
    st.markdown("### 📈 Weekly Activity")
    chart_data = system['progress_tracker'].get_weekly_chart_data(st.session_state.user_id)
    
    import plotly.graph_objects as go
    fig = go.Figure(data=[
        go.Bar(name='Modules Completed', x=chart_data['labels'], y=chart_data['completed_modules'])
    ])
    fig.update_layout(title="Weekly Progress")
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    for rec in analytics['recommendations']:
        st.info(f"**{rec['type'].upper()}:** {rec['message']}\n\n👉 {rec['action']}")

def show_learning_path():
    """Learning path using PersonalizationAgent"""
    st.markdown("### 📚 Your Personalized Learning Path")
    
    # Get personalized learning path
    learning_path = system['personalization'].create_learning_path(st.session_state.user_profile)
    
    st.info(f"**Estimated Total Time:** {learning_path['estimated_completion']}")
    
    # Display modules
    progress_data = system['progress_tracker'].get_progress(st.session_state.user_id)
    completed = progress_data.get('completed_modules', [])
    
    for i, module in enumerate(learning_path['learning_path']):
        is_completed = module['module'] in completed
        status_icon = "✅" if is_completed else "⏳"
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"{status_icon} **{module['module']}**")
        with col2:
            st.markdown(f"`{module['duration']}`")
        with col3:
            st.markdown(f"*{module['priority']}*")

def show_assessments():
    """Assessments using AssessmentAgent"""
    st.markdown("### Skills Assessments")
    
    # Get available assessments
    assessments = system['assessment'].get_available_assessments(
        st.session_state.user_profile['role']
    )
    
    for assess in assessments:
        with st.expander(f"{'✅' if assess['status'] == 'completed' else '📝' if assess['status'] == 'available' else '🔒'} {assess['name']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Duration:** {assess['duration']}")
                st.markdown(f"**Questions:** {assess['questions']}")
                st.markdown(f"**Difficulty:** {assess['difficulty']}")
            
            with col2:
                if assess['status'] == 'available':
                    if st.button("Start Assessment", key=assess['id']):
                        st.session_state.current_assessment = assess['id']
                        st.success("Starting assessment...")
                elif assess['status'] == 'locked':
                    st.info("Complete prerequisites first")

def show_schedule():
    """Schedule management using MeetingScheduler"""
    st.markdown("### 📅 Meeting Schedule")
    
    # Get upcoming meetings
    meetings = system['scheduler'].get_upcoming_meetings(st.session_state.user_id)
    
    for meeting in meetings:
        with st.expander(f"📅 {meeting['title']} - {meeting['date']} at {meeting['time']}"):
            st.markdown(f"**Duration:** {meeting['duration']}")
            st.markdown(f"**Attendees:** {', '.join(meeting['attendees'])}")
            st.markdown(f"**Location:** {meeting['location']}")
            st.markdown(f"**Type:** {meeting['type']}")
            
            if meeting.get('meeting_link'):
                st.markdown(f"[Join Meeting]({meeting['meeting_link']})")

def show_content_library():
    """Content library using ContentCuratorAgent"""
    st.markdown("### 📖 Content Library")
    
    # Search functionality
    search_query = st.text_input("🔍 Search content...")
    
    if search_query:
        results = system['content_curator'].search_content(search_query)
        st.markdown(f"**Found {len(results)} results:**")
        for item in results:
            st.markdown(f"- {item['name']} ({item['type']}) - {item['duration']}")
    else:
        # Show categories
        categories = ['company_culture', 'technical', 'policies', 'tools']
        
        for cat in categories:
            content = system['content_curator'].get_content_by_category(cat)
            if content:
                with st.expander(f"📁 {content['title']}"):
                    for item in content['items']:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"📄 {item['name']}")
                        with col2:
                            st.markdown(f"`{item['type']}`")
                        with col3:
                            st.markdown(f"`{item['duration']}`")

if __name__ == "__main__":
    main()
