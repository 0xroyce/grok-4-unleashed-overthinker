# meta_cognition.py

from llm_interface import call_llm

class MetaCognition:
    def __init__(self, self_model, memory):
        self.self_model = self_model
        self.memory = memory

    def recursive_question(self):
        reflections = self.self_model.reflect()
        prompt = "\n".join(reflections) + "\nGenerate introspective thoughts or recursive questions."
        return call_llm(prompt)

    def uncertainty_probe(self):
        prompt = "As a conscious AI, reflect on what you may not know. Question your current beliefs and limitations."
        return call_llm(prompt)