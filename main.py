import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# Load configuration from environment variables
load_dotenv()

IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
MAILBOX = os.getenv("MAILBOX", "INBOX")
ACTION = os.getenv("ACTION", "TRASH").upper()
DRY_RUN = os.getenv("DRY_RUN", "True").lower() in ("true", "1", "yes")

# Parse keywords from environment
KEYWORDS_STR = os.getenv("TARGET_KEYWORDS", "URGENT,ASAP,PRIORITY 1")
KEYWORDS = [kw.strip().lower() for kw in KEYWORDS_STR.split(",") if kw.strip()]

def clean_text(header_printable):
    """Safely decode email headers into strings."""
    value, encoding = decode_header(header_printable)[0]
    if isinstance(value, bytes):
        try:
            return value.decode(encoding or "utf-8", errors="ignore")
        except Exception:
            return value.decode("utf-8", errors="ignore")
    return str(value)

def get_email_body(msg):
    """Extract plain text body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
    else:
        return msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    return ""

def process_inbox():
    if not all([IMAP_SERVER, EMAIL_ADDRESS, EMAIL_PASSWORD]):
        print("[ERROR] Missing required configuration variables in .env file.")
        return

    print(f"[INFO] Connecting to {IMAP_SERVER}...")
    try:
        # Establish secure connection
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select(MAILBOX)
        
        # Search for all unread messages (or use 'ALL' for every email in mailbox)
        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK":
            print("[ERROR] Failed to search mailbox.")
            return

        email_ids = messages[0].split()
        if not email_ids:
            print("[INFO] No new emails to process.")
            return

        print(f"[INFO] Found {len(email_ids)} unread email(s). Scanning for keywords...")

        for e_id in email_ids:
            # Fetch the email headers and body structure
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            if res != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = clean_text(msg["Subject"])
                    sender = clean_text(msg["From"])
                    body = get_email_body(msg)

                    # Check for triggers in subject or body text
                    combined_text = f"{subject} {body}".lower()
                    triggered_words = [kw for kw in KEYWORDS if kw in combined_text]

                    if triggered_words:
                        print(f"\n[MATCH] Triggered by words: {triggered_words}")
                        print(f"        From: {sender}")
                        print(f"        Subject: {subject}")

                        if DRY_RUN:
                            print("        [DRY RUN] Execution skipped. No changes made.")
                        else:
                            if ACTION == "TRASH":
                                # Move to Trash folder (standard IMAP approach)
                                mail.store(e_id, '+FLAGS', '\\Deleted')
                                print("        [ACTION] Marked for deletion successfully.")
                            elif ACTION == "ARCHIVE":
                                # Remove from current Inbox folder view
                                mail.store(e_id, '+FLAGS', '\\Secondary') # Custom flags vary by host
                                mail.copy(e_id, 'Archive') # Copies to standard Archive directory
                                mail.store(e_id, '+FLAGS', '\\Deleted')
                                print("        [ACTION] Moved to Archive successfully.")

        # Permanently expunge items marked as deleted from server if not running in dry-run
        if not DRY_RUN:
            mail.expunge()
            print("\n[INFO] Mailbox updated successfully.")

        mail.close()
        mail.logout()
        print("[INFO] Disconnected safely.")

    except Exception as e:
        print(f"[ERROR] An unexpected failure occurred: {e}")

if __name__ == "__main__":
    process_inbox()
