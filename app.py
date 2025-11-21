"""
Hejbot - A Python Slack App Boilerplate
Built with Slack Bolt framework for Python
"""

from datetime import datetime
import logging
import sqlite3
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the Slack app
app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)

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
        thread_ts=event.get("ts")  # Reply in thread
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
    user_id = event.get('user')
    text = event.get('text')
    con = sqlite3.connect("hejbot.db")
    cur = con.cursor()
    cur.execute("INSERT INTO cv_entries (user_id,text,timestamp) VALUES (?,?,?)",
        (user_id, text, datetime.now())
    )
    cv_entries = cur.execute("SELECT user_id,text,timestamp FROM cv_entries").fetchall()
    con.commit()
    con.close()

    logger.info(cv_entries)


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
                    "text": "Click the button below to see an interactive response!"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Click Me"
                        },
                        "action_id": "button_click",
                        "style": "primary"
                    }
                ]
            }
        ]
    )

@app.command("/cv")
def handle_cv_command(ack, command, say, logger):
    ack()
    logger.info(command)

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
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to Hejbot! 👋*"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This is your App Home. You can customize this view to show useful information."
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Available Commands:*\n• `/hello` - Get a greeting\n• `/demo-button` - See an interactive button demo"
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error updating home tab: {e}")

def setup_db():
    con = sqlite3.connect("hejbot.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS cv_entries(user_id,text,timestamp)")
    con.commit()
    con.close()

# ============================================================================
# Application Entry Point
# ============================================================================

def main():
    """Start the Slack bot application."""
    try:
        setup_db()

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
