from datetime import datetime
from enum import Enum
from multiprocessing import Process
import time
import schedule
from logging import Logger

from slack_bolt import App

from chat_helper import all_users, get_private_chat
from db import query


class PostTypes(Enum):
    MondayMorning = "MondayMorning"


def get_post_type_display_text(post_type):
    if post_type == PostTypes.MondayMorning:
        return "Måndag morgon"
    return "Okänd"


def get_scheduled_posts_by_type(post_type: PostTypes):
    return query(
        "SELECT post_id,type,text,added_by FROM scheduled_posts WHERE type=%s",
        (post_type.value,),
    )


def consume_scheduled_post(post_id):
    return query("DELETE FROM scheduled_posts WHERE post_id=%s", (post_id,))


class Scheduler:
    logger: Logger
    app: App

    def event_monday_morning(self):
        self._send_scheduled_post(PostTypes.MondayMorning)

    def start(self):
        schedule.every().monday.at("09:00", "Europe/Stockholm").do(
            self.event_monday_morning
        )

        p = Process(target=self.run)
        p.start()

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(10)

    def _send_scheduled_post(self, post_type: PostTypes):
        posts = get_scheduled_posts_by_type(post_type)

        for scheduled_post in posts:
            for user in all_users(self.app):
                self.app.client.chat_postMessage(
                    channel=get_private_chat(self.app, user),
                    text=scheduled_post["text"],
                )

            consume_scheduled_post(scheduled_post["post_id"])

    def __init__(self, logger: Logger, app: App):
        self.logger = logger
        self.app = app
