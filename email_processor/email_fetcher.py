import imaplib
from email.header import decode_header
from email import policy
from email.parser import BytesParser

def fetch_emails(email_user, email_password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(email_user, email_password)
    except imaplib.IMAP4.error as e:
        print(f"Login failed: {e}")
        return []
    
    status, messages = mail.select('inbox', readonly=True)
    if status != 'OK':
        print(f"Error selecting mailbox: {status}")
        return []
    
    status, messages = mail.search(None, '(UNSEEN)')
    if status != 'OK':
        print(f"Error searching emails: {status}")
        mail.logout()
        return []
    
    email_ids = messages[0].split()
    emails_data = []
    
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = BytesParser(policy=policy.default).parsebytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                from_ = msg.get("From")
                body = get_email_body(msg)
                emails_data.append({
                    "subject": subject,
                    "from": from_,
                    "body": body
                })
                move_email(mail, email_id, "Reported Emails")
    
    return emails_data

def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    return decode_payload(part.get_payload(decode=True))
                elif content_type == "text/html":
                    return decode_payload(part.get_payload(decode=True))
    else:
        return decode_payload(msg.get_payload(decode=True))

    return None

def decode_payload(payload):
    import chardet
    result = chardet.detect(payload)
    encoding = result['encoding']
    return payload.decode(encoding)

def move_email(mail, email_id, destination_folder):
    if not create_folder_if_not_exists(mail, destination_folder):
        print(f"Failed to ensure the folder '{destination_folder}' exists. Skipping email {email_id}.")
        return
    quoted_folder = f'"{destination_folder}"'
    print(f"Moving email ID {email_id} to folder {quoted_folder}")
    result = mail.copy(email_id, quoted_folder)
    if result[0] == 'OK':
        mail.store(email_id, '+FLAGS', '\\Deleted')
        mail.expunge()
    else:
        print(f"Error moving email ID {email_id} to folder {quoted_folder}: {result}")

def create_folder_if_not_exists(mail, folder_name):
    status, mailboxes = mail.list()
    if status != 'OK':
        print(f"Error listing mailboxes: {status}")
        return False

    for mailbox in mailboxes:
        if folder_name in mailbox.decode():
            return True
    status, response = mail.create(folder_name)
    if status == 'OK':
        print(f"Folder '{folder_name}' created successfully.")
        return True
    else:
        print(f"Error creating folder '{folder_name}': {response}")
        return False