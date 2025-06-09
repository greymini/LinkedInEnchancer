from .base_agent import BaseLinkedInAgent
from typing import Dict, Any, Optional
import re

class JobMatcherAgent(BaseLinkedInAgent):
    def __init__(self, gemini_client, memory_manager):
        super().__init__("JobMatcher", gemini_client, memory_manager)
        
    async def execute_task(self, task_data: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
        """Execute job matching analysis"""
        try:
            profile_data = task_data.get("profile_data")
            query = task_data.get("query", "")
            
            if not profile_data:
                return {"error": "No profile data provided for job matching"}
            
            # Check if this is a job fit analysis with specific job description
            if self._is_job_fit_analysis(query):
                match_analysis = await self._detailed_job_fit_analysis(profile_data, query, context)
            else:
                # General job matching
                match_analysis = await self._general_job_match_analysis(profile_data, query, context)
            
            return {
                "match_analysis": match_analysis,
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Job matching analysis failed: {str(e)}"}
    
    def _is_job_fit_analysis(self, query: str) -> bool:
        """Check if query contains a job description for detailed analysis"""
        indicators = [
            "job description", "analyze how well", "compare", "match score",
            "requirements", "qualifications", "responsibilities"
        ]
        return any(indicator in query.lower() for indicator in indicators)
    
    async def _detailed_job_fit_analysis(self, profile_data: Dict, query: str, context: str) -> str:
        """Perform detailed job fit analysis against specific job description"""
        
        # Extract profile information
        skills = profile_data.get('skills', [])
        experience = profile_data.get('experience', [])
        education = profile_data.get('education', [])
        headline = profile_data.get('headline', '')
        about = profile_data.get('about', '')
        full_name = profile_data.get('full_name', 'Candidate')
        
        prompt = f"""
        As an expert recruiter and career advisor, perform a comprehensive job fit analysis for {full_name}.
        
        CANDIDATE PROFILE:
        📋 Current Role: {headline}
        🎓 Education: {self._format_education(education)}
        💼 Experience: {len(experience)} positions
        🛠️ Skills: {', '.join(skills) if skills else 'Not specified'}
        📄 About: {about[:400] if about else 'Not provided'}...
        
        DETAILED EXPERIENCE:
        {self._format_detailed_experience(experience)}
        
        ANALYSIS REQUEST:
        {query}
        
        Provide a comprehensive job fit analysis with:
        
        ## 📊 MATCH SCORE BREAKDOWN
        - **Overall Match**: X/100 (with reasoning)
        - **Skills Match**: X/100 (required vs. possessed skills)
        - **Experience Match**: X/100 (years and relevance)
        - **Education Match**: X/100 (degree requirements)
        - **Culture Fit**: X/100 (based on background and role type)
        
        ## ✅ STRENGTHS & ALIGNMENT
        - List specific qualifications that match perfectly
        - Highlight competitive advantages
        - Identify transferable skills
        
        ## ⚠️ GAPS & IMPROVEMENT AREAS
        - Missing required skills (prioritized)
        - Experience gaps to address
        - Certification or education needs
        
        ## 🚀 IMPROVEMENT RECOMMENDATIONS
        1. **Immediate Actions** (0-3 months)
           - Quick wins to strengthen application
           - Skills to highlight/develop
           - Portfolio/project suggestions
        
        2. **Medium-term Goals** (3-12 months)
           - Training programs to pursue
           - Certifications to obtain
           - Experience to gain
        
        3. **Profile Optimization**
           - Specific LinkedIn headline improvements
           - Keywords to add
           - Experience descriptions to enhance
        
        ## 💡 APPLICATION STRATEGY
        - How to position candidacy
        - Key points to emphasize in cover letter
        - Interview preparation focus areas
        - Networking recommendations
        
        ## 🎯 RECRUITER APPEAL ENHANCEMENT
        - What recruiters look for in this role
        - Industry trends to leverage
        - Competitive positioning advice
        
        Be specific, actionable, and honest about both strengths and areas for improvement.
        """
        
        analysis = await self.gemini_client.generate_response(prompt)
        return analysis
    
    async def _general_job_match_analysis(self, profile_data: Dict, query: str, context: str) -> str:
        """Analyze general job matching and career opportunities"""
        
        # Extract key profile information
        skills = profile_data.get('skills', [])
        experience = profile_data.get('experience', [])
        education = profile_data.get('education', [])
        headline = profile_data.get('headline', '')
        about = profile_data.get('about', '')
        full_name = profile_data.get('full_name', 'Candidate')
        
        prompt = f"""
        As a career advisor and job matching expert, analyze this LinkedIn profile for optimal job opportunities.
        
        CANDIDATE PROFILE:
        👤 Name: {full_name}
        📋 Current Role: {headline}
        🎓 Education: {self._format_education(education)}
        💼 Experience: {len(experience)} positions
        🛠️ Skills: {', '.join(skills[:15]) if skills else 'Not specified'}
        📄 Background: {about[:300] if about else 'Not provided'}...
        
        CAREER TRAJECTORY:
        {self._format_detailed_experience(experience[:4])}
        
        CONTEXT: {context}
        USER QUERY: {query}
        
        Provide comprehensive career guidance:
        
        ## 🎯 BEST JOB MATCHES
        1. **Primary Target Roles** (90%+ match)
           - Specific job titles
           - Why they're perfect fits
           - Salary ranges
        
        2. **Growth Opportunities** (70-90% match)
           - Stretch roles for career advancement
           - Skills needed to qualify
           - Timeline to readiness
        
        3. **Adjacent Opportunities** (60-80% match)
           - Related fields to consider
           - Transferable skills leverage
        
        ## 🏢 INDUSTRY RECOMMENDATIONS
        - Top 3 industries to target
        - Emerging sectors with opportunity
        - Industry-specific preparation needed
        
        ## 🛠️ SKILL GAP ANALYSIS
        - **In-Demand Skills Missing**: Critical gaps to fill
        - **Skills to Strengthen**: Existing skills needing improvement
        - **Emerging Skills**: Future-focused additions
        
        ## 💪 COMPETITIVE ADVANTAGES
        - Unique strengths in current market
        - Differentiators from other candidates
        - Experience combinations that stand out
        
        ## 📈 CAREER STRATEGY
        1. **Short-term (3-6 months)**
           - Immediate opportunities to pursue
           - Quick skill enhancements
        
        2. **Medium-term (6-18 months)**
           - Career advancement pathway
           - Strategic skill development
        
        3. **Long-term (1-3 years)**
           - Senior role preparation
           - Leadership development
        
        ## 💰 MARKET POSITIONING
        - Current market value assessment
        - Salary negotiation leverage points
        - Geographic market considerations
        
        ## 🎯 RECRUITER ATTRACTION STRATEGY
        - Keywords to emphasize
        - Profile sections to optimize
        - Industry networking recommendations
        
        Be specific with job titles, companies, salary ranges, and actionable advice.
        """
        
        analysis = await self.gemini_client.generate_response(prompt)
        return analysis
    
    def _format_education(self, education_list: list) -> str:
        """Format education information"""
        if not education_list:
            return "Not specified"
        
        formatted = []
        for edu in education_list[:2]:  # Show top 2
            if isinstance(edu, dict):
                degree = edu.get('degree', '')
                field = edu.get('field', '')
                school = edu.get('school', '')
                duration = edu.get('duration', '')
                
                if degree or field:
                    edu_str = f"{degree} in {field}" if degree and field else degree or field
                    if school:
                        edu_str += f" from {school}"
                    if duration:
                        edu_str += f" ({duration})"
                    formatted.append(edu_str)
        
        return '; '.join(formatted) if formatted else "Not specified"
    
    def _format_detailed_experience(self, experience_list: list) -> str:
        """Format detailed experience for analysis"""
        if not experience_list:
            return "No experience data available"
        
        formatted = []
        for i, exp in enumerate(experience_list, 1):
            if isinstance(exp, dict):
                title = exp.get('title', 'Unknown Role')
                company = exp.get('company', 'Unknown Company')
                duration = exp.get('duration', 'Unknown duration')
                location = exp.get('location', '')
                description = exp.get('description', '')
                
                exp_entry = f"{i}. **{title}** at {company}"
                if duration:
                    exp_entry += f" | {duration}"
                if location:
                    exp_entry += f" | {location}"
                if description:
                    exp_entry += f"\n   {description[:150]}..." if len(description) > 150 else f"\n   {description}"
                
                formatted.append(exp_entry)
        
        return '\n\n'.join(formatted) if formatted else "Experience details not available" 