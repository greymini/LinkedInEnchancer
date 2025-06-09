import google.generativeai as genai
from typing import List, Dict, Optional
import json
import re
import asyncio
from ..config.settings import settings

class GeminiClient:
    def __init__(self, api_key: str = None):
        api_key = api_key or settings.GEMINI_API_KEY
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response using Gemini model
        """
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=settings.MAX_OUTPUT_TOKENS,
            top_p=0.8,
            top_k=40
        )
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"
        
    async def analyze_profile_structured(
        self, 
        profile_data: Dict,
        analysis_type: str
    ) -> Dict:
        """
        Structured analysis with JSON output
        """
        prompt = self.build_analysis_prompt(profile_data, analysis_type)
        
        response = await self.generate_response(
            prompt + "\n\nRespond in valid JSON format.",
            temperature=0.3
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from response
            return self.extract_json_from_text(response)
    
    def build_analysis_prompt(self, profile_data: Dict, analysis_type: str) -> str:
        """Build analysis prompt based on type"""
        if analysis_type == "profile_completeness":
            return f"""
            Analyze this LinkedIn profile for completeness and professional quality:
            
            Profile Data: {json.dumps(profile_data, indent=2)}
            
            Provide analysis in JSON format with:
            {{
                "completeness_score": <0-100>,
                "missing_sections": [list of missing sections],
                "strengths": [list of strengths],
                "improvement_areas": [list of areas to improve],
                "recommendations": [specific actionable recommendations]
            }}
            """
        elif analysis_type == "job_match":
            return f"""
            Analyze job match compatibility:
            
            Profile: {profile_data.get('profile', {})}
            Job: {profile_data.get('job', {})}
            
            Provide analysis in JSON format with:
            {{
                "score": <0-100>,
                "breakdown": {{
                    "skills_match": <0-100>,
                    "experience_match": <0-100>,
                    "education_match": <0-100>
                }},
                "missing_skills": [list of missing skills],
                "suggestions": [improvement suggestions]
            }}
            """
        else:
            return f"Analyze this profile data: {json.dumps(profile_data, indent=2)}"
    
    def extract_json_from_text(self, text: str) -> Dict:
        """Extract JSON from text response as fallback"""
        # Try to find JSON-like content
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        # Fallback to basic structured response
        return {
            "error": "Could not parse structured response",
            "raw_response": text
        } 