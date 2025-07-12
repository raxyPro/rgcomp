from flask import Flask, render_template, request
import win32com.client
import pythoncom
import logging
import nltk
from rake_nltk import Rake

# ---------- Logging Setup ----------
logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# ---------- NLTK Resource ----------
try:
    nltk.data.find('corpora/stopwords')
    logging.info("NLTK stopwords found.")
except LookupError:
    logging.info("Downloading NLTK stopwords...")
    nltk.download('stopwords')

rake = Rake()

# ---------- Flask App Setup ----------
app = Flask(__name__)

@app.before_request
def before_request():
    pythoncom.CoInitialize()
    logging.debug("COM initialized for request.")

@app.teardown_request
def teardown_request(exception=None):
    pythoncom.CoUninitialize()
    logging.debug("COM uninitialized after request.")

def get_outlook():
    logging.debug("Getting Outlook MAPI namespace.")
    return win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

def list_folders(folder):
    folders = []
    logging.debug(f"Listing folders under: {folder.Name}")
    for i in range(1, folder.Folders.Count + 1):
        try:
            subfolder = folder.Folders.Item(i)
            folders.append({
                "name": subfolder.Name,
                "entry_id": subfolder.EntryID,
                "store_id": subfolder.StoreID
            })
            logging.debug(f"  Found folder: {subfolder.Name}")
        except Exception as e:
            logging.warning(f"  Failed to access subfolder index {i}: {e}")
    return folders

@app.route("/")
def index():
    try:
        outlook = get_outlook()
        accounts = []
        logging.info("Fetching Outlook accounts and top-level folders.")
        for i in range(outlook.Folders.Count):
            store = outlook.Folders.Item(i + 1)
            logging.debug(f"Account: {store.Name}")
            accounts.append({
                "name": store.Name,
                "entry_id": store.EntryID,
                "folders": list_folders(store)
            })
        return render_template("index.html", accounts=accounts)
    except Exception as e:
        logging.error(f"Error in index route: {e}", exc_info=True)
        return "Failed to load Outlook folders."

@app.route("/emails")
def get_emails():
    try:
        folder_entry_id = request.args.get("folder_id")
        store_id = request.args.get("store_id")
        offset = int(request.args.get("offset", 0))
        limit = 100

        logging.info(f"Fetching emails from folder: {folder_entry_id}, offset: {offset}")

        outlook = get_outlook()
        folder = outlook.GetFolderFromID(folder_entry_id, store_id)
        messages = folder.Items
        messages.Sort("[ReceivedTime]", True)

        total = messages.Count
        logging.info(f"Total messages in folder: {total}")
        emails = []

        i = offset + 1
        count = 0

        while count < limit and i <= total:
            try:
                msg = messages.Item(i)
                subject = msg.Subject or ""
                body = msg.Body[:300] if msg.Body else ""
                text = subject + " " + body

                #rake.extract_keywords_from_text(text)
                #tag_list = rake.get_ranked_phrases()[:3]
                tag_list=[]
                emails.append({
                    "entry_id": msg.EntryID,
                    "subject": subject,
                    "sender": msg.SenderName,
                    "datetime": msg.ReceivedTime.Format(),
                    "size": msg.Size,
                    "tags": tag_list
                })

                logging.debug(f"  Email #{i} - Subject: {subject}, Tags: {tag_list}")
                count += 1
            except Exception as e:
                logging.warning(f"  Error reading email at index {i}: {e}")
            i += 1

        logging.info(f"Returned {count} emails (offset {offset})")
        return {
            "emails": emails,
            "next_offset": offset + count,
            "has_more": (offset + count) < total
        }

    except Exception as e:
        logging.error(f"Failed to fetch emails: {e}", exc_info=True)
        return {"error": "Failed to fetch emails"}

@app.route("/email/<entry_id>")
def get_email(entry_id):
    try:
        logging.info(f"Fetching full email content for ID: {entry_id}")
        outlook = get_outlook()
        mail = outlook.GetItemFromID(entry_id)
        return {
            "subject": mail.Subject,
            "sender": mail.SenderName,
            "to": mail.To,
            "cc": mail.CC,
            "body": mail.Body
        }
    except Exception as e:
        logging.error(f"Failed to fetch full email: {e}", exc_info=True)
        return {"error": "Failed to fetch email"}

@app.route("/move_email", methods=["POST"])
def move_email():
    try:
        entry_id = request.form["email_id"]
        dest_folder_id = request.form["dest_folder_id"]
        store_id = request.form["store_id"]

        logging.info(f"Moving email ID: {entry_id} to folder: {dest_folder_id}")
        outlook = get_outlook()
        mail = outlook.GetItemFromID(entry_id)
        dest_folder = outlook.GetFolderFromID(dest_folder_id, store_id)
        mail.Move(dest_folder)

        logging.info("Email moved successfully.")
        return "Moved"
    except Exception as e:
        logging.error(f"Failed to move email: {e}", exc_info=True)
        return "Failed to move email"

if __name__ == "__main__":
    logging.info("Starting Flask app...")
    app.run(debug=True)
