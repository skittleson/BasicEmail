from typing import TypedDict, List
from imapclient import IMAPClient  # https://imapclient.readthedocs.io/en/2.3.1/
import email
from datetime import datetime, timedelta
import email.header
from pydantic import BaseModel

class ResponseMessage(TypedDict):
    uid: str
    sender: str
    date: str
    subject: str
    body: str
    flags: str
    seen: bool
    size: int

class LoginRequest(BaseModel):
    email: str
    password: str
    server: str
    port: int


class MailClient:

    def logout(self) -> None:
        self._server.logout()

    def login(self, login_request: LoginRequest) -> bool:
        try:
            self._server = IMAPClient(login_request.server, login_request.port)
            self._server.login(login_request.email, login_request.password)
            return True
        except:
            print('unable to login with creds')
        return False

    def get_render(self, uid: int) -> str:
        # https://coderslegacy.com/python/imap-read-emails-with-imaplib/#:~:text=The%20imap.fetch%20%28%29%20function%20takes%20an%20email%20ID,in%20byte%20form%2C%20to%20a%20proper%20message%20object.
        msgs_data = self._server.fetch([uid], 'RFC822').items()
        (uid, msg_data) = next(iter(msgs_data))
        msg = email.message_from_bytes(msg_data[b'RFC822'])
        body = ""
        if msg.is_multipart():
            # iterate over email parts
            for part in msg.walk():
                # extract content type of email
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                try:
                    body = part.get_payload(decode=True).decode()
                    print(f'{content_type} {content_disposition}')
                except:
                    pass

                # if content_type == "text/plain" and "attachment" not in content_disposition:
                #     print(body)
                # elif "attachment" in content_disposition:
                #     print('do nothing with attachment')
                    # download_attachment(part)
        else:
            # extract content type of email
            content_type = msg.get_content_type()
            # get the email body
            body = msg.get_payload(decode=True).decode()
            # if content_type == "text/plain":
            #     print(body)
        return body

    def get(self, uid: int) -> ResponseMessage:
        msgs_data = self._server.fetch([uid], 'RFC822').items()
        (uid, msg_data) = next(iter(msgs_data))  # first item
        msg = email.message_from_bytes(msg_data[b'RFC822'])
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))

                # skip any text/plain (txt) attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True)  # decode
                    break
        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            body = msg.get_payload(decode=True)
        response = ResponseMessage(uid=uid, sender=msg.get("From"), date=msg.get(
            "Date"), subject=self.decode(msg.get("Subject")), body=body)
        return response

    def fetch(self, folder: str, q: str) -> List[ResponseMessage]:
        if self._server is None:
            raise ValueError('not started')
        select_info = self._server.select_folder(folder, readonly=True)
        # count = int(select_info[b"EXISTS"])
        fetch_datetime = (datetime.now() + timedelta(days=-1)
                          ).strftime('%d-%b-%Y')
        search = (f'SINCE {fetch_datetime}').encode('utf-8')
        if q is not None:
            search = ['SUBJECT', q]
        messages = self._server.search(search)
        msgs = self._server.fetch(
            messages, ['ENVELOPE', 'FLAGS', 'RFC822.SIZE']).items()
        result = []
        for uid, data in msgs:
            envelope = data[b'ENVELOPE']
            flags = str(data[b'FLAGS'])
            size = int(data[b'RFC822.SIZE'])
            seen = 'Seen' in flags
            from_name = self.decode(envelope.from_[0].name)
            result.append(ResponseMessage(
                uid=uid, subject=self.decode(envelope.subject), date=envelope.date, sender=from_name, seen=seen, size=size))
        result.reverse()
        return result


    def decode(self, value: bytes) -> str:
        try:
            text, encoding = email.header.decode_header(value.decode('utf-8'))[0]
            if isinstance(text, str):
                return text
            if encoding is None:
                encoding = 'utf-8'
            return text.decode(encoding)
        except Exception as ex:
            print(f'Unable to decode {value}')
        return 'decoded_value'
