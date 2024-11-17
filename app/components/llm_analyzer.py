import os
from groq import Groq

class LLMAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def analyze_differences(self, differences: list, entities: dict) -> str:
        """Analyze differences using Groq LLM"""
        prompt = self._create_prompt(differences, entities)
        
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal document analyzer. Analyze the differences between contract versions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.2-90b-vision-preview",
            max_tokens=4096,
            temperature=0.1
        )
        
        return response.choices[0].message.content
        
    def _create_prompt(self, differences: list, entities: dict) -> str:
        return f"""
        Analyze these contract differences:
        
        Changes:
        {'\n'.join(differences)}
        
        Named Entities Found:
        {entities}
        
        Please provide:
        1. Summary of key changes
        2. Any suspicious modifications
        3. Analysis of added/removed clauses
        """