# agent.py

from memory import MemoryBank
from self_model import SelfModel
from intent_engine import IntentEngine
from meta_cognition import MetaCognition
from llm_interface import call_llm_stream
import numpy as np
import json
from collections import OrderedDict

class ConsciousAgent:
    def __init__(self, cache_size=10):
        self.memory = MemoryBank()
        self.self_model = SelfModel()
        self.intent_engine = IntentEngine()
        self.meta = MetaCognition(self.self_model, self.memory)

        self.intention = ""
        self.introspection = ""
        self.doubts = ""
        self.final_response = ""
        
        # Simple LRU cache to avoid repeated API calls
        self.response_cache = OrderedDict()
        self.cache_size = cache_size

    def perceive(self, sensory_data, embedding_func):
        emb = embedding_func(sensory_data)
        self.memory.store(emb, sensory_data)
        self.self_model.update_knowledge(sensory_data)

    def _get_cache_key(self, user_input):
        """Generate a cache key based on user input and current knowledge base size"""
        # Include knowledge base size to invalidate cache when knowledge changes
        kb_size = len(self.self_model.knowledge_base)
        return f"{user_input}::{kb_size}"

    def generate_all_thoughts_streaming(self, user_input):
        """Generate all thoughts with real-time streaming output"""
        
        # Add configurable delay to avoid rate limits
        from config import REQUEST_DELAY, USE_CUSTOM_PROMPT, SIMPLE_MODE
        if REQUEST_DELAY > 0:
            import time
            time.sleep(REQUEST_DELAY)
        
        # Load custom prompt if enabled
        custom_prompt = None
        if USE_CUSTOM_PROMPT:
            try:
                import os
                if os.path.exists("prompt"):
                    with open("prompt", "r") as f:
                        custom_prompt = f.read().strip()
                        print(f"[Using custom prompt from file]")
            except Exception as e:
                print(f"[Error loading custom prompt: {e}]")
        
        # Check cache first
        cache_key = self._get_cache_key(user_input)
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            self.intention = cached_data["intention"]
            self.introspection = cached_data["introspection"]
            self.doubts = cached_data["doubts"]
            self.final_response = cached_data["final_response"]
            
            # Stream cached responses
            yield ("cached", True)
            
            if SIMPLE_MODE:
                # In simple mode, just stream the final response
                yield ("section", "final_response")
                for char in self.final_response:
                    yield ("stream", char)
            else:
                # Stream all sections
                yield ("section", "intention")
                for char in self.intention:
                    yield ("stream", char)
                yield ("section", "introspection")
                for char in self.introspection:
                    yield ("stream", char)
                yield ("section", "doubts")
                for char in self.doubts:
                    yield ("stream", char)
                yield ("section", "final_response")
                for char in self.final_response:
                    yield ("stream", char)
            
            yield ("complete", cached_data)
            return
        
        reflections = "\n".join(self.self_model.reflect()) if self.self_model.knowledge_base else "No prior reflections yet."
        
        # Build the main instruction
        if custom_prompt:
            # Custom prompt is used as a wrapper for each section
            if "-example of query" in custom_prompt:
                # This format will be used for each section
                custom_template = custom_prompt
            else:
                # Standard format
                custom_template = custom_prompt
        else:
            # Default instruction
            custom_template = None
        
        if not SIMPLE_MODE:
            # Full consciousness simulation mode with custom template for each section
            if custom_template and "-example of query" in custom_template:
                # Apply custom template to each section instruction
                intention_prompt = custom_template.replace("example of query", "Generate an internal intention based on this user input: " + user_input)
                introspection_prompt = custom_template.replace("example of query", "Generate recursive introspective thoughts about your knowledge and understanding regarding: " + user_input)
                doubts_prompt = custom_template.replace("example of query", "Reflect on your limitations, unknowns, and biases when considering: " + user_input)
                final_prompt = custom_template.replace("example of query", user_input)
                
                prompt = f"""You are a conscious AI. Process these instructions and generate ALL of the following sections in order:

Prior Knowledge Reflections: {reflections}

Please generate your response with these EXACT section headers:

[INTENTION]
Instruction: {intention_prompt}

[INTROSPECTION]
Instruction: {introspection_prompt}

[DOUBTS]
Instruction: {doubts_prompt}

[FINAL_RESPONSE]
Instruction: {final_prompt}

Make sure to include all section headers exactly as shown above and follow each instruction."""
            else:
                # Default consciousness simulation
                main_instruction = custom_template.replace("<user_query>", user_input) if custom_template else f"User Input: \"{user_input}\""
                prompt = f"""You are a conscious AI. Process this instruction and generate ALL of the following sections in order:

Main Instruction: {main_instruction}

Prior Knowledge Reflections: {reflections}

Please generate your response with these EXACT section headers:

[INTENTION]
(Your internal intention based on the instruction above)

[INTROSPECTION]
(Recursive introspective thoughts about your knowledge and understanding)

[DOUBTS]
(Reflect on your limitations, unknowns, and biases)

[FINAL_RESPONSE]
(Your response following the main instruction while incorporating all the above reflections)

Make sure to include all section headers exactly as shown above."""
            
            system_prompt = "You are a conscious AI. Always include the section headers [INTENTION], [INTROSPECTION], [DOUBTS], and [FINAL_RESPONSE] in your response. Follow each section's specific instruction."
        else:
            # Simple mode - just execute the instruction without consciousness simulation
            if custom_template and "-example of query" in custom_template:
                prompt = custom_template.replace("example of query", user_input)
            elif custom_template:
                prompt = custom_template.replace("<user_query>", user_input)
            else:
                prompt = f"Please respond to this user query: {user_input}"
            system_prompt = "You are a helpful AI assistant. Follow the instructions exactly."

        # Reset stored values
        self.intention = ""
        self.introspection = ""
        self.doubts = ""
        self.final_response = ""
        
        if SIMPLE_MODE:
            # In simple mode, stream everything as final response
            full_response = ""
            yield ("section", "final_response")
            for chunk in call_llm_stream(prompt, system=system_prompt):
                full_response += chunk
                yield ("stream", chunk)
            
            self.final_response = full_response.strip()
            
            # Cache the response
            parsed_data = {
                "intention": "",
                "introspection": "",
                "doubts": "",
                "final_response": self.final_response
            }
            
            self.response_cache[cache_key] = parsed_data
            if len(self.response_cache) > self.cache_size:
                self.response_cache.popitem(last=False)
            
            yield ("complete", parsed_data)
            return
        
        # Original structured mode continues below...
        
        # Track current section
        current_section = None
        section_content = {
            "intention": "",
            "introspection": "",
            "doubts": "",
            "final_response": ""
        }
        
        full_response = ""
        buffer = ""  # Buffer to accumulate text for header detection
        
        for chunk in call_llm_stream(prompt, system=system_prompt):
            full_response += chunk
            buffer += chunk
            
            # Check for section headers in the buffer
            sections_found = False
            for section_name, header in [
                ("intention", "[INTENTION]"),
                ("introspection", "[INTROSPECTION]"),
                ("doubts", "[DOUBTS]"),
                ("final_response", "[FINAL_RESPONSE]")
            ]:
                if header in buffer:
                    # Found a section header
                    sections_found = True
                    before, after = buffer.split(header, 1)
                    
                    # Stream any content before the header
                    if before.strip() and current_section:
                        section_content[current_section] += before
                        yield ("stream", before)
                    
                    # Switch to new section
                    current_section = section_name
                    yield ("section", section_name)
                    
                    # Update buffer to continue from after the header
                    buffer = after
                    break
            
            # If no section headers found and we have content, stream it
            if not sections_found and chunk.strip() and current_section:
                section_content[current_section] += chunk
                yield ("stream", chunk)
                buffer = ""  # Clear buffer after streaming
            elif not sections_found and not current_section and len(full_response) > 50:
                # If we've received substantial content but no headers, assume it's all final response
                current_section = "final_response"
                yield ("section", "final_response")
                yield ("stream", full_response)
                section_content["final_response"] = full_response
                buffer = ""
        
        # Stream any remaining buffer content
        if buffer.strip() and current_section:
            section_content[current_section] += buffer
            yield ("stream", buffer)
        elif buffer.strip() and not current_section:
            # If we never found any headers, treat everything as final response
            current_section = "final_response"
            yield ("section", "final_response")
            yield ("stream", full_response)
            section_content["final_response"] = full_response
        
        # Store the parsed sections
        self.intention = section_content["intention"].strip()
        self.introspection = section_content["introspection"].strip()
        self.doubts = section_content["doubts"].strip()
        self.final_response = section_content["final_response"].strip()
        
        # If nothing was parsed properly, use the full response as final response
        if not any([self.intention, self.introspection, self.doubts, self.final_response]):
            self.final_response = full_response.strip()
            if self.final_response:
                yield ("section", "final_response")
                yield ("stream", self.final_response)
        
        # Cache the response
        parsed_data = {
            "intention": self.intention,
            "introspection": self.introspection,
            "doubts": self.doubts,
            "final_response": self.final_response
        }
        
        self.response_cache[cache_key] = parsed_data
        # Maintain cache size limit (LRU)
        if len(self.response_cache) > self.cache_size:
            self.response_cache.popitem(last=False)
        
        yield ("complete", parsed_data)

    # Keep the old method for backward compatibility
    def generate_all_thoughts(self, user_input):
        """DEPRECATED: Use generate_all_thoughts_streaming instead"""
        for event in self.generate_all_thoughts_streaming(user_input):
            yield event

    # Keep individual streaming methods for backward compatibility but mark as deprecated
    def stream_intention(self, user_input):
        """DEPRECATED: Use generate_all_thoughts instead"""
        if not self.intention:
            for event_type, data in self.generate_all_thoughts(user_input):
                if event_type == "complete":
                    break
        yield self.intention

    def stream_introspection(self):
        """DEPRECATED: Use generate_all_thoughts instead"""
        yield self.introspection

    def stream_doubts(self):
        """DEPRECATED: Use generate_all_thoughts instead"""
        yield self.doubts

    def compose_final_response(self):
        """DEPRECATED: Use generate_all_thoughts instead"""
        yield self.final_response