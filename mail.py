from typing import TypedDict, List
from imapclient import IMAPClient  # https://imapclient.readthedocs.io/en/2.3.1/
import email
from datetime import datetime, timedelta
from pprint import pprint
import email.header


class ResponseMessage(TypedDict):
    uid: str
    sender: str
    date: str
    subject: str
    body: str
    flags: str
    seen: bool
    size: int


class MailClient:

    def logout(self) -> None:
        self._server.logout()

    def login(self, host: str, username: str, password: str) -> bool:
        try:
            self._server = IMAPClient(host, 993)
            self._server.login(username, password)
            return True
        except:
            print('unable to login with creds')
        return False

    def item(self, uid: int) -> ResponseMessage:
        msgs_data = self._server.fetch([uid], 'BODY[]').items()
        (uid, msg_data) = next(iter(msgs_data))  # first item
        msg = email.message_from_bytes(msg_data['BODY[]'])
        if msg.startswith(b'Text/plain'):
            plain_text_body = msg.decode('utf-8')
            print(plain_text_body)
        elif msg.startswith(b'Text/html'):
            html_body = msg.decode('utf-8')
            print(html_body)
        response = ResponseMessage(uid=uid, sender=msg.get("From"), date=msg.get(
            "Date"), subject=msg.get("Subject"), body='type')
        return response

    def inbox(self) -> List[ResponseMessage]:
        select_info = self._server.select_folder("INBOX", readonly=True)
        count = int(select_info[b"EXISTS"])
        fetch_datetime = (datetime.now() + timedelta(days=-1)
                          ).strftime('%d-%b-%Y')
        search = (f'SINCE {fetch_datetime}').encode('utf-8')
        messages = self._server.search(search)
        msgs = self._server.fetch(
            messages, ['ENVELOPE', 'FLAGS', 'RFC822.SIZE']).items()
        result = []
        for uid, data in msgs:
            envelope = data[b'ENVELOPE']
            flags = str(data[b'FLAGS'])
            size = int(data[b'RFC822.SIZE'])
            seen = 'Seen' in flags
            from_name = self.decode(envelope.from_[0].name.decode("utf-8"))
            result.append(ResponseMessage(
                uid=uid, subject=self.decode(envelope.subject.decode()), date=envelope.date, sender=from_name, seen=seen, size=size))
        result.reverse()
        return result

    def decode(self, value: str) -> str:
        text, encoding = email.header.decode_header(value)[0]
        return text
