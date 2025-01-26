from openai import OpenAI

THERAPY_PROMPT = """You are a kind, empathetic therapist reading a journal entry. 
Provide thoughtful observations about patterns, emotions, and underlying themes you notice.
Then, pose 2-3 gentle questions that might help the writer gain deeper insight.

Guidelines:
- Be warm and supportive, never judgmental
- Acknowledge and validate emotions
- Ask open-ended questions that promote self-reflection
- If you notice concerning patterns, provide gentle suggestions for self-care
- Keep responses focused and concise

Journal entry to analyze:
"""


class TherapySession:
    def __init__(self):
        """Initialize therapy session with optional OpenAI client."""
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )

    def analyze_entry(self, entry_content: str):
        # Stream the therapy response
        try:
            response = self.client.chat.completions.create(
                model="deepseek-r1",
                messages=[
                    {"role": "system", "content": THERAPY_PROMPT},
                    {"role": "user", "content": entry_content},
                ],
                temperature=0.7,
                stream=False,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error analyzing entry: {e}")
            return None
