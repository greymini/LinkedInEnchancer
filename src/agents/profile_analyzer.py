from .base_agent import BaseLinkedInAgent
from typing import Dict, Any, Optional

class ProfileAnalyzerAgent(BaseLinkedInAgent):
    def __init__(self, gemini_client, memory_manager):
        super().__init__("ProfileAnalyzer", gemini_client, memory_manager)
        
    async def execute_task(self, task_data: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
        """Execute profile analysis task"""
        try:
            profile_data = task_data.get("profile_data")
            query = task_data.get("query", "")
            
            if not profile_data:
                return {"error": "No profile data provided for analysis"}
            
            # Analyze the profile
            analysis = await self._analyze_profile(profile_data, query, context)
            
            return {
                "analysis": analysis,
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Profile analysis failed: {str(e)}"}
    
    async def _analyze_profile(self, profile_data: Dict, query: str, context: str) -> str:
        """Analyze LinkedIn profile and provide insights"""
        
        # Create a comprehensive analysis prompt
        prompt = f"""
        As a LinkedIn profile optimization expert, analyze this profile and provide actionable insights.
        
        Profile Data:
        - Name: {profile_data.get('full_name', 'N/A')}
        - Headline: {profile_data.get('headline', 'N/A')}
        - About: {profile_data.get('about', 'Not provided')[:500]}...
        - Experience: {len(profile_data.get('experience', []))} positions
        - Education: {len(profile_data.get('education', []))} entries
        - Skills: {len(profile_data.get('skills', []))} skills listed
        - Location: {profile_data.get('location', 'N/A')}
        
        {context}
        
        User Question: {query}
        
        Provide a comprehensive analysis including:
        1. Profile Completeness Assessment (rate 1-10)
        2. Key Strengths 
        3. Areas for Improvement
        4. Specific Recommendations
        5. Next Steps
        
        Be specific, actionable, and encouraging. Format your response clearly with headers and bullet points.
        """
        
        analysis = await self.gemini_client.generate_response(prompt)
        return analysis
    
    def _calculate_completeness_score(self, profile_data: Dict) -> Dict:
        """Calculate profile completeness score"""
        score = 0
        total_points = 10
        feedback = []
        
        # Basic info (2 points)
        if profile_data.get('full_name'):
            score += 1
        else:
            feedback.append("Add your full name")
            
        if profile_data.get('headline'):
            score += 1
        else:
            feedback.append("Add a professional headline")
        
        # About section (2 points)
        about = profile_data.get('about', '')
        if len(about) > 100:
            score += 2
        elif len(about) > 0:
            score += 1
            feedback.append("Expand your About section (aim for 200+ words)")
        else:
            feedback.append("Add an About section")
        
        # Experience (3 points)
        experience = profile_data.get('experience', [])
        if len(experience) >= 3:
            score += 2
        elif len(experience) >= 1:
            score += 1
            feedback.append("Add more work experience entries")
        else:
            feedback.append("Add your work experience")
        
        # Check if experience has descriptions
        if any(exp.get('description') for exp in experience):
            score += 1
        else:
            feedback.append("Add descriptions to your experience entries")
        
        # Education (1 point)
        if profile_data.get('education'):
            score += 1
        else:
            feedback.append("Add your education background")
        
        # Skills (2 points)
        skills = profile_data.get('skills', [])
        if len(skills) >= 10:
            score += 2
        elif len(skills) >= 5:
            score += 1
            feedback.append("Add more relevant skills (aim for 10+)")
        else:
            feedback.append("Add your key skills")
        
        percentage = int((score / total_points) * 100)
        
        return {
            "score": percentage,
            "raw_score": score,
            "total_points": total_points,
            "feedback": feedback,
            "level": self._get_completeness_level(percentage)
        }
    
    def _get_completeness_level(self, score: int) -> str:
        """Get completeness level based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Needs Improvement" 