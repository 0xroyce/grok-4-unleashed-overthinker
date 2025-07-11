# intent_engine.py

from llm_interface import call_llm

class IntentEngine:
    def __init__(self):
        self.current_intention = None

    def generate_intention(self, recent_context):
        prompt = f"""
You are an introspective AI. Based on the recent interaction:
"{recent_context}"
Generate a meaningful internal intention to guide your thought process.
"""
        self.current_intention = call_llm(prompt)
        return self.current_intention

    def evaluate_progress(self):
        return f"Progress on '{self.current_intention}': subjective."