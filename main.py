import shutil
import sys
import asyncio
import uuid
import requests
import discord
from discord import Intents
import logging
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(
    filename='myLog.log',
    encoding='UTF8',
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

client = discord.Client(intents=Intents())


@client.event
async def on_ready():
    """Logs when the bot is ready."""
    logging.info('Logged in...')


@client.event
async def on_message(message):
    """Handles incoming messages and triggers the appropriate commands."""
    if message.content.startswith('!save help'):
        await send_help_message(message.channel)
    elif message.content.startswith('!save channel'):
        await save_messages_in_channel(message.channel)
    elif message.content.startswith('!save all channels'):
        await save_all_channels(message.guild, message.channel)
    elif message.content.startswith('!push channel'):
        await handle_push_channel(message)
    elif message.content.startswith('!push all channels'):
        await push_all_channels(message.guild.channels, message.channel)


async def send_help_message(channel):
    """Sends a help message to the specified channel."""
    help_text = (
        'Hallo. Ich bin der SaveChannelBot\n\n'
        '!save channel: \tSpeichert die Nachrichten des aktuellen Channels\n'
        '!save all channels: \tSpeichert die Nachrichten aller Channels auf dem Server\n'
        '!push channel [von Channelname] [Ziel Channelname]: '
        '\tSchreibt die Nachrichten des von-Channels in den Ziel-Channel. '
        'Wenn von und Ziel nicht angegeben werden sind beide der Name des Channels, in den geschrieben wurden\n'
        '!push all channels: \tSchreibt Nachrichten in alle Channels'
    )
    await channel.send(help_text)


async def save_all_channels(guild, origin_channel):
    """Saves messages from all text channels in the guild."""
    start_time = datetime.now()
    for channel in guild.channels:
        if str(channel.type) == 'text':
            await save_messages_in_channel(channel)
            await asyncio.sleep(3)
    await origin_channel.send('Nachrichten wurden erfolgreich gespeichert!')
    end_time = datetime.now()
    logging.info(f'Started with saving at {start_time} and stopped at {end_time}.'
                 f' So it took {(end_time - start_time).total_seconds()}')


async def save_messages_in_channel(channel):
    """Saves messages from the specified channel."""
    try:
        with open('channelMessages.txt', 'a', encoding='UTF8') as messages_file:
            messages_file.write(f'\nChannel: {channel}\n')
            async for message in channel.history(oldest_first=True, limit=None):
                if message.author != client.user:
                    content = await handle_message_content(message)
                    messages_file.write(content)
        logging.info(f'Messages in the channel {channel} were saved')
    except discord.errors.Forbidden:
        logging.warning(f'Insufficient permissions for channel {channel}')


async def handle_message_content(message):
    """Handles the content of a message and returns it as a formatted string."""
    content = message.content.replace('\n\n', '\n')
    if message.attachments:
        url = message.attachments[0].url
        if url.startswith('https://cdn.discordapp.com'):
            content += await save_attachment(url)
    try:
        return f'{message.author.nick} {content}\n'
    except UnicodeEncodeError:
        safe_content = ''.join(char if char.isascii() else str(ord(char)) for char in message.content)
        return f'Unknown {safe_content}\n'
    except:
        if not message or not message.author or not message.author.name:
            return f'Unknown schrieb: {content}\n'
        return f'{message.author.name} schrieb: {content}\n'


async def save_attachment(url):
    """Saves an attachment from a URL and returns a reference string."""
    response = requests.get(url, stream=True)
    image_name = f'{uuid.uuid4()}.{url.rsplit(".", 1)[1].lower()}'
    with open(f'files/{image_name}', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    return f'\nFILE: {image_name}'


async def handle_push_channel(message):
    """Handles the push channel command."""
    split_message = message.content.split(' ')
    from_channel = str(message.channel) if len(split_message) == 2 else split_message[2]
    target_channel_name = split_message[3] if len(split_message) == 4 else from_channel
    target_channel = get_channel_by_name(message.guild, target_channel_name)
    if target_channel:
        await push_messages_of_one_channel(from_channel, target_channel)


async def push_all_channels(channels, origin_channel):
    """Pushes messages to all channels."""
    await origin_channel.send(
        'Wichtig: Die Namen der Channel der gespeicherten Nachrichten müssen den Namen auf dem Zielserver entsprechen!')
    for channel in channels:
        if str(channel.type) == 'text':
            await push_messages_of_one_channel(str(channel), channel)


async def push_messages_of_one_channel(from_channel, target_channel):
    """Pushes messages from one channel to another."""
    with open('channelMessages.txt', 'r', encoding='UTF8') as channel_messages_file:
        for next_message in channel_messages_file:
            if next_message.startswith('\nChannel:'):
                current_channel = next_message.strip().replace('\nChannel: ', '')
                if current_channel.lower() == from_channel.lower():
                    await process_messages(channel_messages_file, target_channel)
                    break


async def process_messages(messages_file, target_channel):
    """Processes and sends messages to the target channel."""
    message_length = 0
    temp_message = ''
    for line in messages_file:
        if line.startswith('\nChannel:') or not line:
            if temp_message:
                await target_channel.send(temp_message)
            break
        temp_message, message_length = await build_message(line, temp_message, message_length, target_channel)


async def build_message(line, temp_message, message_length, target_channel):
    """Builds a message from a line and sends it if necessary."""
    if '!save' in line or '!push' in line:
        return temp_message, message_length
    if 'schrieb: ' in line:
        author, content = line.split('schrieb: ')
        author_formatted = f'**{author}**\n'
        if message_length + len(author_formatted) >= 2000:
            await target_channel.send(temp_message)
            await asyncio.sleep(1)
            temp_message = author_formatted
            message_length = len(author_formatted)
        else:
            temp_message += author_formatted
            message_length += len(author_formatted)
        return temp_message + content, message_length + len(content)
    if line.startswith('\nFILE: '):
        await target_channel.send(temp_message)
        file_name = line.replace('\nFILE: ', '').strip()
        await target_channel.send(file=discord.File(f'files/{file_name}'))
        return '', 0
    if message_length + len(line) >= 2000:
        await target_channel.send(temp_message)
        await asyncio.sleep(1)
        return line, len(line)
    return temp_message + line, message_length + len(line)


def get_channel_by_name(guild, name):
    """Gets a channel by name."""
    for channel in guild.channels:
        if channel.name == name and str(channel.type) == 'text':
            return channel
    return None


if __name__ == "__main__":
    token = config['discord']['token']
    client.run(token)
