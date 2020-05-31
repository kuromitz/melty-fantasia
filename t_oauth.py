import json
import os
from requests_oauthlib import OAuth1Session

CK = os.environ["TW_API_KEY"]
CS = os.environ["TW_API_SECRET"]
AT = os.environ["TW_ACCESS_TOKEN"]
ATS = os.environ["TW_ACCESS_SECRET"]
twitter = OAuth1Session(CK, CS, AT, ATS)


def get_tl(num=1):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {"count": num}

    res = twitter.get(url, params=params)

    return res.text


def add2list(uid):
    url = "https://api.twitter.com/1.1/lists/members/create.json"

    params = {
        "list_id": os.environ["TW_LIST_ID"],
        "user_id": uid}

    res = twitter.post(url, params=params)
    return json.loads(res.text).get("member_count", 0)


if __name__ == "__main__":
    # test
    print(add2list("149065051"))
