# utils.py
import requests
import json
import re
import time
from difflib import SequenceMatcher
from duckduckgo_search import DDGS  

# -----------------------------
# AI Prompt Builder
# -----------------------------
def build_prompt_for_action(action, text, tone="Professional"):
    base = (
        "You are an expert AI writing assistant. "
        "Return ONLY the processed output. No conversational filler. "
        "Use Markdown formatting."
    )
    if action == "proofread":
        return base + f"\n\nCorrect grammar, spelling, and punctuation. Tone: {tone}.\n\n{text}"
    if action == "rewrite":
        return base + f"\n\nRewrite this text to be {tone}. Improve clarity.\n\n{text}"
    if action == "seo":
        return base + f"\n\nGenerate SEO titles, keywords, and meta description.\n\n{text}"
    return base + f"\n\n{text}"

# -----------------------------
# OpenRouter API (AI Generation)
# -----------------------------
def call_openrouter(prompt, api_key, model):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1500
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=40)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"AI Error: {str(e)}"

# -----------------------------
# Local Repetition Check (Internal only)
# -----------------------------
def sentence_split(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def check_local_repetition(text):
    sentences = sentence_split(text)
    n = len(sentences)
    if n < 2: return {"score": 0, "matches": []}
    
    flagged = []
    max_sim = 0.0
    for i in range(n):
        for j in range(i+1, n):
            sim = SequenceMatcher(None, sentences[i], sentences[j]).ratio()
            max_sim = max(max_sim, sim)
            if sim > 0.8:
                flagged.append({"s1": sentences[i], "s2": sentences[j], "similarity": int(sim*100)})
    return {"score": int(max_sim*100), "matches": flagged}

# -----------------------------
# EXTERNAL API PLAGIARISM CHECK
# -----------------------------
def check_web_plagiarism(text):
    """
    Scans the live internet using DuckDuckGo External API.
    """
    sentences = sentence_split(text)
    
    # Filter: Only check sentences long enough to be unique (approx 6+ words)
    # Short phrases like "Thank you" appear everywhere and cause false positives.
    sentences_to_check = [s for s in sentences if len(s.split()) > 5]
    
    if not sentences_to_check:
        return {"error": "Text is too short or generic to check."}

    # SAFETY LIMIT: External APIs have rate limits.
    # We check up to 8 sentences to ensure speed and prevent blocking.
    # If text is long, we take a distributed sample.
    limit = 8
    if len(sentences_to_check) > limit:
        step = len(sentences_to_check) // limit
        target_sentences = sentences_to_check[::step][:limit]
    else:
        target_sentences = sentences_to_check

    matches = []
    
    try:
        with DDGS() as ddgs:
            for sent in target_sentences:
                # We search for the EXACT sentence in quotes
                query = f'"{sent}"'
                
                # Call External API
                results = list(ddgs.text(query, max_results=1))
                
                if results:
                    matches.append({
                        "sentence": sent,
                        "found_at": results[0]['href'],
                        "title": results[0]['title']
                    })
                
                # 0.5s delay to be polite to the API
                time.sleep(0.5)
                
    except Exception as e:
        return {"error": f"External API Error: {str(e)}"}

    # Calculate EXACT Percentage
    # Formula: (Matches Found / Total Checked) * 100
    total_checked = len(target_sentences)
    if total_checked == 0:
        score = 0
    else:
        score = int((len(matches) / total_checked) * 100)

    return {
        "web_score": score,
        "matches": matches,
        "checked_count": total_checked
    }
