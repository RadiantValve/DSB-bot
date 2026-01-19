from json_handler import usr_data as js
from dsb import DSBPlanExtractor
from dotenv import load_dotenv
from discord.ext import tasks
from datetime import datetime
import discord
import logging
import time
import os

load_dotenv(dotenv_path=f'/.env')
DSB_ID = os.getenv('ID')
DSB_USER = os.getenv('USERNAME')
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

users = js()
extractor = DSBPlanExtractor(DSB_ID, DSB_USER)

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
    send_times = [(7, 0)]
    auto_send_loop = True
    async def on_ready(self):
        log(f'Logged in as {self.user} (ID: {self.user.id})')
        log('------')

        print(client.user)
        for i in client.guilds:
            print(f'{i}\n{i.member_count}')
            for o in i.members:
                print(o)
        self.restart_auto_send_loop()
        #self.set_send_times()
        print("init complete")
    
    #def set_send_times(self):
    #    #send_times = [(7, 45), (9, 30)]
    #    self.send_times =  []
    #    for u in users.get_users_sendinfo():
    #        h, m = users.get_user_time(u)
    #        self.send_times.append((h, m))
    #    self.restart_auto_send_loop()
    
    async def send_dsb_img(self, u, data):
        file_list = []
        extractor.fetch_and_extract(data)
        user = await client.fetch_user(u)

        images_folder = "images"
        if not os.path.exists(images_folder):
            return
        
        for file in os.listdir(images_folder):
            if file.endswith('.jpg'):
                file_list.append(file)
                await user.send(file=discord.File(os.path.join(images_folder, file)))
        
        print(file_list)
        if file_list:
            await user.send("done")
        else:
            await user.send("No images found in the 'images' folder.")
    
    async def restart_auto_send_loop(self):
        if self.auto_send_loop == False:
            self.auto_send_loop = True
            self.send_to_users_enqueue()
        elif self.auto_send_loop == True:
            self.auto_send_loop = False
            time.sleep(70)
            self.auto_send_loop = True
            self.send_to_users_enqueue()

    async def send_to_users_enqueue(self): #enques users to get messages sent
        while self.auto_send_loop:
            now = datetime.now()
            queue = []
            for u in users.get_users_sendinfo():
                h, m = users.get_user_time(u)
                if h == now.hour and m == now.minute:
                    queue.append(u)
            self.send_to_users_dequeue(queue)
            time.sleep(60)
    
    async def send_to_users_dequeue(self, queue):
        while queue != []:
            for i in queue:
                data = users.get_user_data(i)
                self.send_dsb_img(i, data)
                if extractor.backup():
                    print("backup sucessfull")
                else:
                    print("backup failed...")
                queue.remove[i]



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
            extractor = DSBPlanExtractor(DSB_ID, DSB_USER)
            await message.channel.send("Starting backup...")
            if extractor.backup():
                await message.channel.send("Backup completed!")
            else:
                await message.cannel.send("Error while moving files...")
            
            
        
        all_commands = commands + special_commands
        for c in all_commands:
            if message.content == c:
                return
        await message.channel.send('looking for commands? `!help`')


client = MyClient(intents=Intents)
client.run(TOKEN)