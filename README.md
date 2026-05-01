# 🎵 Moodify.ai – AI-Powered Mood-Based Playlist Generator

Moodify.ai is an intelligent web application that generates personalized Spotify playlists based on your mood. It uses Natural Language Processing (NLP) and deep learning to analyze emotions from text or voice input and curates songs from your liked tracks accordingly.

---

## 🚀 Features

* 🎭 **Mood Detection using BERT** – Classifies user emotions from text input
* 🎤 **Voice Input Support** – Convert speech to text for mood analysis
* 🎶 **Spotify Integration** – Fetches liked songs and creates playlists
* 🧠 **Lyrics-Based Analysis** – Matches songs to mood using lyric sentiment
* ⚡ **Real-Time Playlist Creation** – Instantly generates playlists in your Spotify account
* 🔐 **Secure Authentication** – OAuth-based login with Spotify

---

## 🛠️ Tech Stack

* **Python**
* **Flask**
* **Transformers (HuggingFace BERT)**
* **Spotipy (Spotify API)**
* **LyricsGenius API**
* **JavaScript (Frontend)**
* **HTML & CSS**

---

## 📂 Project Structure

```
Moodify-ai/
│
├── app.py
├── requirements.txt
├── .gitignore
├── .env.example
│
└── templates/
    └── index.html
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Donalizasaji/Moodify.ai-AI-Powered-Mood-Based-Playlist-Generator.git
cd Moodify.ai-AI-Powered-Mood-Based-Playlist-Generator
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create a `.env` file and add:

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/callback
GENIUS_ACCESS_TOKEN=your_genius_access_token
FLASK_SECRET_KEY=your_secret_key
```

---

### 5️⃣ Run the Application

```bash
python app.py
```

Open in browser:
👉 http://127.0.0.1:5000

---

## 🧠 How It Works

1. User enters mood (text or voice)
2. BERT model classifies emotion
3. Spotify API fetches liked songs
4. Lyrics are retrieved using Genius API
5. Songs are matched to detected mood
6. A new playlist is created automatically

---

## 📊 Example Moods Supported

* Happy 😊
* Sad 😢
* Angry 😡
* Calm 😌
* Suprised 😐

---

## 🔐 Security Note

* `.env` file is excluded 
* API keys are not exposed in the repository

---

## 🌟 Future Improvements

* 🎧 Add recommendation for new songs (not only liked songs)
* 📊 Improve mood classification accuracy
* 🎨 Enhanced UI/UX
* 📱 Mobile-friendly design
* 🤖 Deploy using cloud platforms

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit a pull request.

---

## 📜 License

This project is licensed under the MIT License.

---

## 👩‍💻 Author

**Dona Liza Saji**
AI/ML Enthusiast | Data Analyst | Aspiring AI Engineer

---
