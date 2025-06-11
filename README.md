# 💬 Chat with Your Data — Powered by OpenAI + Streamlit

Interact with your data using natural language!

This Streamlit app lets you upload a CSV file and have a conversation with a powerful OpenAI large language model (LLM). The assistant can explore, summarize, analyze, and visualize your data using built-in tools like the code interpreter and web search.

---

## ✨ Features

- 📁 Upload CSV data as context for the assistant
- 🧠 Ask questions, explore trends, and run analysis with LLM guidance
- 🧮 Uses OpenAI’s code interpreter for live computation and visualization
- 🌐 Optional web search tool included
- 🖼️ Automatically displays assistant-generated charts and images
- 💬 Full chat history with Markdown + code support

---

## 🔧 Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit openai pandas python-dotenv pillow
```

### 3. Set your OpenAI API key

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your-openai-api-key
```

---

## ▶️ Usage

Run the app with Streamlit:

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📂 Project Structure

```
├── streamlit_chat_app.py     # Main app script
├── instructions.py           # Custom prompt templates (optional)
├── requirements.txt          # List of Python dependencies
├── .env                      # Environment config with your API key
```

---

## 📸 Preview

> Upload your data and start chatting like this:

```
User: Can you summarize this dataset?
Assistant: Sure! Here's an overview: ...
```

If the assistant generates charts or images, they’ll appear directly in the chat.

---

## 🌍 Deploy

You can deploy this app publicly on:

* [Streamlit Community Cloud](https://streamlit.io/cloud)
* [Hugging Face Spaces](https://huggingface.co/spaces)
* [Render](https://render.com/), [Railway](https://railway.app/), or similar platforms

---

## 🔐 Security Notes

* Your OpenAI API key is stored locally in a `.env` file and never exposed to users.
* Uploaded files are stored temporarily in OpenAI's secure containers and only used during the session.

---

## 📜 License

MIT License — free to use, modify, and share.

---

## 🙌 Acknowledgements

Built with [Streamlit](https://streamlit.io/) and [OpenAI API](https://platform.openai.com/).

Inspired by the growing demand for easy, intelligent interfaces to explore data.

---

## 📫 Feedback

Got ideas or issues? [Open an issue](https://github.com/your-username/your-repo-name/issues) or start a discussion!
