# Hejbot - Python Slack App Boilerplate

A production-ready Python Slack bot boilerplate built with the [Slack Bolt framework](https://slack.dev/bolt-python/). This boilerplate provides a solid foundation for building Slack applications with modern Python best practices.

## Features

- 🚀 **Slack Bolt Framework** - Official Python framework for Slack apps
- 🔌 **Socket Mode Support** - Easy local development without exposing endpoints
- 🐳 **Docker Support** - Containerized deployment ready
- ⚙️ **Configuration Management** - Centralized config with environment variables
- 📝 **Comprehensive Examples** - Event listeners, slash commands, interactive components, and modals
- 🏠 **App Home Tab** - Custom home tab implementation
- 🔒 **Security Best Practices** - Environment-based secrets management
- 📊 **Logging** - Structured logging for debugging and monitoring

## Quick Start

### Prerequisites

- Python 3.11 or higher
- A Slack workspace where you can install apps
- Slack App credentials (Bot Token, App Token, Signing Secret)

### 1. Clone the Repository

```bash
git clone https://github.com/hejare/hejbot.git
cd hejbot
```

### 2. Set Up Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app and select your workspace
4. Configure the following:

#### OAuth & Permissions
Add these Bot Token Scopes:
- `app_mentions:read` - View messages that directly mention your bot
- `chat:write` - Send messages as the bot
- `commands` - Add slash commands
- `im:history` - View messages in direct messages
- `im:write` - Send messages to direct messages
- `users:read` - View people in the workspace

#### Event Subscriptions
Enable Events and subscribe to:
- `app_mention` - When the bot is mentioned
- `message.im` - Messages in direct messages
- `app_home_opened` - When users open the app home

#### Interactivity & Shortcuts
- Enable Interactivity
- Add shortcuts if needed

#### Slash Commands
Create these commands:
- `/hello` - Description: "Say hello to the bot"
- `/demo-button` - Description: "Demo interactive button"

#### App Home
- Enable Home Tab
- Enable Messages Tab

#### Socket Mode (for local development)
- Enable Socket Mode
- Generate an App-Level Token with `connections:write` scope

5. Install the app to your workspace
6. Copy your tokens (found in "OAuth & Permissions" and "Basic Information")

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Slack credentials
# SLACK_BOT_TOKEN=xoxb-your-token
# SLACK_APP_TOKEN=xapp-your-token
# SLACK_SIGNING_SECRET=your-secret
```

### 4. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run the Bot

```bash
python app.py
```

You should see:
```
Starting Hejbot in Socket Mode...
⚡️ Bolt app is running!
```

## Usage Examples

### Mention the Bot
In any channel where the bot is added:
```
@hejbot Hello!
```

### Use Slash Commands
```
/hello
/demo-button
```

### Interact with Buttons
Use `/demo-button` to see an interactive button, then click it!

### View App Home
Click on the bot in your Slack sidebar to see the custom home tab.

## Project Structure

```
hejbot/
├── app.py                 # Main application with event handlers
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore patterns
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker Compose configuration
├── LICENSE               # License file
└── README.md             # This file
```

## Deployment

### Docker Deployment

```bash
# Build the image
docker build -t hejbot .

# Run with environment variables
docker run -d \
  --env-file .env \
  --name hejbot \
  hejbot
```

### Docker Compose

```bash
# Start the bot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

### Production Deployment

For production deployments:

1. **Disable Socket Mode**: Set `SOCKET_MODE=False` in your `.env`
2. **Configure HTTP endpoint**: Update your Slack app's Request URL to point to your server
3. **Use a reverse proxy**: Set up nginx or similar in front of your app
4. **Enable HTTPS**: Slack requires HTTPS for production apps
5. **Monitor logs**: Set up proper logging and monitoring
6. **Scale horizontally**: Deploy multiple instances behind a load balancer if needed

### Platform-Specific Deployment

#### Heroku
```bash
# Add Procfile
echo "web: python app.py" > Procfile

# Deploy
git push heroku main
```

#### AWS/GCP/Azure
Deploy the Docker container using their respective container services (ECS, Cloud Run, Container Instances).

## Development

### Adding New Commands

```python
@app.command("/yourcommand")
def handle_your_command(ack, command, say):
    ack()
    say("Your response here")
```

### Adding New Event Listeners

```python
@app.event("event_type")
def handle_event(event, say, logger):
    logger.info(f"Event received: {event}")
    say("Response to event")
```

### Adding Interactive Components

```python
@app.action("your_action_id")
def handle_action(ack, body, say):
    ack()
    say("Action handled!")
```

### Testing Locally

The boilerplate uses Socket Mode by default, which is perfect for local development:
- No need to expose your local machine to the internet
- No need for ngrok or similar tools
- Instant feedback while developing

## Configuration Options

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SLACK_BOT_TOKEN` | Bot User OAuth Token | Yes | - |
| `SLACK_APP_TOKEN` | App-Level Token (Socket Mode) | Yes (Socket Mode) | - |
| `SLACK_SIGNING_SECRET` | Signing Secret for request verification | Yes | - |
| `SOCKET_MODE` | Enable Socket Mode | No | True |
| `PORT` | HTTP server port | No | 3000 |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | INFO |

## Troubleshooting

### Bot doesn't respond to mentions
- Ensure the bot is added to the channel
- Check that `app_mentions:read` and `chat:write` scopes are added
- Verify the bot is running and logs show no errors

### Slash commands don't work
- Verify commands are created in your Slack app settings
- Check that the bot is running
- Look for errors in the logs

### Socket Mode connection issues
- Verify `SLACK_APP_TOKEN` is set correctly
- Ensure Socket Mode is enabled in your Slack app
- Check your internet connection

### Import errors
- Make sure you've activated your virtual environment
- Run `pip install -r requirements.txt` again

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Resources

- [Slack Bolt for Python Documentation](https://slack.dev/bolt-python/)
- [Slack API Documentation](https://api.slack.com/)
- [Building Slack Apps](https://api.slack.com/start/building)
- [Block Kit Builder](https://api.slack.com/block-kit/building) - Visual builder for Slack messages

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/hejare/hejbot).
