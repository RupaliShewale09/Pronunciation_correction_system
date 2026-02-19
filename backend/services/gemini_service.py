# gemini api integration

import os
import json
from typing import Dict, List
from loguru import logger
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai not installed. Install with: pip install google-genai")



class GeminiService:
    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai package not installed")
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(
            api_key=api_key
        )

        self.model_name = "gemini-2.5-flash-lite"
    
    # ===================================================================
    def generate_feedback(self, 
                         target_word: str, 
                         transcript: str,
                         phoneme_errors: Dict,
                         score: float,
    ) -> Dict[str, str]:

        
        # Handle perfect pronunciation
        if score >= 95:
            return {
                'feedback': f"Excellent pronunciation of '{target_word}'! Your articulation is very clear.",
                'tips': "Keep practicing to maintain this level of accuracy."
            }
        
        # Build error description
        error_description = ""
        if phoneme_errors:
            error_list = []
            for phoneme, details in phoneme_errors.items():
                error_list.append(f"{phoneme} (heard as: {details.get('heard', 'unclear')})")
            error_description = ", ".join(error_list)
        
        prompt = f"""You are a spoken English pronunciation tutor giving verbal-style coaching.

            Context:
            - Target word: "{target_word}"
            - Student said: "{transcript}"
            - Score: {score}%
            - Phoneme issues: {error_description if error_description else "General clarity issue"}

            Instructions:
            1. Feedback: 1–2 short sentences explaining the main mistake.
            2. Tips: Break the word into parts (2–3 parts max).
            - Show how it sounds in simple phonetic form (like: duh-VEL-up).
            - Give very short articulation guidance (tongue, lips, stress).
            - Keep it verbal and natural (like a tutor speaking).
            3. Total response under 90 words.
            4. No long paragraphs.
            5. No technical phoneme symbols (no IPA).
            6. DO NOT use asterisks, bold symbols, markdown, all capitals or special characters.

            Return ONLY valid JSON:

            {{
            "feedback": "short explanation",
            "tips": "Short breakdown with guidance"
            }}
            """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,)
            result_text = response.text.strip()
            
            # Try to parse JSON response
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            elif result_text.startswith('```'):
                result_text = result_text.replace('```', '').strip()
            
            result = json.loads(result_text)
            return {
                'feedback': result.get('feedback', 'Keep practicing!'),
                'tips': result.get('tips', 'Focus on clear articulation.')
            }
        
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                'feedback': response.text if hasattr(response, 'text') else "Good effort! Keep practicing.",
                'tips': "Focus on pronouncing each sound clearly and slowly at first."
            }
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {
                'feedback': f"Score: {score}%. Continue practicing '{target_word}'.",
                'tips': "Listen to the reference pronunciation and try to match the sounds."
            }
    
    # ================================================================
    def suggest_practice_words(self, 
                               problematic_phonemes: List[str],
                               mastered_words: List[str],
                               difficulty_level: str = "medium"
                               
    ) -> List[Dict[str, str]]:

        phonemes_str = (
            ", ".join(problematic_phonemes)
            if problematic_phonemes
            else "general pronunciation"
        )
        mastered_str = ", ".join(mastered_words[:5]) if mastered_words else "none yet"
        
        prompt = f"""You are helping a student improve English pronunciation.

        Their weak areas: {phonemes_str}
        Words they've mastered: {mastered_str}
        Difficulty level: {difficulty_level}

        Generate 5 practice words that:
        1. Target their weak phonemes
        2. Are progressively challenging
        3. Are different from mastered words

        Format as JSON array:
        [
            {{"word": "word1", "reason": "why this helps"}},
            {{"word": "word2", "reason": "why this helps"}},
            ...
        ]

        Keep words practical and commonly used."""

        try:
            logger.debug("Sending prompt to Gemini for word suggestions")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            result_text = response.text.strip()
            
            # Clean markdown formatting
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            elif result_text.startswith('```'):
                result_text = result_text.replace('```', '').strip()
            
            suggestions = json.loads(result_text)
            if not isinstance(suggestions, list):
                logger.error("Gemini did not return list")
                raise ValueError("Invalid AI format")
            
            return suggestions[:5]  # Ensure max 5 suggestions
        
        except Exception as e:
            logger.exception(f"Gemini suggestion error {e}")
            # Fallback suggestions
            return [
                {"word": "practice", "reason": "Common word with multiple sounds"},
                {"word": "think", "reason": "Practice the 'th' sound"},
                {"word": "world", "reason": "Practice 'r' and 'l' sounds"},
                {"word": "beautiful", "reason": "Multi-syllable word practice"},
                {"word": "through", "reason": "Challenging pronunciation"}
            ]
    

    # ==============================================================
    def generate_progress_report(self, 
                                 user_stats: Dict,
                                 recent_attempts: List[Dict]
        ) -> str:
        
        attempts_summary = ""
        if recent_attempts:
            attempts_summary = "\n".join([
                f"- {att.get('target_word')}: {att.get('score')}% (attempt #{att.get('attempt_number')})"
                for att in recent_attempts[:10]
            ])
        
        prompt = f"""You are a supportive pronunciation coach writing a progress report.

        Student Statistics:
        - Total practice attempts: {user_stats.get('total_attempts', 0)}
        - Words mastered: {user_stats.get('words_mastered', 0)}
        - Average score: {user_stats.get('average_score', 0)}%
        - Current practice streak: {user_stats.get('current_streak', 0)} days
        - Problematic sounds: {', '.join(user_stats.get('problematic_phonemes', {}).keys()) or 'None identified yet'}

        Recent Practice Sessions:
        {attempts_summary if attempts_summary else "No recent attempts"}

        Write an encouraging 3-paragraph progress report:
        1. Celebrate their achievements and progress
        2. Identify patterns and areas for improvement
        3. Provide specific next steps

        Keep it motivating, specific, and under 100 words."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text.strip()
        
        except Exception as e:
            print(f"Gemini API error in progress report: {e}")
            return f"""Great work on your pronunciation journey! You've completed {user_stats.get('total_attempts', 0)} practice attempts and mastered {user_stats.get('words_mastered', 0)} words with an average score of {user_stats.get('average_score', 0)}%.

            Your current practice streak is {user_stats.get('current_streak', 0)} days - keep up the consistent effort! 

            Continue focusing on the sounds that challenge you, and remember that regular practice is the key to improvement."""
    
    # =======================================================================
    def check_grammar(self, text: str) -> Dict:
        prompt = f"""You are an English linguistics expert. Analyze the grammatical structure of: "{text}"
        RULES:
            1. IGNORE capitalization (e.g., 'i' vs 'I' is NOT an error).
            2. IGNORE missing periods or commas at the end.
            3. ONLY flag errors in verb tense, word order, subject-verb agreement, or missing essential words.
        If the grammar is correct, return only: {{"status": "correct"}}
        If there are mistakes, return:
        {{
            "status": "wrong",
            "correction": "the full corrected sentence",
            "explanation": "a very brief explanation of the fix (max 15 words)"
        }}
        Return ONLY valid JSON. No markdown formatting."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            result_text = response.text.strip()
            # Clean markdown if present
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(result_text)
        except Exception as e:
            logger.error(f"Grammar check failed: {e}")
            return {"status": "error", "message": "Grammar check unavailable"}

# ===============================================
# Singleton instance
_gemini_service = None

def get_gemini_service():
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        try:
            _gemini_service = GeminiService()
        except Exception as e:
            print(f"Failed to initialize Gemini service: {e}")
            return None
    return _gemini_service
