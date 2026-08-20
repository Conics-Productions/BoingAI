import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class AIModelEngine:
    def __init__(self, model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_id = model_id
        self.device = self._detect_device()
        self.tokenizer = None
        self.model = None

    def _detect_device(self) -> str:
        """Detect GPU acceleration for macOS (Apple Silicon Metal) or Windows (CUDA)."""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"  # Metal Performance Shaders for macOS
        return "cpu"

    def load_model(self):
        """Downloads/caches and loads the Hugging Face model into memory."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            device_map=self.device
        )

    def generate_response(self, user_prompt: str) -> str:
        if not self.model or not self.tokenizer:
            return "Error: Model is not loaded yet."

        messages = [{"role": "user", "content": user_prompt}]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                do_sample=True
            )

        # Decode response without echo
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True)