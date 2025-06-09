import asyncio
import json
import time
import requests
import re
from typing import Dict, Optional, List
from apify_client import ApifyClient
from pydantic import BaseModel

# Handle Streamlit import gracefully
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except (ImportError, Exception):
    STREAMLIT_AVAILABLE = False
    # Create a mock streamlit for non-streamlit environments
    class MockStreamlit:
        def __init__(self):
            self.secrets = {}
        def info(self, msg): print(f"ℹ️  {msg}")
        def success(self, msg): print(f"✅ {msg}")
        def warning(self, msg): print(f"⚠️  {msg}")
        def error(self, msg): print(f"❌ {msg}")
        def spinner(self, msg): 
            return MockSpinner()
    
    class MockSpinner:
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    st = MockStreamlit()

class LinkedInProfile(BaseModel):
    full_name: str
    headline: str
    about: Optional[str] = ""
    experience: List[Dict] = []
    education: List[Dict] = []
    skills: List[str] = []
    location: str = ""
    connections_count: Optional[int] = None
    profile_url: str
    profile_image: Optional[str] = ""

class LinkedInScraperService:
    def __init__(self, apify_token: str):
        self.client = ApifyClient(apify_token)
        self.actor_id = "curious_coder/linkedin-profile-scraper"
        self.apify_token = apify_token
        
    def get_working_cookies(self) -> List[Dict]:
        """Return working LinkedIn cookies - these need to be updated with valid session cookies"""
        # Note: These are placeholder cookies. For real scraping, you need to:
        # 1. Log into LinkedIn in your browser
        # 2. Use browser dev tools to get current li_at and JSESSIONID cookies
        # 3. Replace the values below with your actual session cookies
        return [
            {
                "name": "li_at",
                "value": "AQEDATNp9ZkDJ7rkAAABk-gTmDUAAAGXb8vvVFYAbaxdWanwzyJKwBHlaT7KzsdaeWs4VSRocod647wzRk-Qq4iLQydk0nm9lJD9LP_B5hlxZWyCikcJZOY67-AvB29OKiJ-TWLrIZNMYZJ9irt8N4H8",
                "domain": ".linkedin.com"
            },
            {
                "name": "JSESSIONID", 
                "value": "ajax:8402475393784977436",
                "domain": ".linkedin.com"
            },
            {
                "name": "bcookie",
                "value": "v=2&e97d7692-2a94-4c41-8f49-f62e59ecf92e", 
                "domain": ".linkedin.com"
            },
            {
                "name": "bscookie",
                "value": "v=1&202412061006577fd4144e-e016-4721-8943-98824a378d89AQGu9Q9UzRkoR7uMbcbnkK8xvhyZctGe",
                "domain": ".linkedin.com"
            }
        ]
    

    def create_scraper_input(self, profile_url: str) -> Dict:
        """Create input using the exact format that works"""
        return {
            "cookie": self.get_working_cookies(),
            "findContacts": False,
            "maxDelay": 60,
            "minDelay": 15,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": [],
                "apifyProxyCountry": "US"
            },
            "scrapeCompany": True,
            "urls": [profile_url]
        }
    
    def check_credits(self) -> Dict:
        """Check available Apify credits"""
        try:
            # Direct API call to user endpoint
            headers = {
                "Authorization": f"Bearer {self.apify_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://api.apify.com/v2/users/me", 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                plan = user_data.get('plan', {})
                available_credits = plan.get('availableCredits', 0)
                
                return {
                    'available_credits': available_credits,
                    'has_credits': available_credits > 0.001,
                    'username': user_data.get('username', 'Unknown')
                }
            else:
                pass  # Silent fail for credit check
                
        except Exception as e:
            pass  # Silent fail for credit check
        
        # Fallback: Use Apify client method
        try:
            user_info = self.client.user().get()
            plan = user_info.get('plan', {})
            available_credits = plan.get('availableCredits', 0)
            
            return {
                'available_credits': available_credits,
                'has_credits': available_credits > 0.001,
                'username': user_info.get('username', 'Unknown')
            }
            
        except Exception as e:
            # Return optimistic result to allow scraping attempt
            return {
                'available_credits': 0,
                'has_credits': True,
                'username': 'Unknown',
                'check_failed': True
            }

    def fetch_from_dataset(self, dataset_id: str) -> Optional[LinkedInProfile]:
        """Fetch profile data directly from a known dataset ID"""
        try:
            url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
            headers = {
                "Authorization": f"Bearer {self.apify_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    profile_data = data[0]
                    return self._normalize_profile_data(profile_data, "")
                    
            return None
            
        except Exception as e:
            st.error(f"Error fetching from dataset: {e}")
            return None

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Check if the provided URL is a valid LinkedIn profile URL"""
        linkedin_patterns = [
            r'linkedin\.com/in/[^/?]+',
            r'www\.linkedin\.com/in/[^/?]+',
            r'https?://(?:www\.)?linkedin\.com/in/[^/?]+'
        ]
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in linkedin_patterns)

    def _extract_username_from_url(self, url: str) -> str:
        """Extract username from LinkedIn URL"""
        try:
            match = re.search(r'/in/([^/?]+)', url)
            if match:
                return match.group(1)
        except:
            pass
        return "linkedin-user"

    async def scrape_profile(self, profile_url: str) -> LinkedInProfile:
        """Main scraping method using the correct Apify API format"""
        
        # Validate LinkedIn URL
        if not self._is_valid_linkedin_url(profile_url):
            st.error(f"❌ Invalid LinkedIn profile URL: {profile_url}")
            return self._create_simple_demo_profile(profile_url, "Invalid LinkedIn URL provided")
        
        username = self._extract_username_from_url(profile_url)
        
        # Check credits
        credit_info = self.check_credits()
        if not credit_info['has_credits'] and not credit_info.get('check_failed', False):
            st.warning("⚠️ Insufficient Apify credits - add credits at: https://console.apify.com/billing")
            # Continue with scraping attempt anyway
        
        # Attempt scraping
        try:
            with st.spinner(f"Scraping LinkedIn profile..."):
                run_input = self.create_scraper_input(profile_url)
                run = self.client.actor(self.actor_id).call(run_input=run_input)
                
                run_id = run.get("id")
                if not run_id:
                    st.error("Failed to start scraping")
                    return self._create_simple_demo_profile(profile_url, "Failed to start scraping run")
                
                # Wait for completion
                max_wait = 300  # 5 minutes
                start_time = time.time()
                check_interval = 15
                
                while run.get("status") not in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    elapsed = time.time() - start_time
                    if elapsed > max_wait:
                        st.error("Scraping timed out")
                        return self._create_simple_demo_profile(profile_url, "Scraping timeout")
                    
                    await asyncio.sleep(check_interval)
                    try:
                        run = self.client.run(run_id).get()
                    except Exception:
                        continue
                
                # Handle completion
                final_status = run.get("status")
                
                if final_status == "SUCCEEDED":
                    dataset_id = run.get("defaultDatasetId")
                    items = list(self.client.dataset(dataset_id).iterate_items())
                    
                    if items and len(items) > 0:
                        profile_data = items[0]
                        
                        if self._is_valid_profile_data(profile_data):
                            normalized_profile = self._normalize_profile_data(profile_data, profile_url)
                            st.success(f"Successfully scraped profile: {normalized_profile.full_name}")
                            return normalized_profile
                        else:
                            st.warning("Scraped data appears incomplete")
                            return self._create_simple_demo_profile(profile_url, "Incomplete data retrieved")
                    else:
                        st.warning("No data returned from scraping")
                        return self._create_simple_demo_profile(profile_url, "No data returned")
                        
                elif final_status == "FAILED":
                    error_message = run.get("errorMessage", "Unknown error")
                    st.error(f"Scraping failed: {error_message}")
                    return self._create_simple_demo_profile(profile_url, f"Scraping failed: {error_message}")
                
                else:
                    st.warning(f"Scraping was {final_status.lower()}")
                    return self._create_simple_demo_profile(profile_url, f"Process {final_status.lower()}")
                    
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return self._create_simple_demo_profile(profile_url, f"Technical error: {str(e)}")

    def _normalize_profile_data(self, raw_data: Dict, profile_url: str) -> LinkedInProfile:
        """Normalize scraped profile data to our LinkedInProfile format"""
        try:
            # Extract name
            full_name = (
                raw_data.get("fullName") or 
                raw_data.get("full_name") or
                f"{raw_data.get('firstName', '')} {raw_data.get('lastName', '')}".strip() or
                "LinkedIn User"
            )
            
            # Extract headline
            headline = (
                raw_data.get("headline") or 
                raw_data.get("occupation") or
                raw_data.get("title") or
                "Professional"
            )
            
            # Extract about section
            about = (
                raw_data.get("about") or 
                raw_data.get("summary") or 
                raw_data.get("description") or
                ""
            )
            
            # Extract location
            location = (
                raw_data.get("location") or
                raw_data.get("locationName") or
                raw_data.get("geo", {}).get("city") or
                ""
            )
            
            # Extract connections count
            connections_count = None
            connections_raw = raw_data.get("connectionsCount") or raw_data.get("connections")
            if connections_raw:
                if isinstance(connections_raw, int):
                    connections_count = connections_raw
                elif isinstance(connections_raw, str):
                    match = re.search(r'(\d+)', connections_raw)
                    if match:
                        connections_count = int(match.group(1))
            
            # Extract experience
            experience = []
            exp_data = raw_data.get("experience", []) or raw_data.get("positions", [])
            
            for exp in exp_data[:5]:  # Limit to 5 most recent
                if isinstance(exp, dict):
                    experience.append({
                        "title": exp.get("title") or exp.get("position") or "",
                        "company": exp.get("company") or exp.get("companyName") or "",
                        "description": exp.get("description") or exp.get("summary") or "",
                        "duration": exp.get("duration") or exp.get("dateRange") or "",
                        "location": exp.get("location") or ""
                    })
            
            # Extract education
            education = []
            edu_data = raw_data.get("education", []) or raw_data.get("educations", [])
            
            for edu in edu_data[:3]:  # Limit to 3 most recent
                if isinstance(edu, dict):
                    education.append({
                        "school": edu.get("school") or edu.get("schoolName") or "",
                        "degree": edu.get("degree") or edu.get("degreeName") or "",
                        "field": edu.get("field") or edu.get("fieldOfStudy") or "",
                        "duration": edu.get("duration") or edu.get("dateRange") or ""
                    })
            
            # Extract skills
            skills = []
            skills_data = raw_data.get("skills", [])
            
            if isinstance(skills_data, list):
                for skill in skills_data[:20]:  # Limit to 20 skills
                    if isinstance(skill, dict):
                        skill_name = skill.get("name") or skill.get("skill")
                        if skill_name:
                            skills.append(skill_name)
                    elif isinstance(skill, str):
                        skills.append(skill)
            
            return LinkedInProfile(
                full_name=full_name,
                headline=headline,
                about=about,
                experience=experience,
                education=education,
                skills=skills,
                location=location,
                connections_count=connections_count,
                profile_url=profile_url,
                profile_image=raw_data.get("profilePicture", "")
            )
            
        except Exception as e:
            st.error(f"Error normalizing profile data: {e}")
            return self._create_simple_demo_profile(profile_url, f"Data processing error: {str(e)}")

    def _create_simple_demo_profile(self, profile_url: str, reason: str) -> LinkedInProfile:
        """Create a simple demo profile when real scraping isn't possible"""
        username = self._extract_username_from_url(profile_url)
        
        return LinkedInProfile(
            full_name=f"Demo User ({username})",
            headline="Demo Profile - Real LinkedIn scraping not available",
            about=f"""This is a demo profile because: {reason}

To get real LinkedIn data:
• Ensure you have Apify credits ($5-10 recommended)
• Verify the LinkedIn URL is correct and public
• Check your Apify account configuration

Real LinkedIn scraping requires proper setup and credits.""",
            experience=[{
                "title": "Demo Position",
                "company": "Demo Company",
                "description": "This is example data. Real scraping would show actual work history.",
                "duration": "Demo Period",
                "location": "Demo Location"
            }],
            education=[{
                "school": "Demo University",
                "degree": "Demo Degree",
                "field": "Demo Field",
                "duration": "Demo Years"
            }],
            skills=["Demo Skill 1", "Demo Skill 2", "Demo Skill 3"],
            location="Demo Location",
            connections_count=500,
            profile_url=profile_url
        )
    
    def _is_valid_profile_data(self, profile_data: Dict) -> bool:
        """Check if the profile data contains meaningful information"""
        if not profile_data:
            return False
            
        has_name = bool(profile_data.get("firstName") or profile_data.get("fullName") or profile_data.get("full_name"))
        has_headline = bool(profile_data.get("headline") or profile_data.get("occupation"))
        
        return has_name and has_headline

class JobDatabaseService:
    """Service to provide job description templates for analysis"""
    
    def __init__(self):
        self.job_templates = {
            "data_scientist": {
                "title": "Senior Data Scientist",
                "requirements": [
                    "PhD or Master's in Data Science, Statistics, or related field",
                    "5+ years experience in machine learning and statistical analysis",
                    "Proficiency in Python, R, and SQL",
                    "Experience with ML frameworks (TensorFlow, PyTorch, scikit-learn)",
                    "Strong communication and presentation skills"
                ]
            }
        }
    
    async def get_job_description(self, role: str) -> Dict:
        """Get job description template for a specific role"""
        return self.job_templates.get(role.lower().replace(" ", "_"), {
            "title": f"{role}",
            "requirements": ["Role-specific requirements would be listed here"]
        }) 