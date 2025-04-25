# 🔍 JobHarvest: AI-Powered Job Scraping & Resume Matching Framework

## 📌 Overview

**JobHarvest** is an intelligent, user-friendly application that scrapes job listings from major platforms and uses
GPT-powered AI to evaluate resume relevance, identify skill gaps, and generate tailored improvement suggestions. Built
with Python, Streamlit, LangChain, and GPT-4, it empowers job seekers with actionable insights during their job search.

---

## 🚀 Features

- 🔧 **Real-time job scraping** from LinkedIn and Indeed using Selenium
- 🧠 **AI-powered resume matching** using LangChain and GPT-4
- 📄 **Smart skill gap detection** and resume improvement suggestions
- 📊 Clean, interactive UI with downloadable results in CSV
- 🔍 Semantic search using FAISS and OpenAI embeddings

---

## 📦 Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python, Selenium
- **AI/NLP**: LangChain, GPT-4 (or GPT-4o via OpenAI API)
- **Vector Search**: FAISS
- **Embedding Model**: OpenAI Embeddings

---

## ⚙️ Installation

### 1️⃣. Clone the Repository

```bash
git clone https://github.com/yourusername/jobharvest.git
cd jobharvest
```

### **2️⃣. Set Up a Virtual Environment (Recommended)**

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

### **3️⃣. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4️⃣. Add Environment Variables**

Add OpenAI API Key in your system variables

```ini
OPENAI_API_KEY=your_openai_api_key
```

### **5️⃣. Add ChromeDriver**

Download the **ChromeDriver** that matches your installed version of Google Chrome and place it in the `resources/`
directory of the project.

- To find your Chrome version, go to `chrome://settings/help` in your Chrome browser.

**Place the driver here:**

- Windows: `resources/chromedriver.exe`
- macOS/Linux: `resources/chromedriver`

---

### **6️⃣. Create `config.ini` for APIFY API Key**

Inside the `resources/` directory, create a new file named `config.ini` with the following content:

```ini
[DEFAULT]
APIFY_API_KEY = your_apify_api_key
```

## ▶️ Running the Application

```bash
streamlit run main.py
```

