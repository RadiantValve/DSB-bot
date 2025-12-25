from json_handler import usr_data as js
from dsb import DSBPlanExtractor
from dotenv import load_dotenv
from discord.ext import tasks
from datetime import datetime
import datetime
import discord
import logging
import shutil
import time
import os

users = js()

load_dotenv(dotenv_path=f'/.env')
DSB_ID = os.getenv('ID')
DSB_USER = os.getenv('USERNAME')
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

Intents = discord.Intents.default()
# dm intents
Intents.dm_messages = True
Intents.dm_reactions = True
Intents.dm_typing = True
#server intents
Intents.guild_messages = True
Intents.guild_reactions = True
Intents.guild_typing = True
Intents.guilds = True
Intents.members = True

client = discord.Client(intents=Intents)

def log(message):

    logging.basicConfig(
        filename='bot.log',                # Log file name
        level=logging.INFO,                # Log level
        format='%(asctime)s %(message)s',  # Timestamp format
        datefmt='%Y-%m-%d %H:%M:%S'        # Date format
    )
    logging.info(message)

#@client.event
#async def on_ready():
#    print(client.user)
#    for i in client.guilds:
#        print(f'{i}\n{i.member_count}')
#        for o in i.members:
#            print(o)

class MyClient(discord.Client):
    logging = True
    async def on_ready(self):
        log(f'Logged in as {self.user} (ID: {self.user.id})')
        log('------')

        print(client.user)
        for i in client.guilds:
            print(f'{i}\n{i.member_count}')
            for o in i.members:
                print(o)
    send_times =  []
    
    def set_send_times(self):
        #send_times = [datetime.time(hour=7, minute=45), datetime.time(hour=9, minute=30)]
        self.send_times =  []
        for u in users.get_users_sendinfo():
            h, m = users.get_user_time(u)
            self.send_times.append(datetime.time(hour=h, minute=m))
    
    async def send_dsb_img(self, user, data):
        file_list = []
        extractor = DSBPlanExtractor(DSB_ID, DSB_USER)
        extractor.fetch_and_extract(data)

        images_folder = "images"
        if not os.path.exists(images_folder):
            return
        
        for file in os.listdir(images_folder):
            if file.endswith('.jpg'):
                file_list.append(file)
                await user.send(file=discord.File(os.path.join(images_folder, file)))
                time.sleep(.4)
        
        print(file_list)
        if file_list:
            await user.send("done")
        else:
            await user.send("No images found in the 'images' folder.")
    
    set_send_times()
    @tasks.loop(send_times)
    async def send_to_users(self):
        for u in users.get_users_sendinfo():
            for t in self.send_times:
                h, m = users.get_user_time(u)
                if datetime.time(hour=h, minute=m) == self.send_times[t]:
                    data = users.get_user_data(u)
                    user = await client.fetch_user(u)
                    self.send_dsb_img(user, data)

        print(1)

    @client.event
    async def on_message(self, message):
        print(message)
        print(message.author)
        print(message.content)

        commands = ['!h', '!help', '!hello', '!menu', 'get', 'backup']
        special_commands = ['-h', '-help', '-log', '-logstatus', '-sendlog', '-deluser']
            
        if self.logging:
            log(f'Message from {message.author}: {message.content}')
        
        if message.author == client.user:
            return
        
        if not users.user_known(message.author.id):
            # new user prompt
            await message.channel.send("Hi, this is the first time you are talking to this bot.\nFor an overview of commands, type `!help`\nIf you want to receive updates, type `!menu`")
            users.add_user(message.author.id, False, None, None, None)
            return
        
        if message.content == ('!help') or message.content == ('!h'):
            str1 = 'Available commands: '
            for c in commands:
                str1 = "\n".join((str1, c))
            await message.channel.send(str1)
        
        if message.content == ('!hello'):
            await message.channel.send('Hello! How can I assist you today?')
        
        if message.content == ('!menu'):
            view = MenuView()
            await message.channel.send(content=view.pages[0], view=view)
        
        if message.content == ('-help') or message.content == ('-h'):
            str1 = 'Available special commands: '
            for s in special_commands:
                str1 = "\n".join((str1, s))
            await message.channel.send(str1)
        
        if message.content == ('-log'):
            if not self.logging:
                self.logging = True
                log('Log command received.')
                await message.channel.send('Log entry created, logging started.')
            else:
                self.logging = False
                await message.channel.send('Logging stopped.')
        
        if message.content == ('-logstatus'):
            status = "Logging is active." if self.logging else "Logging is inactive."
            await message.channel.send(f'Current status: {status}')
        
        if message.content == ('-sendlog'):
            if os.path.exists('bot.log'):
                await message.channel.send(file=discord.File('bot.log'))
            else:
                await message.channel.send('No log file found.')
        
        if message.content == ('-deluser'):
            users.del_user(message.author.id)
            await message.channel.send(f'User '+str(message.author.id)+' deleted!')
        
        if message.content == ("get"):
            file_list = []
            await message.channel.send("ok")
            extractor = DSBPlanExtractor(DSB_ID, DSB_USER)
            extractor.get_all()
        
            # Look specifically for images in the 'images' folder
            images_folder = "images"
            if not os.path.exists(images_folder):
                await message.channel.send("The 'images' folder does not exist.")
                return
            
            for file in os.listdir(images_folder):
                if file.endswith('.jpg'):
                    file_list.append(file)
                    await message.channel.send(file=discord.File(os.path.join(images_folder, file)))
                    time.sleep(.4)
            
            print(file_list)
            if file_list:
                await message.channel.send("done")
            else:
                await message.channel.send("No images found in the 'images' folder.")
            return
        
        if message.content == ("backup"):
            await message.channel.send("Starting backup...")
            
            backup_folder = "backup"
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
            
            # Move images to the backup folder, organizing by date
            for file in os.listdir("images"):
                if file.endswith(".jpg"):
                    # Extract the date from the filename (assuming format like 'subst_8b_2025-11-24.jpg')
                    try:
                        # Split the filename and extract the date part
                        date_str = file.split("_")[-1].split(".")[0]  # Extract '2025-11-24'
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        date_folder = os.path.join(backup_folder, date_obj.strftime("%Y-%m-%d"))
                        
                        # Create the date folder if it doesn't exist
                        if not os.path.exists(date_folder):
                            os.makedirs(date_folder)
                        
                        # Move the file to the date folder
                        shutil.move(os.path.join("images", file), os.path.join(date_folder, file))
                    except ValueError:
                        await message.channel.send(f"Skipping file with invalid date format: {file}")
            
            await message.channel.send("Backup completed!")
        
        all_commands = commands + special_commands
        for c in all_commands:
            if message.content == c:
                return
        await message.channel.send('looking for commands? `!help`')


client = MyClient(intents=Intents)
client.run(TOKEN)