import os
import base64
import re
from datetime import datetime
from sqlalchemy.orm import Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models import Base, Attachment,Garbage
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class AttachmentHandler:
    def __init__(self):
        DATABASE_URL = os.getenv('DATABASE_URL')
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
        self.scopes = [
            "https://www.googleapis.com/auth/gmail.readonly", 
            "https://mail.google.com/"
        ]
        self.sender_name = os.getenv("SENDER_NAME")
        self.user_id = os.getenv("USER_ID")
        self.credentials_path = os.path.join(os.getcwd(), "utils", "credentials.json")
        self.token_path = os.path.join(os.getcwd(), "utils", "token.json")
        self.folder_prefix = os.path.join(os.getcwd(), 'media', 'sos_voice_record')
        self.staticfile_prefix = os.getenv("PREFIX_PATH")

    def authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes,redirect_uri='urn:ietf:wg:oauth:2.0:oob')
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f'Please go to this URL: {auth_url}')
                code = input('Enter the authorization code: ')
                flow.fetch_token(code=code)
                creds = flow.credentials
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())
        return creds

    def check_id(self, sos_ids: list[int]) -> dict:
        db = self.db
        isOk = True
        for sos_id in sos_ids:
            if db.query(Attachment).filter(Attachment.sos_id == sos_id).first():
                isOk = False
                break
        return {'ok': isOk}
            
    def download_attachments(self, sos_ids: list[int], call_timestamps: list[datetime]):
        try:
            db = self.db

            # Ensure sos_ids and call_timestamps are lists
            if not isinstance(sos_ids, list) or not isinstance(call_timestamps, list):
                return {'ok': False, 'error': 'sos_ids and call_timestamps must be lists.'}

            if len(sos_ids) != len(call_timestamps):
                return {'ok': False, 'error': 'Lengths of sos_ids and call_timestamps do not match.'}

            creds = self.authenticate()
            service = build("gmail", "v1", credentials=creds)
            query = f"from:{self.sender_name} has:attachment"
            results = service.users().messages().list(userId=self.user_id, q=query).execute()
            messages = results.get("messages")
            
            if messages is not None and isinstance(messages, list):
                payloads = []
                for idx, message in enumerate(messages):
                    message_id: str = message['id']
                    sos_id: int = sos_ids[idx]
                    call_timestamp = call_timestamps[idx]
                    if not db.query(Attachment).filter(Attachment.message_id == message_id).first() and not db.query(Attachment).filter(Attachment.sos_id == sos_id).first():
                        payload = self.process_message(service, message_id, sos_id, call_timestamp,"Attachment")
                        if payload:
                            payloads.append(payload)
                    elif db.query(Attachment).filter(Attachment.message_id == message_id).first() or not db.query(Attachment).filter(Attachment.sos_id == sos_id).first() or sos_id <= 0:
                        payload = self.process_message(service, message_id, sos_id, call_timestamp,"Garbage")
                        if payload:
                            payloads.append(payload)
                    else:
                        return {'ok': False, 'error': 'IDs exist'}

                return {'ok': True, 'data': payloads, 'error': ''}
            else:
                return {'ok': False, 'error': 'No messages found.'}
        except HttpError as error:
            print(f"An error occurred: {error}")
            return {'ok': False, 'error': f"An error occurred: {error}"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {'ok': False, 'error': f"An unexpected error occurred: {e}"}

    def process_message(self, service, message_id, sos_id, call_timestamp,table_name):
        try:
            db = self.db
            msg = service.users().messages().get(userId=self.user_id, id=message_id).execute()
            text = msg['snippet']
            pattern = r'Call at \d{4}-\d{2}-\d{2} \d{2}:\d{2} with number \d+\. Recorded by number \d+\.'
            if re.match(pattern, text):
                timestamp_str = text.split("Call at ")[1].split(" with number ")[0]
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')
                caller = int(text.split(" with number ")[1].split(".")[0])
                recorded = int(text.split("Recorded by number ")[1].split(".")[0])
                parts = [part for part in msg['payload'].get('parts', []) if part.get('filename')]

                if len(parts) == 1:
                    part = parts[0]
                    if part['filename']:
                        FILENAME: str = part['filename']
                        ATT_ID: str = part['body']['attachmentId']
                        ATT = service.users().messages().attachments().get(
                            userId=self.user_id, messageId=message_id, id=ATT_ID).execute()
                        ATT_DATA: base64 = ATT['data']
                        FILENAME_NEW: str = f"{message_id}{FILENAME.split('recording')[1]}" if "recording" in FILENAME else f"{message_id}{FILENAME}"
                        FILE_DATA = base64.urlsafe_b64decode(ATT_DATA.encode('UTF-8'))
                        CALLER_PATH = os.path.join(self.folder_prefix, str(caller))
                        os.makedirs(CALLER_PATH, exist_ok=True)
                        PATH = os.path.join(CALLER_PATH, FILENAME_NEW or FILENAME)
                        os.makedirs(os.path.dirname(PATH), exist_ok=True)

                        with open(PATH, 'wb') as f:
                            f.write(FILE_DATA)
                            print(f"Attachment '{FILENAME_NEW}' saved successfully.")

                        # Data to be used for creating the attachment
                        data = {
                            "message_id": message_id,
                            "filename": FILENAME_NEW,
                            "host_path": PATH,
                            "static_path": f"{self.staticfile_prefix}/{caller}/{FILENAME_NEW}",
                            "timestamp": timestamp,
                            "caller": caller,
                            "recorded": recorded,
                            "call_timestamp": call_timestamp
                        }
                        insertdb = None
                        # Conditionally add the sos_id if it is not zero
                        if table_name == "Attachment":
                            data["sos_id"] = sos_id
                            insertdb = Attachment(**data)
                        elif table_name == "Garbage":
                            insertdb = Garbage(**data)

                        # Create the Attachment object with the constructed data
                        if insertdb:
                            db.add(insertdb)
                            db.commit()

                        delete = service.users().messages().delete(
                            userId=self.user_id, id=message_id).execute()
                        delete_status = delete if delete else 'delete successfully'

                        payload = {
                            'ok': True,
                            'message_id': message_id,
                            'filename': FILENAME_NEW,
                            'path': PATH,
                            'timestamp': timestamp,
                            'caller': caller,
                            'recorded': recorded,
                            'sos_id': sos_id,
                            'call_timestamp': call_timestamp,
                            'delete_status': delete_status,
                            'staticfile_prefix': f"{self.staticfile_prefix}/{caller}/{FILENAME_NEW}"
                        }
                        return payload
                    else:
                        return {'ok': False, 'error': 'No attachments found for this message.'}
                else:
                    return {'ok': False, 'error': 'The attachment has more than 1 file.'}
            else:
                return {'ok': False, 'error': 'The format of the body message is incorrect.'}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def get_attachments(self):
        try:
            db = self.db
            creds = self.authenticate()
            service = build("gmail", "v1", credentials=creds)
            query = f"from:{self.sender_name} has:attachment"
            results = service.users().messages().list(userId="me", q=query).execute()
            messages = results.get("messages")

            if messages is not None and isinstance(messages, list):
                payloads = []
                for idx, message in enumerate(messages):
                    message_id = message['id']
                    if not db.query(Attachment).filter(Attachment.message_id == message_id).first():
                        payload = self.extract_message_data(service, message_id)
                        if payload:
                            payloads.append(payload)
                payloadssorted = sorted(payloads, key=lambda x: x['message_id'])
                sorted_data_with_order = [{**item, 'order': i + 1}
                                          for i, item in enumerate(payloadssorted)]
                return {'ok': True, 'data': sorted_data_with_order, 'error': ''}
            else:
                return {'ok': False, 'error': 'No messages found.'}
        except HttpError as error:
            print(f"An error occurred: {error}")
            return {'ok': False, 'error': f"An error occurred: {error}"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {'ok': False, 'error': f"An unexpected error occurred: {e}"}
        
    def extract_message_data(self, service, message_id):
        try:
            msg = service.users().messages().get(userId=self.user_id, id=message_id).execute()
            text = msg['snippet']
            pattern = r'Call at \d{4}-\d{2}-\d{2} \d{2}:\d{2} with number \d+\. Recorded by number \d+\.'
            if re.match(pattern, text):
                timestamp_str = text.split("Call at ")[1].split(" with number ")[0]
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')
                caller = text.split(" with number ")[1].split(".")[0]
                recorded = text.split("Recorded by number ")[1].split(".")[0]
                payload = {
                    'message_id': message_id,
                    'timestamp': timestamp,
                    'caller': caller,
                    'recorded': recorded,
                }
                return payload
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
            
    def delete_msg(self,message_id):
        creds = self.authenticate()
        service = build("gmail", "v1", credentials=creds)
        delete = service.users().messages().delete(
        userId=self.user_id, id=message_id).execute()
        delete_status = delete if delete else 'delete successfully'
        return delete_status
    
    def get_voice_logs(self):
        try:
            db = self.db
            payloads = db.query(Attachment).all()
            return {'ok': True, 'payloads': payloads}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {'ok': False, 'error': f"An unexpected error occurred: {e}"}

    def get_voice_log(self, sos_id=None):
        try:
            db = self.db
            payload = db.query(Attachment).filter(Attachment.sos_id == sos_id).first() if sos_id else None
            return {'ok': True, 'payload': payload}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {'ok': False, 'error': f"An unexpected error occurred: {e}"}
        
    def get_voice_logs_garbage(self):
        try:
            db = self.db
            payloads = db.query(Garbage).all()
            return {'ok': True, 'payloads': payloads}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {'ok': False, 'error': f"An unexpected error occurred: {e}"}
