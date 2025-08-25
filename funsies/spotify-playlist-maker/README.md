# 🎵 Spotify Playlist Maker

This project automatically creates a Spotify playlist from a CSV file with two columns (name, band).
You provide a list of songs and artists, and the script adds everything to a playlist in your Spotify account.

---

## 🚀 Prerequisites

- Spotify account (free or premium).
- Python 3.9+ installed.
- Spotify Developer app configured.

---

## ⚙️ Creating your app on Spotify

1. Access the Spotify Developer Dashboard (https://developer.spotify.com/dashboard/).
2. Click "Create App."
3. Set a name and description (e.g., Spotify Playlist Maker).
4. In **Redirect URI**, add:
```
http://127.0.0.1:8000/callback
```
⚠️ Since **April 9, 2025**, new applications must use exactly this format (`127.0.0.1`, port `8000`).
5. Save your changes.
6. Make a note of the **Client ID** and **Client Secret**. You will enter these values ​​in the Python script.
7. When you log in for the first time, Spotify will ask for 2FA authentication:
- You will receive an **email with a 6-digit code**.
- Simply enter this code to complete the login.

---

## 📥 Installation

Clone the repository and navigate to the project folder. Next, create and activate a Python virtual environment:

bash
python3 -m venv spotify
source spotify/bin/activate

Install the dependencies:

bash
pip3 install -r requirements.txt

---

## 📝 CSV Structure

The CSV file must have exactly two columns: 'name' (song) and 'band' (artist).

Example (`example-list.csv`):

```csv
name,band
Smells Like Teen Spirit,Nirvana
One,Metallica
Billie Jean,Michael Jackson
```

---

## ▶️ Usage

Run the script, passing the playlist name and the path to the CSV:

```bash
python3 spotify-playlist-maker.py --playlist "Test Playlist" --file "example-list.csv"
```

- The script will open the browser for Spotify login.
- After authorizing the application, it will create a private playlist with the name you provided.
- All songs found in the CSV will be added.

---

## ✅ Expected result

```
🎵 Creating playlist: Playlist Test
✔ Added: Smells Like Teen Spirit - Nirvana
✔ Added: One - Metallica
✔ Added: Billie Jean - Michael Jackson

✅ Playlist 'Playlist Test' created with 3 songs!
```

---

## 📄 License

This project is distributed under the MIT license.