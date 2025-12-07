# WordCraft v2.0 🖋️ 

**WordCraft** is an intelligent, privacy-focused writing assistant powered by AI. It helps users proofread, rewrite, and optimize content for SEO, featuring a distinct "Dark Academia" aesthetic and a built-in plagiarism checker that scans the live web for free.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-Creative_Commons-amber)

## ✨ Features

* **AI Writing Tools:** Proofread, Rewrite (change tones), Fix Grammar, and Generate SEO keywords.
* **Deep Web Plagiarism Check:** Scans sentences against the live internet using DuckDuckGo (Free, no API key required).
* **Local History:** Automatically saves your generated drafts to a local database.
* **Custom Tones:** Switch between Professional, Casual, Academic, Creative, and Persuasive voices.
* **Privacy Focused:** No user data is sent to external servers other than the AI provider and search engine.

## 🛠️ Tech Stack

* **Backend:** Python (Flask)
* **Frontend:** HTML5, Tailwind CSS (via CDN)
* **AI Provider:** OpenRouter API 
* **Search Engine:** DuckDuckGo Search (`duckduckgo_search`)
* **Database:** SQLite (Local)

## 🚀 Setup & Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/AliAbbasHaidar313/WordCraft
    cd wordcraft
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Add your Openrouter API key in `config.txt`:
    ```text
    OPENROUTER_API_KEY=your_api_key_here
    FLASK_SECRET=your_random_secret_key
    OPENROUTER_MODEL=add_another_model_if_you_wish
    ```

4.  **Run the Application**
    ```bash
    python app.py
    ```
    Access the app at `http://127.0.0.1:5000`

## 🎨 Credits

* **Developer:** Ali Abbas Haidar
* **License:** Creative Commons Tool

---
*Developed with ❤️ for writers and developers.*
