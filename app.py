import base64
import hashlib
import hmac
import json
import os
import responder
import requests

import google_photo as gp
import pshnot
import t_oauth


app = responder.API()


def mkres():
    if request.method == "GET":
        return crc_test()
    elif request.method == "POST":
        return read_stream(request.json)


def crc(req):
    tkn = req.params.get('crc_token')
    sha256_hash_digest = hmac.new(os.environ["TW_API_SECRET"].encode(
    ), msg=tkn.encode().strip(), digestmod=hashlib.sha256).digest()
    res = {"response_token": "sha256=" +
           base64.b64encode(sha256_hash_digest).decode()}
    write_spreadsheet({"get": json.dumps(res)})
    print(res)
    return res


@app.route("/head")
def get_header(req, resp):
    print(req.headers)
    print(req.text)
    return "ok"


@app.route("/webhook/twitter")
async def w_twitter(req, resp):
    if req.method == "get":
        resp.media = crc(req)
        resp.status_code = 200
    elif req.method == "post":
        resp.status_code = 200
        resp.text = "ok"
        d = await req.media()
        read_stream(d)


@app.background.task
def read_stream(d):
    write_spreadsheet(d)

    # 古いほうの個人アカウントではなにもしない
    if int(d.get("for_user_id", 0)) < 10**9:
        return "ok"

    tweet = d.get("favorite_events", [{}])[0].get("favorited_status", {})
    media = tweet.get("extended_entities", {}).get("media", [])
    if media:
        n = 0
        print("start upload")
        tid = tweet.get("id_str", "")
        user = tweet.get("user", {})
        desc = "{0} /{1}\n{2}\n\nSource\nhttps://twitter.com/{3}/status/{4}".format(
            user.get("name", ""),
            user.get("screen_name", ""),
            tweet.get("text"),
            user.get("id", ""),
            tid)
        url1 = media[0]["media_url_https"]
        tmpurl = "{}:thumb".format(url1)

        for p in media:
            if len(media) > 1:
                n += 1
                name = "{0}-{1}".format(tid, n)
            else:
                name = tid
            uri = p.get("media_url_https", "")
            name += "."+uri.split(".")[-1]
            uri += ":orig"
            print(name)
            f = False
            lp = 0
            while lp < 5 or not f:
                f = gp.upload_img_by_uri(uri=uri, name=name, desc=desc)
                lp += 1
        if os.environ.get("TW_LIST_ID", False):
            list_len = t_oauth.add2list(user.get("id"))
        else:
            list_len = 0
        print("upload done")
        pshnot.send_not(
            title="UPLOADED/{}".format(list_len),
            text=desc,
            icon=tmpurl,
            source="https://twitter.com/{0}/{1}".format(
                user.get("id", "dareka"),
                tid
            )
        )
    else:
        print("no pics")
    return "ok"


def write_spreadsheet(jsn):
    url = os.environ["GAS_URI"]
    data = json.dumps(jsn, ensure_ascii=False)
    requests.post(url, data=data.encode("utf-8"))


if __name__ == "__main__":
    app.run()
