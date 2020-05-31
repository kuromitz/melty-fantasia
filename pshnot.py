import json
import os
import requests

appnum = os.environ['P7_NUM']
appkey = os.environ['P7_KEY']

base_url = "https://api.push7.jp/api/v1/"


def send_not(title, text, icon, source):
    url = base_url+appnum+"/send"
    payload = {
        "title": title,
        "body": text,
        "icon": icon,
        "url": source,
        "apikey": appkey
    }
    print(url)
    print(payload)
    return requests.post(url, data=json.dumps(payload))


if __name__ == "__main__":
    # push test
    ic = "https://i0.wp.com/www.herokucdn.com/images/ninja-avatar-96x96.png"
    print(send_not("hoge", "fugafugafuga",
                   source="https://push7.jp/_nuxt/img/ef960d1.svg", icon=ic).text)
