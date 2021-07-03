import json, requests, datetime, time, random
import gspread
import foo


from datetime import datetime
from gspread.exceptions import CellNotFound

gc = gspread.service_account(filename="./service_account.json")
sh = gc.open_by_url(foo.URL)
worksheet = sh.get_worksheet(0)


class WABot():
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['messages']
        self.APIUrl = foo.APIUrl
        self.token = foo.token
        self.switch = True

    def send_requests(self, method, data):
        url = f"{self.APIUrl}{method}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self, chatId, text):
        data = {"chatId" : chatId,
                "body" : text}
        answer = self.send_requests('sendMessage', data)
        return answer

    def file(self, chatId, format, fileName, url, caption=''):
        availableFiles = ['doc', 'gif', 'jpg', 'png', 'pdf', 'mp4', 'mp3', 'mkv']
        if format in availableFiles:
            data = {
                'chatId' : chatId,
                'body': url,
                'filename' : fileName,
                'caption' : caption
            }
            return self.send_requests('sendFile', data)
        return self.send_requests("sendMessage", {})

    def start(self,chatId):
        worksheet.update("D1", "1")
        numbers = worksheet.col_values(1)
        interval = [t for t in range(1, 61)]
        i = 0
        for number in numbers:
            i += 1
            try:
                val = worksheet.acell(f"C{i}").value
                if val is None:
                    phone = int(number)
                    chatId = f"{number}@c.us"
                    f = worksheet.acell("D1").value
                    if f == "1":
                        resp = self.send_message(chatId=chatId, text="Hello")
                        worksheet.update(f"C{i}", "Sent")
                        time.sleep(random.choice(interval))
                    else:
                        break
            except:
                continue
        return {"status": "success"}

    def stop(self, chatId):
        worksheet.update("D1", "0")
        return {"status": "success"}

    def processing(self):
        if self.dict_messages != []:
            print(self.dict_messages)
            for message in self.dict_messages:
                text = message['body'].split()
                if not message['fromMe']:
                    id  = message['chatId']
                    if id == foo.CHAT_ID:
                        url = f"{self.APIUrl}messagesHistory?page=0&count=10&chatId={id}&token={self.token}"
                        foo = requests.get(url).json()["messages"]
                        prevMessage = foo[1]["body"]
                        if text[0] == "1":
                            return self.start(id)
                        elif text[0] == "0":
                            return self.stop(id)
        return 'NoCommand'
