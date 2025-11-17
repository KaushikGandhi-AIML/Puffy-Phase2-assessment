# Puffy Phase 2 – AI Creative Automation Project

This project was built for the **AI Workflow Specialist – Phase 2 Assessment** for **Puffy**, a $100M DTC luxury mattress brand.  
It demonstrates how AI can be used to generate **novel creative angles**, **YouTube-ready scripts**, and a complete end-to-end creative workflow using Claude, Groq, Streamlit, and prompt engineering.

---

## 🚀 Project Overview

The **Puffy Creative Engine** is an AI-powered workflow designed to help Puffy’s marketing team break past the saturated mattress advertising landscape.

The system generates:

- **Completely original creative angles** (luxury-focused)
- **High-conversion 15–20s YouTube scripts**
- **Strong hooks in the first 2–3 seconds**
- **Multiple script variations**
- **Consistent, production-ready formatting**

This ensures **brand consistency**, **creative novelty**, and **YouTube optimization**, while avoiding all common mattress-industry clichés.

---

## 📂 Repository Structure

```
.
├── app.py
├── groq_client.py
├── prompt_templates.py
├── project_instructions.txt
│
├── knowledge/
│   ├── puffy_introduction.txt
│   ├── competitor_landscape.txt
│   ├── luxury_insights.txt
│   └── youtube_hook_playbook.txt
│
├── design/
│   └── Phase2_Design_Document.md
│
├── requirements.txt
└── README.md
```

---

## 🎯 What This Project Does

### ✔ 1. Generates Novel Creative Angles

The AI produces **8–12 luxury-grade ad concepts**, each with:

- A unique creative angle  
- A 0–3 second pattern-interrupt hook  
- A short concept description  
- Why it appeals to affluent buyers  
- How it differs from competitors  

---

### ✔ 2. Converts Concepts Into Professional 20-Second YouTube Scripts

Scripts include:

- **Timed scene breakdown**  
- **Voiceover (VO)**  
- **On-screen text**  
- **Cinematic visual direction**  
- **Sound design notes**  
- **Luxury-tone CTA**  

---

### ✔ 3. Provides Variations & Refinements

Users can request:

- Different tones (cinematic, emotional, witty)  
- Multiple script variations  
- Rewrites and refinements  

---

### ✔ 4. Maintains Puffy’s Luxury Brand Tone

Knowledge files ensure:

- Consistency with Puffy’s brand voice  
- Premium positioning  
- Avoidance of generic mattress tropes  
- Relevance to high-income US households  

---

## 🧠 Knowledge-Grounded AI

The system uses four knowledge files:

- **puffy_introduction.txt** – Brand background & tone  
- **competitor_landscape.txt** – Overused industry patterns to avoid  
- **luxury_insights.txt** – Psychology of affluent US buyers  
- **youtube_hook_playbook.txt** – Proven short-form hook strategies  

These ensure every output is **creative, original, and on-brand**.

---

## ⚙️ Tech Stack

- **Python**  
- **Streamlit**  
- **Groq API**  
- **Claude-style prompting**  
- **Knowledge-file grounding**  
- **Structured JSON outputs**

---

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export GROQ_API_KEY="your-api-key"
export GROQ_API_URL="https://api.groq.com/openai/v1/chat/completions"
export GROQ_DEFAULT_MODEL="llama-3.1-70b-versatile"
```

### 3. Run the App

```bash
streamlit run app.py
```

---

## 📄 Workflow Diagram

```
User Input
    ↓
Creative Angle Generator
    ↓
Angle Selection
    ↓
Script Generator
    ↓
Final 15–20 Second YouTube Ad Script
```

---