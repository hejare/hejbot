import time
from enum import Enum
from logging import Logger
from multiprocessing import Process
from typing import Dict, Optional, Sequence, Union

import schedule
from slack_bolt import App
from slack_sdk.models.attachments import Attachment
from slack_sdk.models.blocks import Block

from chat_helper import all_users, get_private_chat
from db import query
from scheduler.register_time import get_register_time_message, is_last_day_of_month


class PostTypes(Enum):
    MondayMorning = "MondayMorning"
    FridayMorning = "FridayMorning"


def get_post_type_display_text(post_type):
    if post_type == PostTypes.MondayMorning:
        return "Måndag morgon"
    if post_type == PostTypes.FridayMorning:
        return "Fredag morgon"
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

    def event_friday_morning(self):
        self._send_scheduled_post(PostTypes.FridayMorning)

    def event_morning_check_in(self):
        #if is_last_day_of_month():
        #    self._send_message(**get_register_time_message())
        pass

    def start(self):
        schedule.every().monday.at("09:00", "Europe/Stockholm").do(
            self.event_monday_morning
        )

        schedule.every().friday.at("09:00", "Europe/Stockholm").do(
            self.event_friday_morning
        )

        schedule.every().day.at("08:30", "Europe/Stockholm").do(
            self.event_morning_check_in
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
            self._send_message(text=scheduled_post["text"])

            consume_scheduled_post(scheduled_post["post_id"])

    def _send_message(
        self,
        text: Optional[str] = None,
        attachments: Optional[Union[str, Sequence[Union[Dict, Attachment]]]] = None,
        blocks: Optional[Union[str, Sequence[Union[Dict, Block]]]] = None,
    ):
        for user in all_users(self.app):
            self.app.client.chat_postMessage(
                channel=get_private_chat(self.app, user),
                text=text,
                attachments=attachments,
                blocks=blocks,
            )

    def __init__(self, logger: Logger, app: App):
        self.logger = logger
        self.app = app
