# 📊 SheetReasoning Agent
### *Agentic AI-Powered Data Analysis Engine*

An intelligent, **Agentic Data Analyst** that allows users to upload Excel or CSV files and interact with their data through natural language. This system doesn't just "chat"—it autonomously reasons over your data to generate precise Python logic for instant insights.

This project initially began as part of an internship assignment but was redesigned, expanded, and completed independently based on my personal interest and curiosity in AI-powered data interaction. What started as a small task evolved into a full-fledged, functional **AI Agent system**—designed, refined, and tested with attention to both usability and technical intelligence.

### 🧠 The Philosophy: Human-AI Collaboration

Developed through an **AI-assisted development workflow**, this project represents a balanced collaboration between human creativity and AI precision. While the majority of the codebase was generated and iteratively refined with AI tools, the **core agentic logic, system architecture, and interface integration** were carried out manually by me. This approach reflects how AI can be used as a creative partner — not a replacement — in building meaningful technology.

---

## 🌟 Key Features

* 📁 **Autonomous Data Ingestion:** Seamlessly upload and analyze Excel/CSV files with automated schema detection.
* 💬 **Agentic Reasoning Engine:** Instead of fixed responses, the system uses a **Reasoning-Action loop** to generate dynamic Python code for data querying.
* 🧹 **Proactive Data Cleaning:** Automatically handles pre-processing (stripping titles like Mr./Ms. and numeric conversion) to ensure high-fidelity analysis.
* 🧠 **Context-Aware Memory:** Maintains conversational state to handle complex follow-up questions accurately.
* 🎨 **Modern UI/UX:** Features a minimal, responsive design with dual-theme (Light/Dark) support for user comfort.
* ⚡ **Lightweight & Efficient:** Optimized to run effectively on local systems with minimal resource overhead.

---

## 🛠️ Tech Stack

| **Component**         | **Technology**          |
| --------------------- | ----------------------- |
| **Backend Engine**    | Flask (Python)          |
| **Core Intelligence** | Cohere API              |
| **Agentic Logic**     | Pandas, PandasQL, NumPy |
| **Frontend**          | HTML, CSS, JavaScript   |
| **Environment**       | Python-dotenv           |
| **Data Handling**     | OpenPyXL, CSV           |

---

## 🚀 Project Overview

The **Agentic Excel Chatbot** was created with one core idea — **making data exploration natural and intelligent**.

Users can upload their files and the agent interprets complex intent, executing code autonomously to answer questions like:

* “Who are the top 5 earners in the Sales department?”
* “List all employees whose names start with 'M' and calculate their average tenure.”
* “Show me a summary of the salary distributions across regions.”

When questions are analytical, the system generates **deterministic Python code** to filter the data, ensuring that the results are based on facts rather than LLM "hallucinations."

---

## 🧩 Limitations & Notes

* This chatbot is designed for **lightweight, local AI-based data analysis**.
* Due to limited system configuration, it currently uses **smaller AI models** — which are excellent for structured tasks but may reach limits with extreme reasoning-heavy queries.
* **Security**: Currently intended for local, trusted datasets; uses a sandboxed environment for Python code execution.
* While I’m not currently planning to upgrade this specific version, it remains a proud example of building a **functional AI application with limited resources**.

---

## 🖼️ Demo Screenshots

| **File Upload Success**                             | **Query Response Example**                                |
| --------------------------------------------------- | --------------------------------------------------------- |
| ![File Upload](screenshots/file_upload_success.png) | ![Query Response](screenshots/query_response_example.png) |

---

## ⚙️ Installation & Usage

### 1️⃣ Clone the Repository

```bash
git clone [https://github.com/](https://github.com/)<your-username>/<repo-name>.git  
cd <repo-name>
```

### 2️⃣ Set Up Virtual Environment

```bash
python -m venv venv  
venv\Scripts\activate       # (Windows)  
source venv/bin/activate    # (Mac/Linux)
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up Environment Variables

Create a .env file and add your API key:

```plaintext
COHERE_API_KEY=your_api_key_here
```

### 5️⃣ Run the Application

```bash
python app.py
```

Open your browser and go to 👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 💡 Future Scope

Integrate larger LLMs (e.g., Llama 3 or Mistral) for advanced multi-step reasoning.

Add automated data visualizations (charts/graphs) generated by the agent.

Enable multi-file joining for cross-dataset analysis.

---

## 👩‍💻 Author

**Kiruthika T**
B.Tech – Artificial Intelligence & Data Science

📍 Tamil Nadu, India

🌐 LinkedIn: [Kiruthika T](https://www.linkedin.com/in/your-linkedin-username/)


---

## 💬 A Personal Note

This project reflects my personal journey in AI and Data Science, created through the combined power of human design thinking and AI-based development tools. Using AI assistance during the build process helped refine both technical efficiency and user experience.

It began as a simple curiosity-driven idea — to make data communication more human — and evolved into a functioning system that brings AI closer to everyday interaction.

Through this project, I learned how AI can amplify creativity rather than replace it. Every feature, from backend to UI, was shaped through experimentation, feedback, and iteration with AI tools.

This work stands as a reflection of my growth as an AI developer and innovator, and a milestone in my continuous journey to explore how human creativity and AI technology can coexist productively.
