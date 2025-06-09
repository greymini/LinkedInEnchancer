"""
Prompt templates for different LinkedIn Enhancer agents
"""

PROFILE_ANALYSIS_PROMPTS = {
    "about_analysis": """
    Analyze this LinkedIn 'About' section for professional quality and impact:
    
    About Text: "{about_text}"
    
    Please provide:
    1. Overall quality score (1-10)
    2. Specific strengths
    3. Areas for improvement
    4. Suggestions for better keywords
    5. Recommended structure improvements
    
    Focus on professional tone, keyword optimization, and compelling storytelling.
    """,
    
    "experience_analysis": """
    Analyze this work experience entry for LinkedIn profile optimization:
    
    Job Title: {job_title}
    Company: {company}
    Description: {description}
    Duration: {duration}
    
    Evaluate:
    1. Description quality and impact
    2. Quantifiable achievements
    3. Keyword optimization
    4. Professional language
    5. Specific improvement suggestions
    
    Provide actionable recommendations to make this experience more compelling.
    """,
    
    "skills_analysis": """
    Analyze these LinkedIn skills for professional relevance and market demand:
    
    Current Skills: {skills_list}
    Target Industry: {target_industry}
    
    Provide:
    1. Skills alignment with industry standards
    2. Missing high-demand skills
    3. Skills to prioritize/highlight
    4. Skills that may be outdated
    5. Recommendations for skill development
    """
}

JOB_MATCHING_PROMPTS = {
    "compatibility_analysis": """
    Analyze the compatibility between this profile and job requirements:
    
    PROFILE SUMMARY:
    - Name: {full_name}
    - Headline: {headline}
    - Skills: {skills}
    - Experience: {experience_summary}
    
    JOB REQUIREMENTS:
    - Title: {job_title}
    - Required Skills: {required_skills}
    - Requirements: {job_requirements}
    - Responsibilities: {job_responsibilities}
    
    Provide detailed analysis:
    1. Overall compatibility score (0-100)
    2. Skills match breakdown
    3. Experience relevance
    4. Missing qualifications
    5. Specific improvement recommendations
    6. Timeline for skill development
    """,
    
    "skill_gap_analysis": """
    Identify skill gaps between profile and target role:
    
    Current Skills: {current_skills}
    Required Skills: {required_skills}
    Target Role: {target_role}
    
    Analysis needed:
    1. Critical missing skills
    2. Skills that need strengthening
    3. Learning priorities
    4. Recommended resources/courses
    5. Estimated learning timeline
    """
}

CONTENT_GENERATION_PROMPTS = {
    "about_section": """
    Generate an optimized LinkedIn 'About' section based on this profile:
    
    Current About: {current_about}
    Name: {full_name}
    Current Role: {current_role}
    Key Skills: {key_skills}
    Career Goals: {career_goals}
    Notable Achievements: {achievements}
    
    Create a compelling About section that:
    1. Starts with a strong hook
    2. Highlights key achievements
    3. Includes relevant keywords
    4. Shows personality and passion
    5. Ends with a call-to-action
    6. Is 2-3 paragraphs, professional yet engaging
    """,
    
    "headline_optimization": """
    Create optimized LinkedIn headlines for this profile:
    
    Current Headline: {current_headline}
    Current Role: {current_role}
    Key Skills: {key_skills}
    Industry: {industry}
    Career Level: {career_level}
    
    Generate 5 alternative headlines that:
    1. Include relevant keywords
    2. Show value proposition
    3. Are within 220 characters
    4. Sound professional yet distinctive
    5. Attract the right audience
    """,
    
    "experience_description": """
    Optimize this work experience description:
    
    Current Description: {current_description}
    Job Title: {job_title}
    Company: {company}
    Industry: {industry}
    Key Responsibilities: {responsibilities}
    Achievements: {achievements}
    
    Create an improved description that:
    1. Starts with strong action verbs
    2. Quantifies achievements where possible
    3. Includes relevant keywords
    4. Shows progression and impact
    5. Is 2-4 bullet points or short paragraph
    """
}

CAREER_COUNSELING_PROMPTS = {
    "career_path_analysis": """
    Analyze career progression and provide guidance:
    
    Current Profile:
    - Experience: {experience_summary}
    - Skills: {skills}
    - Education: {education}
    - Career Goals: {career_goals}
    
    Provide comprehensive career guidance:
    1. Career trajectory analysis
    2. Potential career paths
    3. Skills development priorities
    4. Industry trends relevant to career
    5. Networking recommendations
    6. Timeline for career goals
    7. Potential obstacles and solutions
    """,
    
    "industry_transition": """
    Provide guidance for industry transition:
    
    Current Industry: {current_industry}
    Target Industry: {target_industry}
    Current Skills: {current_skills}
    Transferable Skills: {transferable_skills}
    Experience Level: {experience_level}
    
    Transition strategy:
    1. Skill gap analysis
    2. Transferable skills highlight
    3. Industry entry strategies
    4. Networking approaches
    5. Portfolio/project recommendations
    6. Timeline and milestones
    7. Potential challenges and solutions
    """,
    
    "personal_branding": """
    Develop personal branding strategy:
    
    Professional Background: {background}
    Unique Strengths: {strengths}
    Target Audience: {target_audience}
    Career Goals: {career_goals}
    Industry: {industry}
    
    Personal branding recommendations:
    1. Brand positioning statement
    2. Key messages to communicate
    3. Content strategy for LinkedIn
    4. Professional image optimization
    5. Thought leadership opportunities
    6. Networking strategy
    7. Online presence optimization
    """
}

CONVERSATION_PROMPTS = {
    "context_summary": """
    Summarize this conversation context for continuity:
    
    Previous Interactions: {interactions}
    User Profile: {user_profile}
    Current Goals: {current_goals}
    
    Provide:
    1. Key conversation points
    2. User's main objectives
    3. Progress made so far
    4. Outstanding action items
    5. Context for next interaction
    """,
    
    "follow_up_suggestions": """
    Based on our conversation, suggest follow-up actions:
    
    Discussion Topics: {discussion_topics}
    User Goals: {user_goals}
    Recommendations Given: {recommendations}
    User's Response: {user_response}
    
    Suggest:
    1. Immediate next steps
    2. Long-term action items
    3. Check-in timeline
    4. Additional resources
    5. Success metrics to track
    """
} 