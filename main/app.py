import customtkinter as ctk
import threading
import re
import webview
from ai.model_manager import AIModelEngine, GGUF_MODELS
from ai.memory_manager import MemoryManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class BoingAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BoingAI Studio")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.ai_engine = AIModelEngine()
        self.db = MemoryManager()
        self.current_session_id = None
        self.latest_html_code = ""

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="BoingAI", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.new_chat_btn = ctk.CTkButton(
            self.sidebar, text="+ New Chat", command=self.start_new_chat
        )
        self.new_chat_btn.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.mem_btn = ctk.CTkButton(
            self.sidebar, text="AI Memories", fg_color="transparent", border_width=1, command=self.open_memory_window
        )
        self.mem_btn.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.model_selector = ctk.CTkOptionMenu(
            self.sidebar, values=list(GGUF_MODELS.keys()), command=self.switch_model
        )
        self.model_selector.grid(row=3, column=0, padx=20, pady=(15, 5), sticky="ew")

        self.search_switch = ctk.CTkSwitch(self.sidebar, text="Web Search")
        self.search_switch.select()
        self.search_switch.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.history_list = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.history_list.grid(row=5, column=0, padx=10, pady=(10, 10), sticky="nsew")

        self.status_label = ctk.CTkLabel(
            self.sidebar, text="Status: Ready", font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.status_label.grid(row=6, column=0, padx=20, pady=15, sticky="ew")

        # ----------------------------------------------------
        # MAIN AREA (CHAT & CODE TABS)
        # ----------------------------------------------------
        self.main_tabs = ctk.CTkTabview(self)
        self.main_tabs.grid(row=0, column=1, sticky="nsew", padx=15, pady=10)

        self.tab_chat = self.main_tabs.add("Chat")
        self.tab_code = self.main_tabs.add("Generated Code")

        # --- Chat Tab ---
        self.tab_chat.grid_rowconfigure(0, weight=1)
        self.tab_chat.grid_columnconfigure(0, weight=1)

        self.chat_history = ctk.CTkScrollableFrame(self.tab_chat, fg_color="transparent")
        self.chat_history.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.chat_history.grid_columnconfigure(0, weight=1)

        self.input_frame = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Ask BoingAI to generate code or answer questions...", height=45, corner_radius=10
        )
        self.entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ctk.CTkButton(
            self.input_frame, text="Send", width=90, height=45, corner_radius=10, command=self.send_message
        )
        self.send_btn.grid(row=0, column=1)

        # --- Generated Code Tab ---
        self.tab_code.grid_rowconfigure(0, weight=1)
        self.tab_code.grid_columnconfigure(0, weight=1)

        self.code_display = ctk.CTkTextbox(self.tab_code, font=ctk.CTkFont(family="Courier", size=13), wrap="none")
        self.code_display.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.code_display.insert("1.0", "<!-- Generated HTML/JS code will appear here -->")

        self.launch_preview_btn = ctk.CTkButton(
            self.tab_code, text="Launch Live Window Preview", height=40, command=self.launch_native_preview
        )
        self.launch_preview_btn.grid(row=1, column=0, sticky="ew")

        self.refresh_saved_chats()
        self.start_new_chat()

        threading.Thread(target=self._init_ai, args=(self.model_selector.get(),), daemon=True).start()

    # ----------------------------------------------------
    # CHAT & PREVIEW LOGIC
    # ----------------------------------------------------
    def send_message(self):
        prompt = self.entry.get().strip()
        if not prompt or self.send_btn.cget("state") == "disabled":
            return

        self.entry.delete(0, "end")
        self._add_message_bubble("You", prompt, is_user=True)
        self.db.save_message(self.current_session_id, "You", prompt)

        use_web = bool(self.search_switch.get())
        threading.Thread(target=self._get_ai_response, args=(prompt, use_web), daemon=True).start()

    def _get_ai_response(self, prompt: str, use_web: bool):
        self.status_label.configure(text="Thinking...")
        self.send_btn.configure(state="disabled")

        response = self.ai_engine.generate_response(prompt, enable_web_search=use_web)

        self._add_message_bubble("BoingAI", response, is_user=False)
        self.db.save_message(self.current_session_id, "BoingAI", response)

        self._extract_code(response)

        self.status_label.configure(text="Status: Ready")
        self.send_btn.configure(state="normal")

    def _extract_code(self, text: str):
        """Extract code blocks from markdown backticks."""
        code_blocks = re.findall(r"```(?:html|xml|javascript|css)?\n(.*?)```", text, re.DOTALL)
        if code_blocks:
            self.latest_html_code = code_blocks[0]
            self.code_display.delete("1.0", "end")
            self.code_display.insert("1.0", self.latest_html_code)
            self.main_tabs.set("Generated Code")

    def launch_native_preview(self):
        """Launches a native macOS web view window to render the HTML/JS output."""
        if not self.latest_html_code:
            return
        
        def _run_webview():
            webview.create_window("BoingAI Live Preview", html=self.latest_html_code)
            webview.start()

        threading.Thread(target=_run_webview, daemon=True).start()

    def start_new_chat(self):
        self.current_session_id = self.db.create_session("New Chat")
        self.clear_chat_display()
        self.refresh_saved_chats()

    def refresh_saved_chats(self):
        for widget in self.history_list.winfo_children():
            widget.destroy()

        sessions = self.db.get_all_sessions()
        for s_id, title in sessions:
            btn = ctk.CTkButton(
                self.history_list,
                text=title,
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                command=lambda sid=s_id: self.load_chat_session(sid),
            )
            btn.pack(fill="x", pady=2)

    def load_chat_session(self, session_id: int):
        self.current_session_id = session_id
        self.clear_chat_display()
        messages = self.db.get_session_messages(session_id)
        for sender, content in messages:
            self._add_message_bubble(sender, content, is_user=(sender == "You"))

    def clear_chat_display(self):
        for widget in self.chat_history.winfo_children():
            widget.destroy()

    def _add_message_bubble(self, sender: str, text: str, is_user: bool):
        bubble_row = ctk.CTkFrame(self.chat_history, fg_color="transparent")
        bubble_row.grid(sticky="ew", pady=6, padx=5)
        bubble_row.grid_columnconfigure(0, weight=1)

        bg_color = "#2b5c8f" if is_user else "#2b2b2b"
        align_side = "e" if is_user else "w"

        bubble = ctk.CTkFrame(bubble_row, fg_color=bg_color, corner_radius=12)
        bubble.grid(row=0, column=0, sticky=align_side, padx=5)

        header = ctk.CTkLabel(
            bubble, text=sender, font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#a0c4ff" if is_user else "#b0b0b0"
        )
        header.pack(anchor="w", padx=12, pady=(8, 2))

        msg_label = ctk.CTkLabel(
            bubble, text=text, font=ctk.CTkFont(size=13), wraplength=550, justify="left"
        )
        msg_label.pack(anchor="w", padx=12, pady=(0, 8))

        self.chat_history._parent_canvas.yview_moveto(1.0)

    def open_memory_window(self):
        mem_win = ctk.CTkToplevel(self)
        mem_win.title("AI Long-Term Memories")
        mem_win.geometry("450x400")
        mem_win.attributes("-topmost", True)

        ctk.CTkLabel(mem_win, text="Add New Memory:", font=ctk.CTkFont(weight="bold")).pack(padx=15, pady=(15, 5), anchor="w")

        mem_entry = ctk.CTkEntry(mem_win, placeholder_text="e.g., 'My name is Seth'")
        mem_entry.pack(padx=15, pady=5, fill="x")

        mem_list = ctk.CTkScrollableFrame(mem_win)
        mem_list.pack(padx=15, pady=10, fill="both", expand=True)

        def refresh_memories():
            for w in mem_list.winfo_children():
                w.destroy()
            for fact in self.db.get_all_memories():
                row = ctk.CTkFrame(mem_list, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=fact, anchor="w", wraplength=300).pack(side="left", padx=5)
                ctk.CTkButton(
                    row, text="X", width=25, fg_color="red",
                    command=lambda f=fact: [self.db.delete_memory(f), refresh_memories()]
                ).pack(side="right")

        def save_mem():
            val = mem_entry.get().strip()
            if val:
                self.db.add_memory(val)
                mem_entry.delete(0, "end")
                refresh_memories()

        ctk.CTkButton(mem_win, text="Add Memory", command=save_mem).pack(padx=15, pady=(0, 10), fill="x")
        refresh_memories()

    def _init_ai(self, model_name: str):
        self.status_label.configure(text=f"Loading {model_name}...")
        try:
            self.ai_engine.load_model(model_name)
            self.status_label.configure(text="Status: Ready")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")

    def switch_model(self, choice: str):
        threading.Thread(target=self._init_ai, args=(choice,), daemon=True).start()