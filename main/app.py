import customtkinter as ctk
import threading
from ai.model_manager import AIModelEngine

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BoingAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BoingAI Desktop")
        self.geometry("700x550")

        self.ai_engine = AIModelEngine()

        # Layout Configuration
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title / Status
        self.status_label = ctk.CTkLabel(
            self, text="Status: Loading AI model...", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Chat Output Area
        self.chat_display = ctk.CTkTextbox(self, state="disabled", wrap="word", font=ctk.CTkFont(size=13))
        self.chat_display.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type your message...", height=40)
        self.entry.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", width=80, height=40, command=self.send_message)
        self.send_btn.grid(row=0, column=1, padx=(0, 10), pady=10)

        # Load model in background thread to prevent UI freezing
        threading.Thread(target=self._init_ai, daemon=True).start()

    def _init_ai(self):
        try:
            self.ai_engine.load_model()
            self.status_label.configure(text=f"Status: Ready ({self.ai_engine.device.upper()} acceleration)")
        except Exception as e:
            self.status_label.configure(text=f"Status: Failed to load model - {e}")

    def send_message(self):
        prompt = self.entry.get().strip()
        if not prompt:
            return

        self.entry.delete(0, "end")
        self.append_chat("You", prompt)

        # Run AI generation in background so window stays responsive
        threading.Thread(target=self._get_ai_response, args=(prompt,), daemon=True).start()

    def _get_ai_response(self, prompt):
        self.status_label.configure(text="Status: Thinking...")
        response = self.ai_engine.generate_response(prompt)
        self.append_chat("BoingAI", response)
        self.status_label.configure(text=f"Status: Ready ({self.ai_engine.device.upper()} acceleration)")

    def append_chat(self, sender: str, text: str):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}:\n{text}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")