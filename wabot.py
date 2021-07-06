import json, requests, time, random
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
        availableFiles = ['doc', 'gif', 'jpg', 'png', 'pdf', 'mp4', 'mp3', 'mkv', 'jpeg']
        if format in availableFiles:
            data = {
                'chatId' : chatId,
                'body': url,
                'filename' : fileName,
                'caption' : caption
            }
            return self.send_requests('sendFile', data)
        return self.send_requests("sendMessage", {})

    def start(self, imageURL, filename, _format, caption):
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
                        # resp = self.send_message(chatId=chatId, text=text)
                        resp = self.file(chatId=chatId, url=imageURL, format=_format, fileName=filename, caption=caption)
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
                _id = message['chatId']
                if message['fromMe'] and _id == foo.CHAT_ID:
                    messageType = message['type']
                    if messageType == "image":
                        imageURL = message['body']
                        caption = message['caption']
                        file = imageURL.split("/")[-1]
                        filename = file.split(".")[0]
                        _format = file.split(".")[1]
                        if caption is None:
                            caption = ""
                        return self.start(imageURL=imageURL, filename=filename, _format=_format, caption=caption)
                # text = message['body']
                # if not message['fromMe']:
                #     id  = message['chatId']
                #     if id == foo.CHAT_ID:
                #         return self.start(text)
        return 'NoCommand'
