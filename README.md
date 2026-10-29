<img width="211" height="278" alt="image" src="https://github.com/user-attachments/assets/28ddcedb-6ab6-45b1-adb0-ec9b379478f1" />

# ASAP-Bin 🗑️

**ASAP-Bin** is a lightweight, zero-tolerance email automation utility designed to safeguard your mental health and work-life balance. It automatically scans your inbox via IMAP and purges (archives or deletes) any incoming emails that contain aggressive corporate buzzwords like "URGENT", "ASAP", or "PRIORITY 1".

If everything is a priority, NOTHING IS. Let this script handle the noise.

## Features

- **Keyword Matching:** Scans email subjects and bodies for triggering buzzwords.
- **Custom Actions:** Choose whether to move matching emails to the Trash or Archive.
- **Dry-Run Mode:** Test the script safely without actually deleting anything.
- **Secure Connections:** Uses SSL/TLS and environment variables for credentials.

## Prerequisites

- Python 3.8 or higher.
- An email provider that supports IMAP (Gmail, Outlook, Yahoo, etc.).
- An **App Password** (do not use your primary password; most providers like Google require an App Password for third-party scripts).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com
   cd asap-bin
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your email details.

## Usage

Run the script manually or set it up as a Cron job:

```bash
python main.py
```

To run a safe test without deleting anything, make sure `DRY_RUN=True` is set in your `.env` file.
