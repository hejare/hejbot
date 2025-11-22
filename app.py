"""
Hejbot - A Python Slack App Boilerplate
Built with Slack Bolt framework for Python
"""

from datetime import datetime
import logging
import sqlite3
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI

from scheduler import Scheduler
from google_api import GoogleApi

from config import Config
from db import setup_db, query

client = OpenAI(api_key=Config.OPEN_AI_KEY)

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize the Slack app
app = App(token=Config.SLACK_BOT_TOKEN, signing_secret=Config.SLACK_SIGNING_SECRET)

# ============================================================================
# Event Listeners
# ============================================================================


@app.event("app_mention")
def handle_app_mention(event, say, logger):
    """
    Respond when the bot is mentioned in a channel.

    Args:
        event: The event data from Slack
        say: Function to send a message to the channel
        logger: Logger instance
    """
    user = event.get("user")
    text = event.get("text", "")

    logger.info(f"App mentioned by user {user}: {text}")

    say(
        text=f"Hello <@{user}>! You mentioned me. How can I help you today?",
        thread_ts=event.get("ts"),  # Reply in thread
    )


@app.event("message")
def handle_message_events(event, logger):
    """
    Handle message events (logged but not responded to automatically).

    Args:
        event: The event data from Slack
        logger: Logger instance
    """
    # Avoid responding to bot messages or messages without text
    if event.get("subtype") == "bot_message" or "text" not in event:
        return

    logger.info(f"Message event: {event}")

    # Add CV entry to database
    user_id = event.get("user")
    text = event.get("text")
    query(
        "INSERT INTO cv_entries (user_id,text,timestamp) VALUES (%s,%s,%s)",
        (user_id, text, datetime.now()),
    )


# ============================================================================
# Slash Commands
# ============================================================================


@app.command("/hello")
def handle_hello_command(ack, command, say, logger):
    """
    Handle the /hello slash command.

    Args:
        ack: Function to acknowledge the command
        command: The command data from Slack
        say: Function to send a message
        logger: Logger instance
    """
    ack()  # Acknowledge the command request

    user_id = command.get("user_id")
    logger.info(f"/hello command received from user {user_id}")

    say(f"Hello <@{user_id}>! 👋 This is a sample slash command response.")


# ============================================================================
# Interactive Components (Buttons, Modals, etc.)
# ============================================================================


@app.action("button_click")
def handle_button_click(ack, body, say, logger):
    """
    Handle button click interactions.

    Args:
        ack: Function to acknowledge the action
        body: The interaction payload
        say: Function to send a message
        logger: Logger instance
    """
    ack()  # Acknowledge the action

    user = body["user"]["id"]
    logger.info(f"Button clicked by user {user}")

    say(f"<@{user}> clicked the button! 🎉")


@app.command("/demo-button")
def handle_demo_button_command(ack, command, say):
    """
    Demo command that shows an interactive button.

    Args:
        ack: Function to acknowledge the command
        command: The command data
        say: Function to send a message with blocks
    """
    ack()

    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Click the button below to see an interactive response!",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click Me"},
                        "action_id": "button_click",
                        "style": "primary",
                    }
                ],
            },
        ]
    )


