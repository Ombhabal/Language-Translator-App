# 🎤🌍 Translator App

A modern desktop **Translator App** built with Python and Tkinter.  
It supports **Text Translation, Voice Input (Speech-to-Text), and Text-to-Speech** — just like Google Translate!  


---

## ✨ Features
- 🌐 Translate text between 100+ languages using **Google Translate**
- 🎤 Voice input (speech recognition via microphone)
- 🔊 Listen to both source and translated text
- 🎨 Clean and simple Tkinter-based UI
- 🗑️ Automatic cleanup of temporary audio files
- ⚡ Fast and lightweight (runs offline except for translation API)

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Ombhabal/translator-app.git
cd translator-app
```

### 2. Create a Virtual Environment (Python 3.13 recommended)
```bash
python -m venv .venv
```
Activate it:
- **Windows (PowerShell):**
  ```bash
  .venv\Scripts\Activate
  ```
- **Linux/MacOS:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
---

## ▶️ Run the App
```bash
python google_translator.py
```
---
## 📂 Project Structure
```bash
translator-app/
│── google_translator.py   # Main app
│── requirements.txt       # Dependencies
│── README.md              # Project guide
│── .gitignore             # Ignore cache/venv files
│── screenshot.png         # UI preview
```
---
## 📸 Screenshot
Here’s how it looks:
![App Screenshot](screenshot.png)
---
## 🙌 Credits
- 📝 Translation: [deep-translator](https://pypi.org/project/deep-translator/)
- 🔊 Text-to-Speech: [gTTS](https://pypi.org/project/gTTS/)
- 🎶 Audio Playback: [pygame](https://www.pygame.org/)
- 🎤 Speech Recognition: [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
---
