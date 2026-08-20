# BoingAI Studio 🚀

A lightweight, local AI desktop application built with Python and CustomTkinter. BoingAI lets you run GGUF models (Qwen, Llama, Gemma) locally on your MacOS or Windows device with real-time web search, persistent AI memories, saved chat histories, and live code previewing.

![BoingAI Screenshot](/Users/sethmiller/BoingAI/other/assets/screenshot.png) <!-- Optional: Add a screenshot of your app -->

## ✨ Key Features

- **Local Inference**: Run open-source LLMs locally using `llama-cpp-python` (optimized for Apple Silicon Metal GPU).
- **Multiple Model Support**: Switch seamlessly between Qwen 2.5, Llama 3.2, and Gemma 2.
- **🌐 Web Search Integration**: Real-time DuckDuckGo web search augmentation for live information.
- **🧠 AI Memory**: Persistent long-term memory engine backed by SQLite.
- **💬 Saved Chats**: Automatically saves conversation threads locally.
- **💻 Live Code Preview**: Syntax-formatted code view with live macOS window previewing for HTML/JS/CSS output.

---

## 🛠️ Tech Stack

- **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Model Engine**: [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- **Database**: SQLite3
- **Search**: `duckduckgo-search`
- **Native Preview**: `pywebview`

---

## 🚀 Getting Started

### Prerequisites

- macOS (Apple Silicon recommended for Metal acceleration)
- Python 3.10+
- `git`

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/your-username/BoingAI.git](https://github.com/your-username/BoingAI.git)
   cd BoingAI
or... just download the app from the latest release
