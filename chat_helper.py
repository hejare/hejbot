from slack_bolt import App

excluded_users = [
    "USLACKBOT",  # slackbot
    "U3XHXNE9X",  # ludde
    "U3Y6GK2UT",  # henrik
    "U7TTAP649",  # bernhard
    "UH8HFCQ6M",  # damien
    "U03JRG1L2BD",  # sara
]


def is_valid_user(user):
    return (
        not user["is_bot"] and not user["deleted"] and user["id"] not in excluded_users
    )


def all_users(app: App, include_users=None):
    users = filter(is_valid_user, app.client.users_list()["members"])
    if include_users != None:
        return [u for u in users if u["name"] in include_users]
    return users


def get_private_chat(app: App, user):
    conv = app.client.conversations_open(users=user["id"])
    return conv["channel"]["id"]
