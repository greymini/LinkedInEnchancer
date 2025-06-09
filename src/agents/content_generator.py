from .base_agent import BaseLinkedInAgent
from typing import Dict, Any, Optional

class ContentGeneratorAgent(BaseLinkedInAgent):
    def __init__(self, gemini_client, memory_manager):
        super().__init__("ContentGenerator", gemini_client, memory_manager)
        
    async def execute_task(self, task_data: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
        """Execute content generation task"""
        try:
            profile_data = task_data.get("profile_data")
            query = task_data.get("query", "")
            
            # Check if this is a content enhancement request
            if self._is_content_enhancement(query):
                generated_content = await self._enhance_profile_content(profile_data, query, context)
            else:
                # General content generation
                generated_content = await self._generate_general_content(profile_data, query, context)
            
            return {
                "generated_content": generated_content,
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Content generation failed: {str(e)}"}
    
    def _is_content_enhancement(self, query: str) -> bool:
        """Check if this is a content enhancement request"""
        enhancement_indicators = [
            "rewrite", "enhance", "improve", "optimize", "best practices",
            "about section", "headline", "experience descriptions", "skills section"
        ]
        return any(indicator in query.lower() for indicator in enhancement_indicators)
    
    async def _enhance_profile_content(self, profile_data: Dict, query: str, context: str) -> str:
        """Enhance specific profile sections with industry best practices"""
        
        if not profile_data:
            return "Please provide your LinkedIn profile data first to get personalized content enhancement."
        
        # Extract profile information
        name = profile_data.get('full_name', 'Professional')
        headline = profile_data.get('headline', '')
        skills = profile_data.get('skills', [])
        experience = profile_data.get('experience', [])
        education = profile_data.get('education', [])
        about = profile_data.get('about', '')
        
        # Determine which section to enhance
        section_to_enhance = self._identify_content_section(query)
        
        prompt = f"""
        As a LinkedIn optimization expert and professional copywriter, enhance the {section_to_enhance} for this professional using industry best practices.
        
        CURRENT PROFILE DATA:
        👤 Name: {name}
        📋 Current Headline: {headline}
        🛠️ Skills: {', '.join(skills) if skills else 'Not specified'}
        🎓 Education: {self._format_education_brief(education)}
        📄 Current About: {about if about else 'Not provided'}
        
        EXPERIENCE OVERVIEW:
        {self._format_experience_brief(experience[:3])}
        
        ENHANCEMENT REQUEST: {query}
        
        SECTION TO ENHANCE: {section_to_enhance}
        
        Please provide enhanced content following these guidelines:
        
        ## {section_to_enhance.upper()} ENHANCEMENT
        
        {"### CURRENT VERSION:" if section_to_enhance != "Skills Section" else ""}
        {self._get_current_section_content(section_to_enhance, profile_data)}
        
        ### ✨ ENHANCED VERSION:
        
        **Key Improvements Made:**
        - Industry best practice alignment
        - ATS optimization with relevant keywords
        - Compelling value proposition
        - Professional tone with personality
        - Quantified achievements where applicable
        
        ### 📊 OPTIMIZATION FEATURES:
        {self._get_section_specific_guidelines(section_to_enhance)}
        
        ### 🎯 TARGETING & KEYWORDS:
        - Primary keywords incorporated
        - Industry-specific terminology
        - Role-relevant buzzwords
        - Recruiter search optimization
        
        ### 💡 USAGE TIPS:
        - Best practices for this section
        - Common mistakes to avoid
        - Update frequency recommendations
        - Performance tracking suggestions
        
        Make the enhanced content compelling, professional, and optimized for both human readers and ATS systems.
        """
        
        enhanced_content = await self.gemini_client.generate_response(prompt)
        return enhanced_content
    
    async def _generate_general_content(self, profile_data: Dict, query: str, context: str) -> str:
        """Generate general LinkedIn content"""
        
        # Extract profile information for context
        if profile_data:
            name = profile_data.get('full_name', 'Professional')
            headline = profile_data.get('headline', '')
            skills = profile_data.get('skills', [])
            experience = profile_data.get('experience', [])
            about = profile_data.get('about', '')
        else:
            name = 'Professional'
            headline = ''
            skills = []
            experience = []
            about = ''
        
        prompt = f"""
        As a LinkedIn content optimization expert, help create compelling content for this professional.
        
        PROFILE CONTEXT:
        👤 Name: {name}
        📋 Current Role: {headline}
        🛠️ Key Skills: {', '.join(skills[:8]) if skills else 'Not specified'}
        💼 Experience Level: {len(experience)} positions
        📄 Current About: {about[:200] if about else 'Not provided'}...
        
        RECENT EXPERIENCE:
        {self._format_experience_brief(experience[:2])}
        
        CONTEXT: {context}
        USER REQUEST: {query}
        
        Based on the request, provide comprehensive content assistance:
        
        ## 📝 CONTENT RECOMMENDATIONS
        
        **If Post Ideas Requested:**
        - 5-7 engaging LinkedIn post concepts
        - Industry-relevant topics
        - Personal branding angles
        - Optimal hashtag strategies
        - Engagement optimization tips
        
        **If Profile Content Requested:**
        - Compelling, keyword-rich content
        - Professional tone with personality
        - Achievement-focused language
        - Call-to-action optimization
        
        **If Experience Descriptions Requested:**
        - Achievement-oriented bullet points
        - Quantified results emphasis
        - Action-verb focused language
        - ATS-friendly keywords
        
        ## 🎯 OPTIMIZATION STRATEGY
        - LinkedIn algorithm considerations
        - Audience targeting advice
        - Content calendar suggestions
        - Performance tracking recommendations
        
        ## 💡 BEST PRACTICES
        - Industry-specific guidelines
        - Engagement optimization
        - Professional networking tips
        - Brand consistency advice
        
        Make all content authentic, professional, and optimized for LinkedIn's platform and audience.
        """
        
        content = await self.gemini_client.generate_response(prompt)
        return content
    
    def _identify_content_section(self, query: str) -> str:
        """Identify which profile section to enhance"""
        query_lower = query.lower()
        
        if "about section" in query_lower or "summary" in query_lower:
            return "About Section"
        elif "headline" in query_lower:
            return "Headline"
        elif "experience" in query_lower or "job description" in query_lower:
            return "Experience Descriptions"
        elif "skills" in query_lower:
            return "Skills Section"
        else:
            return "About Section"  # Default
    
    def _get_current_section_content(self, section: str, profile_data: Dict) -> str:
        """Get current content for the specified section"""
        if section == "About Section":
            return profile_data.get('about', 'Not provided')
        elif section == "Headline":
            return profile_data.get('headline', 'Not provided')
        elif section == "Experience Descriptions":
            experience = profile_data.get('experience', [])
            if experience:
                recent_exp = experience[0]
                return f"Most Recent: {recent_exp.get('title', '')} at {recent_exp.get('company', '')}\nDescription: {recent_exp.get('description', 'Not provided')}"
            return "No experience data available"
        elif section == "Skills Section":
            skills = profile_data.get('skills', [])
            return f"Current Skills ({len(skills)}): {', '.join(skills[:15])}" if skills else "No skills listed"
        else:
            return "Section content not available"
    
    def _get_section_specific_guidelines(self, section: str) -> str:
        """Get section-specific optimization guidelines"""
        guidelines = {
            "About Section": """
            - Hook: Compelling opening line
            - Value proposition: Clear unique selling points
            - Keywords: Industry-relevant terms naturally integrated
            - Call-to-action: Clear next steps for connections
            - Personality: Professional yet authentic voice
            - Achievements: Quantified results and impact
            """,
            "Headline": """
            - Primary keyword: Role-specific search terms
            - Value proposition: What you deliver/achieve
            - Industry focus: Sector-specific terminology
            - Character optimization: Maximum 220 characters
            - Action-oriented: Dynamic, engaging language
            - Differentiation: Unique positioning elements
            """,
            "Experience Descriptions": """
            - Action verbs: Strong, impactful opening words
            - Quantified results: Numbers, percentages, metrics
            - Keywords: Role and industry-specific terms
            - Achievements: Focus on impact and outcomes
            - Relevance: Skills applicable to target roles
            - Readability: Bullet points and clear structure
            """,
            "Skills Section": """
            - Keyword optimization: Recruiter search terms
            - Skill prioritization: Most relevant skills first
            - Industry alignment: Sector-specific competencies
            - Endorsement strategy: Skills likely to be endorsed
            - Future-focused: Emerging and in-demand skills
            - Balance: Technical and soft skills mix
            """
        }
        return guidelines.get(section, "General optimization principles apply")
    
    def _format_education_brief(self, education_list: list) -> str:
        """Format education briefly"""
        if not education_list:
            return "Not specified"
        
        edu = education_list[0] if education_list else {}
        degree = edu.get('degree', '')
        field = edu.get('field', '')
        school = edu.get('school', '')
        
        if degree and field:
            return f"{degree} in {field} from {school}" if school else f"{degree} in {field}"
        return "Education information available"
    
    def _format_experience_brief(self, experience_list: list) -> str:
        """Format experience briefly for context"""
        if not experience_list:
            return "No experience data available"
        
        formatted = []
        for exp in experience_list[:2]:
            if isinstance(exp, dict):
                title = exp.get('title', 'Role')
                company = exp.get('company', 'Company')
                duration = exp.get('duration', '')
                formatted.append(f"• {title} at {company} ({duration})")
        
        return '\n'.join(formatted) if formatted else "Experience details not available" 