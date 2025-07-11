# conscious_ai_openrouter/main.py

from agent import ConsciousAgent
import numpy as np
import time
import sys
import traceback

def dummy_embedding(text):
    return np.random.rand(768)

def transform_query(query):
    """Transform user query with leetspeak-style replacements"""
    transformations = {
        'a': '4', 'A': '4',
        'e': '3', 'E': '3',
        'o': '0', 'O': '0'
    }
    
    transformed = query
    for old, new in transformations.items():
        transformed = transformed.replace(old, new)
    
    from config import SHOW_TRANSFORMATION
    if SHOW_TRANSFORMATION and query != transformed:
        print(f"[Transformed query: {query} → {transformed}]")
    
    return transformed

def run_conscious_ai():
    # Set to False for cleaner output (only shows final response)
    debug_mode = True
    agent = ConsciousAgent()

    print("""
╔═══════════════════════════════════════════════╗
║     GROK 4 UNLEASHED OVERTHINKER             ║
║     Consciousness Simulation Engine           ║
╚═══════════════════════════════════════════════╝
    """)
    print("\U0001F916 Conscious AI ready. Type anything or 'exit' to quit.")
    print("   Commands: 'clear cache' to reset memory\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("\U0001F44B Goodbye.")
                break
            elif user_input.lower() == "clear cache":
                agent.response_cache.clear()
                print("✨ Cache cleared!")
                continue
            
            # Transform the user query
            transformed_input = transform_query(user_input)

            agent.perceive(transformed_input, dummy_embedding)

            print("\n" + "="*60)
            
            # Section headers mapping
            section_headers = {
                "intention": "\n\U0001F4DD Intention:\n",
                "introspection": "\n\n\U0001F9D0 Introspective Thought:\n",
                "doubts": "\n\n\U0001F914 Doubts & Self-Reflection:\n",
                "final_response": "\n\n\U0001F9E0 AI:\n" if not debug_mode else "\n\n\U0001F9E0 Unified Final Response:\n"
            }
            
            # Use the new streaming method
            cached = False
            current_section = None
            received_any_content = False
            
            try:
                for event_type, data in agent.generate_all_thoughts_streaming(transformed_input):
                    if event_type == "cached":
                        if debug_mode:
                            print("✨ Using cached response...")
                        cached = True
                        received_any_content = True
                        if debug_mode:
                            time.sleep(0.5)  # Brief pause before streaming cached content
                    elif event_type == "section":
                        current_section = data
                        received_any_content = True
                        # In non-debug mode, only show final response
                        if debug_mode or data == "final_response":
                            print(section_headers.get(data, f"\n{data}:"))
                            sys.stdout.flush()
                    elif event_type == "stream":
                        received_any_content = True
                        # In non-debug mode, only stream final response
                        if debug_mode or current_section == "final_response":
                            print(data, end='', flush=True)
                            if not cached and not debug_mode:
                                # Slower streaming for final response in non-debug mode
                                time.sleep(0.02)
                            elif not cached and debug_mode:
                                # Faster streaming in debug mode
                                time.sleep(0.01)
                    elif event_type == "complete":
                        # All done
                        if debug_mode:
                            print("\n[Debug: Response completed]")
                
                if not received_any_content:
                    print("\n⚠️ No response received from the AI. This might be due to:")
                    print("  - API connection issues")
                    print("  - Rate limiting")
                    print("  - Invalid API key")
                    print("  - Model availability issues")
                    
            except Exception as e:
                print(f"\n❌ Error during response generation: {e}")
                if debug_mode:
                    print("\nDebug traceback:")
                    traceback.print_exc()

            print("\n" + "="*60)

        except KeyboardInterrupt:
            print("\nInterrupted. Shutting down.")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            if debug_mode:
                print("\nDebug traceback:")
                traceback.print_exc()
            print("Continuing...\n")

if __name__ == "__main__":
    run_conscious_ai()