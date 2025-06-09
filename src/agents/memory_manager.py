import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class SimpleMemoryManager:
    """Simplified memory manager using JSON-based storage"""
    
    def __init__(self, memory_store_path: str):
        self.memory_store_path = memory_store_path
        
        # Create storage directories
        os.makedirs(memory_store_path, exist_ok=True)
        
        # Simple JSON-based storage for persistence
        self.profile_file = os.path.join(memory_store_path, "profiles.json")
        self.conversations_file = os.path.join(memory_store_path, "conversations.json")
        self.goals_file = os.path.join(memory_store_path, "goals.json")
        
        # Load existing data
        self.profiles = self._load_json_file(self.profile_file)
        self.conversations = self._load_json_file(self.conversations_file)
        self.goals = self._load_json_file(self.goals_file)
        
        # In-memory storage for current session
        self.session_memory = {}
        
    def _load_json_file(self, file_path: str) -> Dict:
        """Load JSON file or return empty dict"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
        return {}
    
    def _save_json_file(self, file_path: str, data: Dict):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
    
    async def store_profile(self, user_id: str, profile_data: Dict):
        """Store user profile data"""
        try:
            # Store in session memory
            self.session_memory[f"profile_{user_id}"] = profile_data
            
            # Also store in JSON for persistence
            self.profiles[user_id] = {
                "profile_data": profile_data,
                "timestamp": datetime.now().isoformat()
            }
            self._save_json_file(self.profile_file, self.profiles)
            
        except Exception as e:
            print(f"Error storing profile: {e}")
    
    async def store_interaction(self, user_id: str, agent_name: str, query: Dict, response: Dict):
        """Store conversation interaction"""
        try:
            interaction_id = f"{user_id}_{agent_name}_{datetime.now().timestamp()}"
            
            interaction_data = {
                "user_id": user_id,
                "agent_name": agent_name,
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in session memory
            self.session_memory[interaction_id] = interaction_data
            
            # Also store in JSON for persistence
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            
            self.conversations[user_id].append(interaction_data)
            
            # Keep only last 50 conversations per user to prevent memory bloat
            if len(self.conversations[user_id]) > 50:
                self.conversations[user_id] = self.conversations[user_id][-50:]
            
            self._save_json_file(self.conversations_file, self.conversations)
            
        except Exception as e:
            print(f"Error storing interaction: {e}")
    
    async def get_context(self, user_id: str, agent_name: str, query: str = "") -> str:
        """Retrieve relevant context"""
        context = "Previous Context:\n"
        
        try:
            # Get user profile from session memory first, fallback to JSON
            profile_data = self.session_memory.get(f"profile_{user_id}")
            if not profile_data and user_id in self.profiles:
                profile_data = self.profiles[user_id]["profile_data"]
            
            if profile_data:
                profile_summary = self._profile_to_text(profile_data)
                context += f"User Profile: {profile_summary}\n\n"
            
            # Get recent conversations for this agent
            recent_conversations = self._get_recent_conversations(user_id, agent_name)
            if recent_conversations:
                context += f"Recent Interactions:\n{recent_conversations}\n\n"
            
            # Get career goals if any
            goals_context = self._get_goals_context(user_id)
            if goals_context:
                context += f"Career Goals: {goals_context}\n"
                
        except Exception as e:
            print(f"Error getting context: {e}")
            context = "No previous context available."
        
        return context
    
    def _get_recent_conversations(self, user_id: str, agent_name: str) -> str:
        """Get recent conversations for the specific agent"""
        try:
            if user_id not in self.conversations:
                return ""
            
            # Filter conversations for this agent
            agent_conversations = [
                conv for conv in self.conversations[user_id]
                if conv.get("agent_name") == agent_name
            ]
            
            # Get last 3 conversations
            recent = agent_conversations[-3:] if len(agent_conversations) > 3 else agent_conversations
            
            context_text = ""
            for conv in recent:
                query_str = str(conv.get('query', ''))[:100] + "..." if len(str(conv.get('query', ''))) > 100 else str(conv.get('query', ''))
                response_str = str(conv.get('response', ''))[:100] + "..." if len(str(conv.get('response', ''))) > 100 else str(conv.get('response', ''))
                context_text += f"- Q: {query_str} -> A: {response_str}\n"
            
            return context_text
            
        except Exception as e:
            print(f"Error getting recent conversations: {e}")
            return ""
    
    async def store_career_goals(self, user_id: str, goals: Dict):
        """Store user's career goals"""
        try:
            # Store in session memory
            self.session_memory[f"goals_{user_id}"] = goals
            
            # Also store in JSON
            self.goals[user_id] = {
                "goals": goals,
                "timestamp": datetime.now().isoformat()
            }
            self._save_json_file(self.goals_file, self.goals)
            
        except Exception as e:
            print(f"Error storing career goals: {e}")
    
    def _get_goals_context(self, user_id: str) -> str:
        """Get user's career goals"""
        try:
            # Try session memory first
            goals_data = self.session_memory.get(f"goals_{user_id}")
            if not goals_data and user_id in self.goals:
                goals_data = self.goals[user_id]["goals"]
            
            if goals_data:
                return f"Target Role: {goals_data.get('target_role', '')} Industry: {goals_data.get('industry', '')} Skills: {goals_data.get('desired_skills', [])}"
            
        except Exception as e:
            print(f"Error getting goals context: {e}")
        
        return ""
    
    def _profile_to_text(self, profile_data: Dict) -> str:
        """Convert profile data to searchable text"""
        text_parts = []
        
        try:
            if "full_name" in profile_data:
                text_parts.append(f"Name: {profile_data['full_name']}")
                
            if "headline" in profile_data:
                text_parts.append(f"Headline: {profile_data['headline']}")
                
            if "about" in profile_data:
                about_text = profile_data['about'][:200] + "..." if len(profile_data['about']) > 200 else profile_data['about']
                text_parts.append(f"About: {about_text}")
                
            if "skills" in profile_data:
                skills = profile_data['skills']
                if isinstance(skills, list):
                    text_parts.append(f"Skills: {', '.join(skills[:10])}")  # Limit to first 10 skills
                
            if "experience" in profile_data:
                exp_text = []
                for exp in profile_data["experience"][:3]:  # Limit to first 3 experiences
                    if isinstance(exp, dict):
                        exp_text.append(f"{exp.get('title', '')} at {exp.get('company', '')}")
                text_parts.append(f"Experience: {'; '.join(exp_text)}")
                
        except Exception as e:
            print(f"Error converting profile to text: {e}")
            
        return " | ".join(text_parts) if text_parts else "No profile data"

class MemoryManagerAgent:
    """Wrapper to maintain compatibility with existing code"""
    def __init__(self, memory_store_path: str):
        self.memory_manager = SimpleMemoryManager(memory_store_path)
        
    async def store_profile(self, user_id: str, profile_data: Dict):
        return await self.memory_manager.store_profile(user_id, profile_data)
        
    async def store_interaction(self, user_id: str, agent_name: str, query: Dict, response: Dict):
        return await self.memory_manager.store_interaction(user_id, agent_name, query, response)
        
    async def get_context(self, user_id: str, agent_name: str, query: str = "") -> str:
        return await self.memory_manager.get_context(user_id, agent_name, query)
        
    async def store_career_goals(self, user_id: str, goals: Dict):
        return await self.memory_manager.store_career_goals(user_id, goals) 