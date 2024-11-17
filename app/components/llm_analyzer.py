# app/components/llm_analyzer.py
import os
from groq import Groq

class LLMAnalyzer:
    MODEL_NAME = "llama-3.2-90b-vision-preview"
    MAX_CHUNK_TOKENS = 2048  # Conservative limit per chunk
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        self.client = Groq(api_key=api_key)

    def _chunk_differences(self, differences: list[str], chunk_size: int = 10) -> list[list[str]]:
        """Split differences into manageable chunks"""
        return [differences[i:i + chunk_size] for i in range(0, len(differences), chunk_size)]

    def _analyze_chunk(self, chunk: list[str], entities: dict) -> str:
        """Analyze a single chunk of differences"""
        prompt = self._create_prompt(chunk, entities)
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal document analyzer. Analyze the differences between contract versions."
                },
                {"role": "user", "content": prompt}
            ],
            model=self.MODEL_NAME,
            max_tokens=self.MAX_CHUNK_TOKENS,
            temperature=0.1
        )
        return response.choices[0].message.content

    def _synthesize_analyses(self, analyses: list[str]) -> str:
        """Combine multiple chunk analyses into coherent summary"""
        synthesis_prompt = f"""
        Synthesize these analysis chunks into a coherent summary:
        
        {'\n'.join(analyses)}
        
        Provide:
        1. Overall summary of key changes
        2. Major suspicious modifications
        3. Critical clause changes
        """
        
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Synthesize multiple contract analysis chunks into a coherent summary."
                },
                {"role": "user", "content": synthesis_prompt}
            ],
            model=self.MODEL_NAME,
            max_tokens=2048,
            temperature=0.1
        )
        return response.choices[0].message.content

    def analyze_differences(self, differences: list[str], entities: dict) -> str:
        """Analyze differences using chunking for large inputs"""
        try:
            # Split into chunks if too large
            if len(differences) > 1500:  # Arbitrary threshold
                chunks = self._chunk_differences(differences)
                chunk_analyses = []
                
                for chunk in chunks:
                    analysis = self._analyze_chunk(chunk, entities)
                    chunk_analyses.append(analysis)
                
                # Synthesize all chunk analyses
                return self._synthesize_analyses(chunk_analyses)
            else:
                # Original direct analysis for small inputs
                return self._analyze_chunk(differences, entities)
                
        except Exception as e:
            raise RuntimeError(f"Error analyzing differences: {str(e)}")
        
    def _create_prompt(self, differences: list, entities: dict) -> str:
        """Create prompt for LLM analysis"""
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