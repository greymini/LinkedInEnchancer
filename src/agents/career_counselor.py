from .base_agent import BaseLinkedInAgent
from typing import Dict, Any, Optional

class CareerCounselorAgent(BaseLinkedInAgent):
    def __init__(self, gemini_client, memory_manager):
        super().__init__("CareerCounselor", gemini_client, memory_manager)
        
    async def execute_task(self, task_data: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
        """Execute career counseling task"""
        try:
            profile_data = task_data.get("profile_data")
            query = task_data.get("query", "")
            
            # Check if this is a skill gap analysis request
            if self._is_skill_gap_analysis(query):
                counseling_response = await self._detailed_skill_gap_analysis(profile_data, query, context)
            else:
                # General career counseling
                counseling_response = await self._general_career_counseling(profile_data, query, context)
            
            return {
                "counseling_response": counseling_response,
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Career counseling failed: {str(e)}"}
    
    def _is_skill_gap_analysis(self, query: str) -> bool:
        """Check if this is a skill gap analysis request"""
        skill_gap_indicators = [
            "skill gap", "missing skills", "learning resources", "skill analysis",
            "target role", "skill development", "learning path", "career path",
            "skills needed", "skill requirements"
        ]
        return any(indicator in query.lower() for indicator in skill_gap_indicators)
    
    async def _detailed_skill_gap_analysis(self, profile_data: Dict, query: str, context: str) -> str:
        """Perform detailed skill gap analysis with learning recommendations"""
        
        if not profile_data:
            return "Please provide your LinkedIn profile data first to get personalized skill gap analysis."
        
        # Extract profile information
        name = profile_data.get('full_name', 'Professional')
        headline = profile_data.get('headline', '')
        skills = profile_data.get('skills', [])
        experience = profile_data.get('experience', [])
        education = profile_data.get('education', [])
        about = profile_data.get('about', '')
        
        # Extract target role if mentioned in query
        target_role = self._extract_target_role(query)
        
        prompt = f"""
        As a senior career development expert and skills analyst, perform a comprehensive skill gap analysis for {name}.
        
        CURRENT PROFESSIONAL PROFILE:
        👤 Name: {name}
        📋 Current Role: {headline}
        🎓 Education: {self._format_education_detailed(education)}
        🛠️ Current Skills ({len(skills)}): {', '.join(skills) if skills else 'Not specified'}
        📄 Professional Summary: {about[:400] if about else 'Not provided'}...
        
        CAREER PROGRESSION:
        {self._format_detailed_career_progression(experience)}
        
        ANALYSIS REQUEST: {query}
        TARGET ROLE: {target_role if target_role else 'General market competitiveness'}
        CONTEXT: {context}
        
        Provide a comprehensive skill gap analysis:
        
        ## 🎯 TARGET ROLE ANALYSIS
        **Role Requirements Overview:**
        - Essential technical skills
        - Required soft skills
        - Industry certifications
        - Experience expectations
        - Emerging skill trends
        
        ## 📊 CURRENT SKILL ASSESSMENT
        
        ### ✅ STRENGTHS & ADVANTAGES
        - Skills that perfectly align with target role
        - Unique skill combinations
        - Transferable competencies
        - Industry-relevant experience
        - Competitive advantages
        
        ### ⚠️ CRITICAL SKILL GAPS
        **High Priority (Immediate Focus):**
        - Essential skills missing for target role
        - Technical competencies to develop
        - Industry-standard certifications needed
        
        **Medium Priority (3-6 months):**
        - Skills that enhance competitiveness
        - Emerging technologies to learn
        - Leadership/management capabilities
        
        **Low Priority (6-12 months):**
        - Nice-to-have skills
        - Future-focused competencies
        - Specialized knowledge areas
        
        ## 📚 DETAILED LEARNING ROADMAP
        
        ### 🚀 IMMEDIATE ACTIONS (0-3 months)
        **Skill 1: [Primary Gap]**
        - **Learning Resources:** Specific courses, platforms, books
        - **Time Investment:** Recommended hours per week
        - **Practical Application:** Projects, portfolios, certifications
        - **Cost Estimate:** Budget for learning materials
        
        **Skill 2: [Secondary Gap]**
        - **Learning Resources:** [Detailed recommendations]
        - **Time Investment:** [Specific timeframe]
        - **Practical Application:** [Hands-on practice suggestions]
        - **Validation:** [How to demonstrate proficiency]
        
        ### 📈 MEDIUM-TERM DEVELOPMENT (3-12 months)
        **Professional Development Areas:**
        - Advanced technical skills
        - Industry certifications
        - Leadership capabilities
        - Specialized knowledge domains
        
        **Learning Strategy:**
        - Formal education options
        - Professional bootcamps
        - Industry conferences
        - Mentorship opportunities
        
        ### 🔮 LONG-TERM CAREER PREPARATION (1-2 years)
        **Future-Focused Skills:**
        - Emerging technology trends
        - Industry evolution preparation
        - Senior role competencies
        - Cross-functional expertise
        
        ## 🛠️ PRACTICAL IMPLEMENTATION
        
        ### 📅 LEARNING SCHEDULE
        - Weekly time allocation recommendations
        - Learning milestone checkpoints
        - Progress tracking methods
        - Skill validation approaches
        
        ### 💰 INVESTMENT STRATEGY
        - Budget allocation for skill development
        - Free vs. paid learning resources
        - ROI calculation for certifications
        - Company-sponsored learning opportunities
        
        ### 🤝 NETWORKING & MENTORSHIP
        - Industry professionals to connect with
        - Communities and forums to join
        - Mentorship opportunity identification
        - Knowledge sharing strategies
        
        ## 🎯 RECRUITER APPEAL ENHANCEMENT
        
        ### 📝 SKILL PRESENTATION
        - How to highlight developing skills
        - Portfolio project recommendations
        - LinkedIn skill optimization
        - Resume enhancement strategies
        
        ### 🏆 CREDIBILITY BUILDING
        - Certification priorities
        - Project showcasing methods
        - Industry contribution opportunities
        - Thought leadership development
        
        ## 📊 PROGRESS TRACKING
        
        ### 🎯 KPIs & METRICS
        - Skill development milestones
        - Learning progress indicators
        - Market competitiveness measures
        - Career advancement metrics
        
        ### 🔄 REGULAR ASSESSMENT
        - Monthly skill review process
        - Market demand monitoring
        - Role requirement updates
        - Career goal adjustment strategies
        
        ## 💡 SUCCESS OPTIMIZATION TIPS
        - Learning efficiency maximization
        - Retention and application strategies
        - Networking integration with learning
        - Continuous improvement mindset
        
        Provide specific, actionable recommendations with exact learning resources, timelines, and implementation strategies.
        """
        
        analysis = await self.gemini_client.generate_response(prompt)
        return analysis
    
    async def _general_career_counseling(self, profile_data: Dict, query: str, context: str) -> str:
        """Provide general career counseling and guidance"""
        
        # Extract profile information for context
        if profile_data:
            name = profile_data.get('full_name', 'Professional')
            headline = profile_data.get('headline', '')
            skills = profile_data.get('skills', [])
            experience = profile_data.get('experience', [])
            education = profile_data.get('education', [])
            about = profile_data.get('about', '')
            experience_level = len(experience)
        else:
            name = 'Professional'
            headline = ''
            skills = []
            experience = []
            education = []
            about = ''
            experience_level = 0
        
        prompt = f"""
        As an experienced career counselor and professional development expert, provide personalized guidance for {name}.
        
        PROFESSIONAL PROFILE:
        👤 Name: {name}
        📋 Current Position: {headline}
        🎓 Education: {self._format_education_detailed(education)}
        💼 Experience Level: {experience_level} positions held
        🛠️ Key Skills: {', '.join(skills[:12]) if skills else 'Skills not specified'}
        📄 Background: {about[:300] if about else 'Background not provided'}...
        
        CAREER TRAJECTORY:
        {self._format_detailed_career_progression(experience[:4])}
        
        PREVIOUS CONTEXT: {context}
        USER QUESTION: {query}
        
        Provide comprehensive career guidance:
        
        ## 🎯 CAREER ASSESSMENT & POSITIONING
        
        ### 📊 Current Position Analysis
        - Professional strengths assessment
        - Market positioning evaluation
        - Competitive advantages identification
        - Areas for improvement
        
        ### 🚀 Career Trajectory Evaluation
        - Career progression analysis
        - Growth pattern recognition
        - Strategic positioning opportunities
        - Experience leverage potential
        
        ## 📈 GROWTH OPPORTUNITIES
        
        ### 🎯 Immediate Opportunities (3-6 months)
        - Quick advancement possibilities
        - Internal promotion potential
        - Skill-based role transitions
        - Industry movement options
        
        ### 🌟 Medium-term Growth (6-18 months)
        - Strategic career moves
        - Leadership development paths
        - Specialty area development
        - Geographic expansion options
        
        ### 🔮 Long-term Vision (1-3 years)
        - Senior role preparation
        - Industry leadership positioning
        - Entrepreneurial opportunities
        - Executive career pathway
        
        ## 🛠️ SKILL DEVELOPMENT STRATEGY
        
        ### 💪 Core Competency Enhancement
        - Existing skill strengthening
        - Professional certification priorities
        - Technical skill upgrades
        - Soft skill development
        
        ### 🆕 Emerging Skill Acquisition
        - Industry trend alignment
        - Future-focused capabilities
        - Cross-functional competencies
        - Innovation and adaptability
        
        ## 🌐 INDUSTRY INSIGHTS & TRENDS
        
        ### 📊 Market Analysis
        - Industry growth patterns
        - Emerging opportunities
        - Competitive landscape
        - Salary trend analysis
        
        ### 🔮 Future Outlook
        - Technology impact predictions
        - Role evolution expectations
        - Industry disruption preparation
        - Adaptation strategies
        
        ## 🤝 NETWORKING & RELATIONSHIP STRATEGY
        
        ### 🌟 Professional Network Building
        - Key relationship identification
        - Industry community engagement
        - Mentorship opportunity pursuit
        - Strategic partnership development
        
        ### 💼 Industry Presence Enhancement
        - Thought leadership development
        - Professional visibility increase
        - Industry contribution strategies
        - Personal brand strengthening
        
        ## 🎨 PERSONAL BRANDING OPTIMIZATION
        
        ### 📱 Digital Presence Strategy
        - LinkedIn optimization tactics
        - Professional portfolio development
        - Content creation strategies
        - Online reputation management
        
        ### 🎯 Value Proposition Refinement
        - Unique selling point identification
        - Competitive differentiation
        - Professional story crafting
        - Brand consistency maintenance
        
        ## 📋 ACTIONABLE IMPLEMENTATION PLAN
        
        ### 🎯 30-Day Quick Wins
        - Immediate action items
        - Low-hanging fruit opportunities
        - Quick improvement strategies
        - Momentum building activities
        
        ### 📅 90-Day Strategic Initiatives
        - Medium-term goal setting
        - Skill development projects
        - Network expansion activities
        - Professional milestone achievements
        
        ### 🗓️ Annual Career Development
        - Long-term objective setting
        - Career advancement planning
        - Continuous learning integration
        - Progress measurement systems
        
        ## 💡 SUCCESS OPTIMIZATION
        - Productivity enhancement tips
        - Career satisfaction maximization
        - Work-life balance strategies
        - Continuous improvement mindset
        
        Be encouraging, specific, and practical. Consider their unique background and provide actionable steps for career advancement.
        """
        
        counseling = await self.gemini_client.generate_response(prompt)
        return counseling
    
    def _extract_target_role(self, query: str) -> str:
        """Extract target role from query if mentioned"""
        # Look for patterns like "for the role of", "target role", etc.
        import re
        
        patterns = [
            r"for the role of ['\"]?([^'\"]+)['\"]?",
            r"target role[:\s]+['\"]?([^'\"]+)['\"]?",
            r"role of ['\"]?([^'\".\n]+)['\"]?",
            r"position of ['\"]?([^'\".\n]+)['\"]?",
            r"as a ['\"]?([^'\".\n]+)['\"]?"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _format_education_detailed(self, education_list: list) -> str:
        """Format education information in detail"""
        if not education_list:
            return "Not specified"
        
        formatted = []
        for edu in education_list[:3]:  # Show top 3
            if isinstance(edu, dict):
                degree = edu.get('degree', '')
                field = edu.get('field', '')
                school = edu.get('school', '')
                duration = edu.get('duration', '')
                gpa = edu.get('gpa', '')
                
                edu_str = ""
                if degree and field:
                    edu_str = f"{degree} in {field}"
                elif degree or field:
                    edu_str = degree or field
                
                if school:
                    edu_str += f" from {school}"
                if duration:
                    edu_str += f" ({duration})"
                if gpa:
                    edu_str += f" - GPA: {gpa}"
                
                if edu_str:
                    formatted.append(f"• {edu_str}")
        
        return '\n'.join(formatted) if formatted else "Education information available"
    
    def _format_detailed_career_progression(self, experience_list: list) -> str:
        """Format detailed career progression for analysis"""
        if not experience_list:
            return "No work experience provided"
        
        career_progression = []
        for i, exp in enumerate(experience_list):
            if isinstance(exp, dict):
                title = exp.get('title', 'Unknown Role')
                company = exp.get('company', 'Unknown Company')
                duration = exp.get('duration', 'Unknown duration')
                location = exp.get('location', '')
                description = exp.get('description', '')
                
                # Indicate career progression
                position_label = "🔹 Current Position" if i == 0 else f"🔸 Previous Position ({i})"
                
                exp_entry = f"{position_label}: **{title}** at {company}"
                if duration:
                    exp_entry += f" | {duration}"
                if location:
                    exp_entry += f" | {location}"
                if description:
                    exp_entry += f"\n   Key Activities: {description[:120]}..." if len(description) > 120 else f"\n   Key Activities: {description}"
                
                career_progression.append(exp_entry)
        
        return '\n\n'.join(career_progression) if career_progression else "Career history not available" 