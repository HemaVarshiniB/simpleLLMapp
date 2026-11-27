
import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]


def get_gmail_service():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json", SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            credentials_file = os.getenv("GMAIL_CREDENTIALS_FILE")
            if not credentials_file:
                candidates = [
                    filename
                    for filename in os.listdir(".")
                    if filename.startswith("client_secret_")
                    and filename.endswith(".json")
                ]
                if len(candidates) == 1:
                    credentials_file = candidates[0]
                elif len(candidates) > 1:
                    raise RuntimeError(
                        "Multiple Google OAuth client files found. "
                        "Set GMAIL_CREDENTIALS_FILE to the desired file."
                    )
                else:
                    credentials_file = "credentials.json"

            if not os.path.isfile(credentials_file):
                raise FileNotFoundError(
                    "Google OAuth client file not found. Set "
                    "GMAIL_CREDENTIALS_FILE or add credentials.json."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


def search_emails(service, query, max_results=5):

    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    email_results = []

    for message in messages:

        email = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = email["payload"].get("headers", [])

        email_data = {
            "id": email["id"],
            "message_id": email["id"],
            "snippet": email.get("snippet", ""),
        }

        for header in headers:
            email_data[header["name"].lower()] = header["value"]

        email_results.append(email_data)

    return email_results


def extract_email_body(payload):

    body = ""

    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":

        data = payload.get("body", {}).get("data")

        if data:
            body = base64.urlsafe_b64decode(
                data
            ).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):

        body += extract_email_body(part)

    return body


def read_email(service, message_id):
    if not isinstance(message_id, str):
        raise ValueError(
            "message_id must be the Gmail API message ID returned by "
            "search_emails."
        )

    message_id = message_id.strip()
    if (
        not message_id
        or message_id.startswith("<")
        or message_id.endswith(">")
        or "@" in message_id
    ):
        raise ValueError(
            "Invalid Gmail message ID. Use the message_id returned by "
            "search_emails, not an email's RFC Message-ID header."
        )

    email = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()

    headers = email["payload"].get("headers", [])

    email_data = {
        "id": email["id"],
        "snippet": email.get("snippet", "")
    }

    for header in headers:
        email_data[header["name"].lower()] = header["value"]

    email_data["body"] = extract_email_body(
        email["payload"]
    )[:8000]

    return email_data


def send_email(service, to, subject, body):

    message = MIMEText(body)

    message["to"] = to
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    request_body = {
        "raw": encoded_message
    }

    result = service.users().messages().send(
        userId="me",
        body=request_body
    ).execute()

    return {
        "status": "success",
        "message_id": result["id"],
        "recipient": to
    }


