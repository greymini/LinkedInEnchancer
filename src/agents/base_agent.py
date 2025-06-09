from agno.agent import Agent
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BaseLinkedInAgent(Agent):
    def __init__(self, name: str, gemini_client, memory_manager=None):
        super().__init__(name=name)
        self.gemini_client = gemini_client
        self.memory_manager = memory_manager
    
    async def execute_with_memory(self, task_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        try:
            # Retrieve relevant context from memory manager if available
            context = ""
            if self.memory_manager:
                context = await self.memory_manager.get_context(user_id, self.name)
            
            # Execute agent-specific logic
            result = await self.execute_task(task_data, context)
            
            # Store result in memory manager if available
            if self.memory_manager:
                await self.memory_manager.store_interaction(user_id, self.name, task_data, result)
            
            return result
            
        except Exception as e:
            print(f"Error in {self.name} agent: {e}")
            return {"error": f"Agent {self.name} encountered an error: {str(e)}"}
    
    @abstractmethod
    async def execute_task(self, task_data: Dict[str, Any], context: Optional[str]) -> Dict[str, Any]:
        """Execute the specific task for this agent"""
        pass
    
    def _format_experience_summary(self, experience_list: list) -> str:
        """Helper method to format experience for prompts"""
        if not experience_list:
            return "No experience data available"
        
        summary = []
        for exp in experience_list:
            if isinstance(exp, dict):
                title = exp.get('title', 'Unknown Title')
                company = exp.get('company', 'Unknown Company')
                duration = exp.get('duration', 'Unknown Duration')
                summary.append(f"{title} at {company} ({duration})")
        
        return "; ".join(summary)
    
    def _format_skills_list(self, skills_list: list) -> str:
        """Helper method to format skills for prompts"""
        if not skills_list:
            return "No skills data available"
        
        if isinstance(skills_list, list):
            return ", ".join(skills_list)
        
        return str(skills_list)
    
    def _extract_key_insights(self, response_text: str) -> Dict[str, Any]:
        """Helper method to extract structured insights from LLM response"""
        insights = {
            "recommendations": [],
            "strengths": [],
            "improvements": [],
            "score": None
        }
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for section headers
            if "recommendation" in line.lower() or "suggest" in line.lower():
                current_section = "recommendations"
            elif "strength" in line.lower() or "positive" in line.lower():
                current_section = "strengths" 
            elif "improvement" in line.lower() or "area" in line.lower():
                current_section = "improvements"
            elif "score" in line.lower() and any(char.isdigit() for char in line):
                # Extract score
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    insights["score"] = int(numbers[0])
            
            # Add content to current section
            if current_section and line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                content = line.lstrip('-•* 123456789.')
                if content:
                    insights[current_section].append(content)
        
        return insights 