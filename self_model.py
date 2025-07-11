# self_model.py

class SelfModel:
    def __init__(self):
        self.knowledge_base = []

    def update_knowledge(self, info):
        if info not in self.knowledge_base:
            self.knowledge_base.append(info)

    def reflect(self):
        reflections = []
        for item in self.knowledge_base:
            reflections.append(f"What do I know about {item}? How confident am I?")
        return reflections