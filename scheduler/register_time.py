from datetime import date

import holidays
from dateutil import relativedelta


def is_last_day_of_month():
    se_holidays = holidays.country_holidays("SE")
    date_today = date.today()
    date_last = date_today + relativedelta.relativedelta(day=31)
    while True:
        if date_last.weekday() < 5 and date_last not in se_holidays:
            break
        date_last = date_last + relativedelta.relativedelta(days=-1)

    return date_today == date_last


def get_register_time_message():
    return {
        "text": "Påminnelse! Nu är det sista dagen i månaden att tidsrapportera! Var en snäll hejare och rapportera i tid!",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":mega: Påminnelse! :mega:\n*Nu är det sista dagen i månaden att tidsrapportera!* :timer_clock: Var en snäll hejare och rapportera i tid! :petpethej:\nOch du minns väl det här tydliga <https://hejare.slack.com/archives/C3YUF4H1U/p1761732017784409|meddelandet om tidsrapportering> från ellen? :gazellen:",
                },
            }
        ],
        "attachments": [
            {
                "color": "#fcb0c0",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":white_check_mark: *Interntid:* När var det självstyre/bubbelträff? Något annat vi gjort internt som ska registreras? Kolla i kalendern så det blir rätt!",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":white_check_mark: *Tid på uppdraget:* Dubbelkolla så att det registrerats rätt, och registrerar ni tid hos kund internt i något system där - dubbelchecka så att tiderna överrensstämmer så det inte diffar där (annars skickar vi fel belopp på fakturan och det tar mycket tid att reglera sådana missar!)",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":white_check_mark: *Frånvaro?* Om ni registrerar frånvaro som inte är sjukfrånvaro - skriv gärna en kommentar med kort beskrivning om vad det gäller så blir det lättare att förstå för Lynette direkt.",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":white_check_mark: *Klarmarkera!* Glöm inte att klarmarkera fram till och med sista dag i månaden!",
                        },
                    },
                ],
            }
        ],
    }
