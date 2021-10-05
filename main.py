import shutil
import sys
import time
import uuid
import requests
import discord
import logging


class MyClient(discord.Client):

    async def on_ready(self):
        logging.info('Logged in...')

    async def on_message(self, message):
        if message.content.startswith('!save help'):
            await message.channel.send('Hallo. Ich bin der SaveChannelBot\n\n!save channel: \tSpeichert die Nachrichten des aktuellen Channels\n!save all channels: \tSpeichert die Nachrichten aller Channels auf dem Server\n!push channel [von Channelname] [Ziel Channelname]: \tSchreibt die Nachrichten des von-Channels in den Ziel-Channel. Wenn von und Ziel nicht angegeben werden sind beide der Name des Channels, in den geschrieben wurden\n!push all channels: \tSchreibt Nachrichten in alle Channels')
        elif message.content.startswith('!save channel'):
            await self.save_messages_in_channel(message.channel)
        elif message.content.startswith('!save all channels'):
            await self.save_all_cahnnel_messages(message.guild, message.channel)
        elif message.content.startswith('!push channel'):
            # filter the named channel out of the user_input
            split_message = message.content.split(' ')
            if len(split_message) == 2:
                await self.push_messages_of_one_channel(str(message.channel), message.channel)#
            else:
                from_channel = split_message[2]
                if len(split_message) == 4:
                    target_channel = split_message[3]
                    for channel in message.guild.channels():
                        # if the named channel is in the actual iterating step
                        if target_channel.strip().lower() in str(channel).lower() and str(channel.type) == 'text':
                            await self.push_messages_of_one_channel(from_channel, target_channel)
                else:
                    await self.push_messages_of_one_channel(from_channel, message.channel)
        elif message.content.startswith('!push all channels'):
            await message.channel.send('Wichtig: Die Namen der Channel der gespeicherten Nachrichten müssen den Namen auf dem Zielserver entsprehen!')
            await self.push_all_channels(message.guild.channels)

    async def save_all_cahnnel_messages(self, cl, origin_channel):
        for channel in cl.channels:
            if str(channel.type) == 'text':
                await self.save_messages_in_channel(channel)
                time.sleep(3)
        await origin_channel.send('Nachrichten wurden erfolgreich gespeichert!')

    async def save_messages_in_channel(self, channel):
        try:
            with open('channelMessages.txt', 'a', encoding='UTF8') as file:
                file.write('\Channel: ' + str(channel) + '\n')
                async for m in channel.history(oldest_first=True, limit=None):
                    # Save only if the message is not from the save-bot
                    if m.author != client.user and str(m.author) != 'Rythm#3722': #toDo exclude bot-messages
                        content = m.content.replace('\n\n', '\n')
                        # save an image-attachement
                        try:
                            url = m.attachments[0].url
                        except:
                            pass
                        else:
                            if url[0:26] == 'https://cdn.discordapp.com':
                                r = requests.get(url, stream=True)
                                imageName = str(uuid.uuid4()) + '.jpg'
                                with open('img/' + imageName, 'wb') as out_file:
                                    shutil.copyfileobj(r.raw, out_file)
                                    content = '\IMAGEFILE: ' + imageName
                        try:
                            file.write(str(m.author.nick) + content + '\n')
                        except UnicodeEncodeError:
                            content = ''
                            for char in m.content:
                                if char.isascii():
                                    content += str(ord(char))
                                else:
                                    content += str(char)
                            file.write('Unknown ' + content + '\n')
                        except:
                            try:
                                file.write(str(m.author.name) + ' schrieb: ' + content + '\n')
                            except:
                                pass

            logging.info('Messages in the channel ' + str(channel) + ' were saved')
        except discord.errors.Forbidden:
            logging.warning('Insufficient permissions for channel ' + str(channel))

    async def push_all_channels(self, cl):
        for channel in cl:
            if str(channel.type) == 'text':
                logging.info(f'Call push_messages_of_one_channel with attr: ({str(channel)}, {channel}')
                await self.push_messages_of_one_channel(str(channel), channel)

    async def push_messages_of_one_channel(self, from_channel, target_channel):
        logging.info(f'startet push_messages_of_one_channel with attr: ({from_channel}, {target_channel})')
        channel_found = False
        # open the file with messages
        with open('channelMessages.txt', 'r', encoding='UTF8') as file:
            while not channel_found:
                next_message = file.readline()
                # if messages.txt is empty, return
                if not next_message:
                    logging.info('Reached End of File (channelMessages.txt)')
                    return
                # if the message contains a new Channel:
                elif next_message.startswith('\Channel:'):
                    # ... and the channel is the named channel
                    if next_message.replace('\Channel: ', '').replace('\n', '').lower() == str(from_channel).lower():
                        logging.info('Found named Channel: ' + str(from_channel))
                        channel_found = True
                        message_length = 0
                        temp_message = ''
                        while True:
                            next_message = file.readline()
                            logging.info('read next line: ' + next_message)
                            # stop loop, if reached the next channel or the end of file
                            if next_message.startswith('\Channel:') or not next_message:
                                # send remaining messages and then return
                                if temp_message is not None and temp_message != '':
                                    logging.info(f'send Message with length({message_length}) and content({temp_message})')
                                    await target_channel.send(temp_message)
                                    time.sleep(1)
                                return
                            # else send this message to the channel
                            else:
                                # build message
                                if 'schrieb: ' in next_message:
                                    next_message = next_message.split('schrieb: ')
                                    author = '**' + next_message[0] + '** \n'
                                    message_length += len(author)
                                    if message_length >= 4000:
                                        logging.info(f'send Message with length({message_length}) and content({temp_message})')
                                        await target_channel.send(temp_message)
                                        time.sleep(1)
                                        message_length = len(author)
                                        temp_message = author
                                    else:
                                        # append the the next message to new message_container
                                        message_length += len(temp_message)
                                        temp_message += author
                                    next_message = next_message[1]
                                if next_message.startswith('\IMAGEFILE: '):
                                    logging.info(f'send Message with length({message_length}) and content({temp_message})')
                                    await target_channel.send(temp_message)
                                    temp_message = ''
                                    message_length = 0
                                    picture_name = next_message.replace('\IMAGEFILE: ', '').replace('\n', '')
                                    logging.info(f'send Message with length({message_length}) and content({temp_message})')
                                    await target_channel.send(file=discord.File('img/'+picture_name))
                                    time.sleep(1)

                                else:
                                    message_length += len(author)
                                    # If the length of the message is greater than the max length of discord
                                    if message_length >= 4000:
                                        # send messages, reset counter (message_length) and set the next message
                                        # to the new message_container
                                        if temp_message is not None and temp_message != '':
                                            logging.info(f'send Message with length({message_length}) and content({temp_message})')
                                            await target_channel.send(temp_message)
                                            time.sleep(1)
                                        message_length = len(next_message)
                                        temp_message = next_message
                                    else:
                                        # append the the next message to new message_container
                                        next_message += '\n'
                                        message_length += len(temp_message)
                                        temp_message += next_message


if __name__ == "__main__":
    logging.basicConfig(
        filename='myLog.log',
        encoding='UTF8',
        level=logging.DEBUG,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    client = MyClient()
    client.run('') # Your Bot token
