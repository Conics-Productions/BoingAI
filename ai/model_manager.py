from llama_cpp import Llama
import os
from ai.web_search import search_web
from ai.memory_manager import MemoryManager

GGUF_MODELS = {
    "Qwen 2.5 Chat (1.5B)": "models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    "Llama 3.2 Chat (1B)": "models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    "Gemma 2 Chat (2B)": "models/gemma-2-2b-it-Q4_K_M.gguf",
    "Qwen 2.5 Coder (1.5B)": "models/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
}

class AIModelEngine:
    def __init__(self):
        self.llm = None
        self.memory_mgr = MemoryManager()

    def load_model(self, model_display_name: str = "Qwen 2.5 Chat (1.5B)"):
        self.llm = None 
        file_path = GGUF_MODELS.get(model_display_name)
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

        self.llm = Llama(
            model_path=file_path,
            n_ctx=2048,
            n_gpu_layers=1,
            verbose=False
        )

    def generate_response(self, user_prompt: str, enable_web_search: bool = True) -> str:
        if not self.llm:
            return "Error: Model not loaded."

        system_instruction = "You are a helpful AI assistant."

        # 1. Inject Persistent Memories
        memories = self.memory_mgr.get_all_memories()
        if memories:
            memory_block = "\n".join([f"- {m}" for m in memories])
            system_instruction += f"\n\nKey facts you remember about the user:\n{memory_block}"

        # 2. Inject Web Search Context
        if enable_web_search:
            search_context = search_web(user_prompt)
            if search_context:
                system_instruction += f"\n\nReal-time web search results:\n{search_context}"

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]

        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=256,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()