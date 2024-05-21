# SaveChannelBot

SaveChannelBot is a Discord bot that allows users to save and push messages from Discord channels. The bot can save messages from a specific channel or all channels in a server and then push these messages to another channel or all channels.

## Features

- Save messages from a specific channel.
- Save messages from all channels in a server.
- Push saved messages to a specific channel.
- Push saved messages to all channels.
- Save message attachments and re-upload them when pushing messages.

## Commands

- `!save help`: Displays the help message with all commands.
- `!save channel`: Saves messages from the current channel.
- `!save all channels`: Saves messages from all channels in the server.
- `!push channel [source_channel] [target_channel]`: Pushes messages from the source channel to the target channel. If no channels are specified, it pushes messages to the current channel.
- `!push all channels`: Pushes messages to all channels in the server.

## Installation

### Prerequisites

- Python 3.7 or higher
- Pip (Python package installer)
- A Discord bot token. You can get one by creating a new application on the [Discord Developer Portal](https://discord.com/developers/applications).

### Steps

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/yourusername/SaveChannelBot.git
   cd SaveChannelBot
   \`\`\`

2. Create and activate a virtual environment (optional but recommended):
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate   # On Windows use \`venv\\Scripts\\activate\`
   \`\`\`

3. Install the required dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. Create a \`bot-token.txt\` file in the root directory and add your Discord bot token:
   \`\`\`plaintext
   YOUR_BOT_TOKEN_HERE
   \`\`\`

5. Create a \`files\` directory in the root directory to store message attachments:
   \`\`\`bash
   mkdir files
   \`\`\`

6. Run the bot:
   \`\`\`bash
   python save_channel_bot.py
   \`\`\`

## Logging

The bot logs its activities to a file named \`myLog.log\` and also streams logs to the console. The log file is encoded in UTF-8 and includes detailed information about the bot's operations.

## Usage

Invite the bot to your Discord server using the OAuth2 URL provided on the Discord Developer Portal. Once the bot is in your server, you can use the commands listed above to save and push messages.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure that your code follows the existing style and structure.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Discord.py](https://github.com/Rapptz/discord.py) - A Python wrapper for the Discord API.

If you encounter any issues or have any questions, feel free to open an issue on GitHub or contact the project maintainers.

---

**Disclaimer:** This bot should be used responsibly and in accordance with Discord's Terms of Service. The authors are not responsible for any misuse of this bot.