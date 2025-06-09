import streamlit as st
import asyncio
import uuid
import time
from typing import Dict, Any, Optional
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.profile_analyzer import ProfileAnalyzerAgent
from src.agents.job_matcher import JobMatcherAgent
from src.agents.content_generator import ContentGeneratorAgent
from src.agents.career_counselor import CareerCounselorAgent
from src.agents.memory_manager import MemoryManagerAgent
from src.services.linkedin_scraper import LinkedInScraperService
from src.services.gemini_client import GeminiClient
from src.config.settings import settings

class LinkedInEnhancerApp:
    def __init__(self):
        self.settings = settings
        self.initialize_services()
        self.initialize_agents()
        
    def initialize_services(self):
        """Initialize external services"""
        try:
            # Validate settings first
            self.settings.validate_settings()
            
            self.gemini_client = GeminiClient(self.settings.GEMINI_API_KEY)
            self.linkedin_scraper = LinkedInScraperService(self.settings.APIFY_API_TOKEN)
            self.memory_manager = MemoryManagerAgent("./data/memory_store")
        except Exception as e:
            st.error(f"Failed to initialize services: {e}")
            raise
        
    def initialize_agents(self):
        """Initialize AI agents"""
        try:
            self.profile_analyzer = ProfileAnalyzerAgent(
                self.gemini_client, 
                self.memory_manager
            )
            self.job_matcher = JobMatcherAgent(
                self.gemini_client, 
                self.memory_manager
            )
            self.content_generator = ContentGeneratorAgent(
                self.gemini_client, 
                self.memory_manager
            )
            self.career_counselor = CareerCounselorAgent(
                self.gemini_client, 
                self.memory_manager
            )
        except Exception as e:
            st.error(f"Failed to initialize agents: {e}")
            raise
        
    def render_ui(self):
        """Render the main application UI"""
        st.set_page_config(
            page_title="LinkedIn Enhancer",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session state
        self.initialize_session_state()
        
        # Header
        st.title("🚀 LinkedIn Enhancer")
        st.markdown("**AI-Powered LinkedIn Profile Optimization & Career Guidance**")
        
        # Sidebar for profile input
        self.render_sidebar()
        
        # Main chat interface
        self.render_chat_interface()
        
    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "user_id" not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        if "profile_data" not in st.session_state:
            st.session_state.profile_data = None
        if "profile_analyzed" not in st.session_state:
            st.session_state.profile_analyzed = False
        if "processing" not in st.session_state:
            st.session_state.processing = False
        if "pending_query" not in st.session_state:
            st.session_state.pending_query = None
            
    def render_sidebar(self):
        """Render sidebar with profile input"""
        with st.sidebar:
            st.header("Profile Setup")
            
            # Profile status
            if st.session_state.profile_data:
                st.success("✅ Profile loaded successfully!")
                profile = st.session_state.profile_data
                st.write(f"**Name:** {profile.get('full_name', 'N/A')}")
                st.write(f"**Headline:** {profile.get('headline', 'N/A')}")
                
                if st.button("🔄 Load New Profile", key="new_profile_btn"):
                    st.session_state.profile_data = None
                    st.session_state.profile_analyzed = False
                    st.session_state.messages = []
                    st.rerun()
            else:
                st.info("👆 Enter your LinkedIn profile URL to get started")
            
            # Profile URL input
            linkedin_url = st.text_input(
                "LinkedIn Profile URL",
                placeholder="https://linkedin.com/in/your-profile",
                help="Enter your LinkedIn profile URL to analyze"
            )
            
            analyze_button = st.button(
                "🔍 Analyze Profile", 
                type="primary",
                disabled=not linkedin_url or st.session_state.processing,
                key="analyze_btn"
            )
            
            if analyze_button and linkedin_url:
                asyncio.run(self.process_linkedin_profile(linkedin_url))
            
            # Quick actions
            if st.session_state.profile_data:
                st.divider()
                st.subheader("Quick Actions")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Profile Analysis", key="quick_analysis", disabled=st.session_state.processing):
                        st.session_state.pending_query = "Please provide a comprehensive analysis of my LinkedIn profile including strengths, weaknesses, and improvement suggestions."
                        st.rerun()
                
                with col2:
                    if st.button("🎯 Job Matching", key="quick_jobs", disabled=st.session_state.processing):
                        st.session_state.pending_query = "Based on my profile, what job opportunities would be the best match for me?"
                        st.rerun()
                
                col3, col4 = st.columns(2)
                with col3:
                    if st.button("✍️ Content Ideas", key="quick_content", disabled=st.session_state.processing):
                        st.session_state.pending_query = "Generate content ideas for my LinkedIn posts to increase engagement."
                        st.rerun()
                
                with col4:
                    if st.button("🎯 Career Advice", key="quick_career", disabled=st.session_state.processing):
                        st.session_state.pending_query = "What career development advice do you have based on my current profile?"
                        st.rerun()
                
                # Enhanced Features Section
                st.divider()
                st.subheader("🚀 Enhanced Features")
                
                # Job Description Input for Job Fit Analysis
                job_description = st.text_area(
                    "Job Description (Optional)",
                    placeholder="Paste a job description here to get detailed job fit analysis...",
                    height=100,
                    help="Paste a job description to compare your profile against specific roles"
                )
                
                if st.button("🔍 Job Fit Analysis", key="job_fit_btn", disabled=st.session_state.processing):
                    if job_description.strip():
                        st.session_state.pending_query = f"Analyze how well my profile matches this job description and provide detailed insights and improvement suggestions:\n\n{job_description}"
                    else:
                        st.session_state.pending_query = "Analyze my profile for general job market fit and suggest improvements to make me more attractive to recruiters."
                    st.rerun()
                
                # Content Enhancement
                content_section = st.selectbox(
                    "Content Enhancement Section",
                    ["About Section", "Headline", "Experience Descriptions", "Skills Section"],
                    help="Select which section you'd like to enhance"
                )
                
                if st.button("✨ Enhance Content", key="enhance_content_btn", disabled=st.session_state.processing):
                    st.session_state.pending_query = f"Please rewrite and enhance my {content_section} for better alignment with industry best practices and to make it more compelling to recruiters."
                    st.rerun()
                
                # Skill Gap Analysis
                target_role = st.text_input(
                    "Target Role (Optional)",
                    placeholder="e.g., Senior Data Scientist, Product Manager...",
                    help="Enter your target role for skill gap analysis"
                )
                
                if st.button("🎯 Skill Gap Analysis", key="skill_gap_btn", disabled=st.session_state.processing):
                    if target_role.strip():
                        st.session_state.pending_query = f"Perform a detailed skill gap analysis for the role of '{target_role}'. Identify missing skills I need to develop and suggest specific learning resources and career paths."
                    else:
                        st.session_state.pending_query = "Analyze my current skills and identify gaps that are preventing me from getting more recruiter attention. Suggest specific areas for improvement and learning resources."
                    st.rerun()
            
            # Help section
            st.divider()
            st.subheader("How to Use")
            st.markdown("""
            1. **Enter your LinkedIn URL** above
            2. **Click 'Analyze Profile'** to load your data
            3. **Use Quick Actions** for instant insights
            4. **Try Enhanced Features** for detailed analysis:
               - **Job Fit Analysis**: Compare against specific jobs
               - **Content Enhancement**: Improve profile sections
               - **Skill Gap Analysis**: Identify missing skills
            5. **Chat directly** for custom questions
            """)
            
            # Debug section
            st.divider()
            debug_mode = st.checkbox("🐛 Debug Mode", help="Show debug information")
            if debug_mode:
                st.subheader("Debug Info")
                st.write("**Environment Variables:**")
                st.write(f"- GEMINI_API_KEY: {'✅ Set' if self.settings.GEMINI_API_KEY else '❌ Missing'}")
                st.write(f"- APIFY_API_TOKEN: {'✅ Set' if self.settings.APIFY_API_TOKEN else '❌ Missing'}")
                
                st.write("**Session State:**")
                st.write(f"- User ID: {st.session_state.user_id}")
                st.write(f"- Profile Data: {'✅ Loaded' if st.session_state.profile_data else '❌ Not loaded'}")
                st.write(f"- Messages Count: {len(st.session_state.messages)}")
                st.write(f"- Processing: {st.session_state.processing}")
                st.write(f"- Pending Query: {st.session_state.pending_query is not None}")
                
                if st.button("🔄 Clear All Data", help="Reset all session data"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        
        # Process pending query from Quick Actions
        if st.session_state.pending_query and not st.session_state.processing:
            query = st.session_state.pending_query
            st.session_state.pending_query = None
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Process the query
            asyncio.run(self.process_and_display_response(query))
        
        # Welcome message
        if not st.session_state.messages and not st.session_state.profile_data:
            st.markdown("""
            ### Welcome to LinkedIn Enhancer! 👋
            
            I'm your AI-powered LinkedIn optimization assistant. Here's how I can help you:
            
            🔍 **Profile Analysis** - Get detailed insights on your LinkedIn profile completeness and areas for improvement
            
            🎯 **Job Matching** - Find relevant job opportunities and understand how well your profile matches them
            
            ✍️ **Content Generation** - Create compelling About sections, headlines, and post ideas
            
            💼 **Career Counseling** - Receive personalized career advice and development suggestions
            
            🚀 **Enhanced Features**:
            - **Job Fit Analysis** - Compare your profile against specific job descriptions
            - **Content Enhancement** - Rewrite profile sections with industry best practices
            - **Skill Gap Analysis** - Identify missing skills and get learning recommendations
            
            **To get started:** Enter your LinkedIn profile URL in the sidebar and click "Analyze Profile"
            """)
            return
        
        # Chat messages container
        chat_container = st.container()
        
        with chat_container:
            # Display chat messages
            for i, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input(
            "Ask me about profile optimization, job matching, content creation, or career advice...",
            disabled=st.session_state.processing
        ):
            if st.session_state.processing:
                st.warning("Please wait for the current response to complete.")
                return
                
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Process the query
            asyncio.run(self.process_and_display_response(prompt))
    
    async def process_and_display_response(self, query: str):
        """Process query and display response in real-time"""
        try:
            st.session_state.processing = True
            
            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(query)
            
            # Generate and display assistant response
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.write("🤔 Thinking...")
                
                response = await self.process_user_query(query)
                response_placeholder.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            with st.chat_message("assistant"):
                st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        finally:
            st.session_state.processing = False
            st.rerun()

    async def process_linkedin_profile(self, linkedin_url: str):
        """Process LinkedIn profile URL"""
        try:
            st.session_state.processing = True
            
            # Show progress with more detailed steps
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Initializing LinkedIn scraper...")
            progress_bar.progress(20)
            
            # Scrape profile
            status_text.text("📊 Scraping LinkedIn profile data...")
            progress_bar.progress(40)
            
            profile_data = await self.linkedin_scraper.scrape_profile(linkedin_url)
            
            status_text.text("💾 Storing profile data...")
            progress_bar.progress(60)
            
            # Store profile in memory and session state
            await self.memory_manager.store_profile(
                st.session_state.user_id, 
                profile_data.dict()
            )
            
            st.session_state.profile_data = profile_data.dict()
            st.session_state.profile_analyzed = True
            
            status_text.text("✨ Generating initial analysis...")
            progress_bar.progress(80)
            
            # Clear progress indicators
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            st.success("✅ Profile analyzed successfully!")
            
            # Add welcome message with profile details
            welcome_msg = f"""
            Great! I've successfully analyzed your LinkedIn profile, **{profile_data.full_name}**.
            
            **Profile Overview:**
            - **Current Role:** {profile_data.headline}
            - **Location:** {profile_data.location}
            - **Skills:** {len(profile_data.skills)} skills listed
            - **Experience:** {len(profile_data.experience)} positions
            
            I'm ready to help you optimize your profile! You can:
            
            🚀 **Use Quick Actions** for instant insights
            📊 **Try Enhanced Features** for detailed analysis:
            - Compare your profile against specific job descriptions
            - Get your profile sections rewritten with best practices
            - Identify skill gaps and get learning recommendations
            
            💬 **Or ask me directly** about:
            - Detailed profile analysis and improvement suggestions
            - Job opportunities that match your background
            - Content ideas for LinkedIn posts
            - Career development advice
            
            What would you like to explore first?
            """
            
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
            
            # Also show a quick preview of the profile data
            with st.expander("📋 Profile Data Preview"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Name:**", profile_data.full_name)
                    st.write("**Headline:**", profile_data.headline)
                    st.write("**Location:**", profile_data.location)
                with col2:
                    st.write("**Skills Count:**", len(profile_data.skills))
                    st.write("**Experience Count:**", len(profile_data.experience))
                    st.write("**Education Count:**", len(profile_data.education))
                
                if profile_data.about:
                    st.write("**About (Preview):**")
                    st.write(profile_data.about[:200] + "..." if len(profile_data.about) > 200 else profile_data.about)
            
        except Exception as e:
            st.error(f"❌ Error analyzing profile: {str(e)}")
            
            # Show helpful error message based on error type
            if "Actor with this name was not found" in str(e):
                st.info("💡 **Note:** The LinkedIn scraping service is currently unavailable. The app will use demo data for testing purposes.")
            elif "Missing required environment variables" in str(e):
                st.warning("⚠️ **Configuration Issue:** Please check that your API keys are properly set in the .env file.")
            else:
                st.info("💡 **Tip:** Make sure your LinkedIn URL is public and in the format: https://linkedin.com/in/your-profile")
                
        finally:
            st.session_state.processing = False
            st.rerun()
    
    async def process_user_query(self, query: str) -> str:
        """Process user query and route to appropriate agent"""
        try:
            # Add a small delay to make it feel more natural
            await asyncio.sleep(0.5)
            
            # Determine which agent should handle the query
            agent_choice = await self.route_query(query)
            
            task_data = {
                "query": query,
                "profile_data": st.session_state.get("profile_data")
            }
            
            if agent_choice == "profile_analysis":
                if not st.session_state.profile_data:
                    return "👆 Please first provide your LinkedIn profile URL in the sidebar to get personalized profile analysis."
                
                result = await self.profile_analyzer.execute_with_memory(
                    task_data, st.session_state.user_id
                )
                return self.format_profile_response(result)
                
            elif agent_choice == "job_matching" or agent_choice == "job_fit_analysis":
                if not st.session_state.profile_data:
                    return "👆 Please first provide your LinkedIn profile URL in the sidebar to get personalized job matching."
                
                result = await self.job_matcher.execute_with_memory(
                    task_data, st.session_state.user_id
                )
                return self.format_job_match_response(result)
                
            elif agent_choice == "content_generation" or agent_choice == "content_enhancement":
                result = await self.content_generator.execute_with_memory(
                    task_data, st.session_state.user_id
                )
                return result.get("generated_content", "I've generated some content ideas for you based on your query.")
                
            elif agent_choice == "career_counseling" or agent_choice == "skill_gap_analysis":
                result = await self.career_counselor.execute_with_memory(
                    task_data, st.session_state.user_id
                )
                return result.get("counseling_response", "Here's my career advice for you based on your background and goals.")
                
            else:
                return """I can help you with:
                
                🔍 **Profile Analysis**: Analyze your LinkedIn profile for improvements
                🎯 **Job Matching**: Find jobs that match your skills and experience  
                ✍️ **Content Generation**: Create compelling LinkedIn content
                💼 **Career Counseling**: Get personalized career advice
                
                🚀 **Enhanced Features**:
                📊 **Job Fit Analysis**: Compare your profile against specific job descriptions
                ✨ **Content Enhancement**: Rewrite profile sections with industry best practices
                🎯 **Skill Gap Analysis**: Identify missing skills and get learning recommendations
                
                Please ask me about any of these areas or use the Quick Actions in the sidebar!"""
                
        except Exception as e:
            return f"I apologize, but I encountered an error processing your request: {str(e)}"
    
    async def route_query(self, query: str) -> str:
        """Route query to appropriate agent based on content"""
        query_lower = query.lower()
        
        # Enhanced routing with new features
        
        # Job fit analysis keywords
        if any(word in query_lower for word in [
            "job description", "job fit", "job match", "match score", "job requirements",
            "compare", "qualification", "fit analysis", "recruiter"
        ]):
            return "job_fit_analysis"
            
        # Content enhancement keywords
        elif any(word in query_lower for word in [
            "rewrite", "enhance", "improve content", "best practices", "headline",
            "about section", "experience descriptions", "optimize content"
        ]):
            return "content_enhancement"
            
        # Skill gap analysis keywords  
        elif any(word in query_lower for word in [
            "skill gap", "missing skills", "learning resources", "skill analysis",
            "target role", "skill development", "learning path", "career path"
        ]):
            return "skill_gap_analysis"
        
        # Profile analysis keywords
        elif any(word in query_lower for word in [
            "profile", "analyze", "analysis", "improve", "optimization", "review", 
            "completeness", "strength", "weakness", "recommendation"
        ]):
            return "profile_analysis"
        
        # Job matching keywords
        elif any(word in query_lower for word in [
            "job", "position", "role", "opportunity", "career", "match", "hiring",
            "application", "interview", "company"
        ]):
            return "job_matching"
        
        # Content generation keywords
        elif any(word in query_lower for word in [
            "content", "post", "write", "generate", "create", "ideas"
        ]):
            return "content_generation"
        
        # Career counseling keywords (default)
        else:
            return "career_counseling"
    
    def format_profile_response(self, result: Dict[str, Any]) -> str:
        """Format profile analysis response"""
        if "error" in result:
            return f"Error analyzing profile: {result['error']}"
        
        return result.get("analysis", "Profile analysis completed successfully.")
    
    def format_job_match_response(self, result: Dict[str, Any]) -> str:
        """Format job matching response"""
        if "error" in result:
            return f"Error in job matching: {result['error']}"
        
        return result.get("match_analysis", "Job matching analysis completed successfully.")

def main():
    """Main function to run the Streamlit app"""
    try:
        app = LinkedInEnhancerApp()
        app.render_ui()
    except Exception as e:
        st.error(f"Failed to initialize application: {e}")
        st.info("Please check your environment variables and try again.")

if __name__ == "__main__":
    main() 