@app.command("/cv")
def handle_cv_command(ack, command, say, logger):
    ack()
    if not command.get("text"):
        ack("Please provide a query text. Usage: /cv <your text>")
        return
    text = command.get("text")
    user_id = command.get("user_id")

    if text.lower() == "generate":
        ack("Genererar din CV post...")
        logger.info("Generating CV...")

        user_info = app.client.users_info(user=user_id)
        first_name = user_info["user"]["profile"]["first_name"]

        entries = query(
            "SELECT user_id,text,timestamp FROM cv_entries WHERE user_id=%s", (user_id,)
        )
        entries_text = "\n-----------\n".join(
            [
                f"Text: {entry['text']}\nTimestamp: {entry['timestamp']}"
                for entry in entries
            ]
        )

        with open("cv_example.txt", "r") as f:
            cv_example = f.read()

        input = (
            f"Create a CV post for {first_name} based on the following entries:\n\n"
            f"{entries_text}"
        )
        instructions = (
            "You are a senior consultant profile writer at a tech consulting company.\n"
            "Your task is to generate a high-quality CV assignment description based on short notes collected from internal updates (Slack messages, meeting notes, project logs, etc.).\n"
            "Guidelines: Write in past tense and in third person (he/she/they).\n"
            "The text must read as a coherent narrative, not bullet points.\n"
            "Tone: professional, factual, while emphasizing impact, collaboration and problem-solving.\n"
            "Do not invent details, but you may logically combine and interpret provided notes to form a cohesive story.\n"
            "Highlight the consultant’s role, client context, challenges, contributions, collaboration, and results — even if only partially implied.\n"
            "Do not include dates or timestamps. Max 10 lines of text.\n"
            "Include: Who the client is (describe based on context, e.g., “a leading streaming provider” or “a major public service media company”), the consultant’s role and responsibilities, the client’s challenges and what needed improvement, actions taken including both technical and collaborative contributions, and outcomes and impact (quality improvements, new features, better processes, increased engagement, smoother releases, etc.).\n"
            "Write in a style similar to a modern consulting CV, concise but substantial, flowing naturally.\n"
            "Write in the same format and style as the following CV examples:\n\n"
            f"{cv_example}"
        )

        response = client.responses.create(
            model="gpt-5-nano", input=input, instructions=instructions
        )
        say(text=response.output_text)

    if text.lower() == "delete":
        ack("Raderar dina CV poster")
        query("DELETE FROM cv_entries WHERE user_id=%s", (user_id,))
        logger.info(f"Deleted entries for{user_id} ")


def query(query, parameters, fetch=False):
    con = sqlite3.connect("hejbot.db")
    cur = con.cursor()
    if fetch:
        results = cur.execute(query, parameters).fetchall()
    else:
        results = cur.execute(query, parameters)
    con.commit()
    con.close()
    return results

def get_db_connection():
    """Get a PostgreSQL database connection."""
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_DATABASE,
        user=Config.DB_USERNAME,
        password=Config.DB_PASSWORD,
        sslmode=Config.DB_SSL_MODE
    )

def query(query_text, parameters):
    """Execute a database query and return results."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query_text, parameters)
            if query_text.strip().upper().startswith("SELECT"):
                return cur.fetchall()
            else:
                return None


# ============================================================================
# Home Tab
# ============================================================================


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    """
    Update the App Home tab when a user opens it.

    Args:
        client: Slack Web API client
        event: The event data
        logger: Logger instance
    """
    try:
        user_id = event["user"]

        client.views_publish(
            user_id=user_id,
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "*Welcome to Hejbot! 👋*"},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This is your App Home. You can customize this view to show useful information.",
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Available Commands:*\n• `/hello` - Get a greeting\n• `/demo-button` - See an interactive button demo",
                        },
                    },
                ],
            },
        )
    except Exception as e:
        logger.error(f"Error updating home tab: {e}")


# ============================================================================
# Application Entry Point
# ============================================================================


def main():
    """Start the Slack bot application."""
    try:
        setup_db()

        scheduler = Scheduler(logger)
        scheduler.start()

        # google_api = GoogleApi(logger)
        # events = google_api.get_events()
        # logger.info(events)

        if Config.SOCKET_MODE:
            # Socket Mode - recommended for local development
            logger.info("Starting Hejbot in Socket Mode...")
            handler = SocketModeHandler(app, Config.SLACK_APP_TOKEN)
            handler.start()
        else:
            # HTTP Mode - for production deployment
            logger.info(f"Starting Hejbot in HTTP Mode on port {Config.PORT}...")
            app.start(port=Config.PORT)
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise


if __name__ == "__main__":
    main()
