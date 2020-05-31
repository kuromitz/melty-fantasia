import datetime
import json
import os
import requests
import time


def get_token():
    with open("token", "r") as t:
        tkn = [i.strip() for i in t]
    data = {
        "refresh_token": os.environ["GP_REFRESH_TOKEN"],
        "client_id": os.environ["GP_CLIENT_ID"],
        "client_secret": os.environ["GP_CLIENT_SECRET"],
        "grant_type": "refresh_token"
    }

    url = os.environ["GP_TOKEN_URI"]

    now = time.time()
    if float(tkn[1]) < now:
        res = requests.post(url, data=data)
        r = json.loads(res.content.decode())
        exp = now+r["expires_in"]-60
        n_tkn = r["access_token"]
        with open("token", "w") as t:
            t.write(n_tkn+"\n")
            t.write(str(exp))

        return n_tkn
    else:
        return tkn[0]


def upload_img_by_uri(uri, name="", desc=""):
    try:
        im = requests.get(uri).content
        token = get_token()
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-type": "application/octet-stream",
            "X-Goog-Upload-Protocol": "raw",
            "X-Goog-Upload-File-Name": name,

        }

        response = requests.post(
            "https://photoslibrary.googleapis.com/v1/uploads", headers=headers, data=im)
        u_token = response.content.decode()
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Content-type": "application/json",
        }

        data = {
            "newMediaItems": [
                {
                    "description": desc,
                    "simpleMediaItem": {
                        "uploadToken": u_token
                    }
                }
            ]

        }
        if os.environ.get("ALBUM_ID", False):
            data["albumId"] = os.environ.get("ALBUM_ID", False)
        response = requests.post(
            "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate", headers=headers, data=json.dumps(data))
        return True
    except:
        return False


if __name__ == "__main__":
    # upload test
    print(upload_img_by_uri("https://pbs.twimg.com/media/D6X_tI_UcAAB1ZM.jpg:orig"))
