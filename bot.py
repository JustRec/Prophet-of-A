import discord
import os
import time
import random
from PIL import Image, ImageDraw, ImageFont
import requests
from dotenv import load_dotenv
import sqlite3

#Bot setup
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
load_dotenv()

#Database setup
con = sqlite3.connect('database.db', check_same_thread=False)
cursor = con.cursor()
cursor.execute('create table if not exists MEMBERS (ID INT PRIMARY KEY, TAG TEXT, GUILD TEXT, POINT_A INT, BODY INT)')
cursor.execute('create table if not exists GUILDS (ID INT PRIMARY KEY, GUILD TEXT, LAST_POSTER TEXT, LAST_TIME INT)')
con.commit()

#Global variable declaration
start = time.time() #timer
is_disapproval_sent = False
is_disapproval_wanted = False
disapprovals = []
leaderboard = {}
channel = client.get_channel(924370335774675004)

#Fill the dissaproval list with texts
f = open("content/disapproval.txt")
for i in range(7):
    disapprovals.append(f.readline())
f.close()

#Eternal pain of the thinking rock
print("AAAAAAAAAAAAAAAAAA")


@client.event
async def on_ready():
    global start
    print('We have logged in as {0.user}\n'.format(client))
    

@client.event
async def on_message(message):
    global start
    global is_disapproval_sent
    global is_disapproval_wanted
    global disapprovals
    global leaderboard
    global channel

    #Checks any currency words and converts them to try or usd
    async def CheckDolar():
        oil_cost = 25  #constant oil cost
        words = message.content.split(" ") #words pulled from message
        exchange_rate = 1
        number = 0
        is_it_usd = True #Is it usd that exist in message?

        #Search words that starts with currency names 
        for word in words:
            if word.startswith("dolar") or word.lower() == "usd":
                url = 'https://v6.exchangerate-api.com/v6/' + os.getenv('exchange') + '/latest/USD' #Exchange API
                response = requests.get(url)
                data = response.json()
                exchange_rate = data['conversion_rates']['TRY']
                break
            if word.startswith("tl") or word.startswith("lira"):
                url = 'https://v6.exchangerate-api.com/v6/' + os.getenv('exchange') + '/latest/TRY' #Exchange API
                response = requests.get(url)
                data = response.json()
                exchange_rate = data['conversion_rates']['USD']
                is_it_usd = False
                break

        #Check if there's any number is present in message
        for word in words:
            try:
                number = int(word)
                break
            except:
                number = number

        #If there is a currency name and a number than send a custom message
        if exchange_rate != 1 and number != 0:
            if is_it_usd:
                await message.channel.send("**" + str(number) + " dolar** bugünki kurla **" + "{:.2f}".format(number * exchange_rate) + " lira** ya da " + "{:.2f}".format(number * exchange_rate / oil_cost) + " litre yudum sıvıyağ ediyor")
            else:
                await message.channel.send("**" + str(number) + " lira** bugünki kurla **" + "{:.2f}".format(number * exchange_rate) + " dolar** ya da " + "{:.2f}".format(number / oil_cost) + " litre yudum sıvıyağ ediyor")


    #Send a message to 'channel' with a disapproval text
    async def SendDisapproval():
        if(is_disapproval_wanted):
            await channel.send(message.author.mention + disapprovals[random.randint(0, 6)])
    
    async def UpdateScores():
        global start
        db[message.guild.name + ".player." + db[message.guild.name + ".last_poster"]] += time.time() - start #Update player's score
        start = time.time()


    async def UpdateLeaderboard():
        counter = 0
        leaderboard = {}

        #Pull the .player data from db and sort them
        for key in db.prefix(message.guild.name + ".player"):
            leaderboard[key.replace(message.guild.name + ".player.", '')] = db[key]
        sorted_words = dict(sorted(leaderboard.items(), key=lambda x: x[1], reverse=True))

        #Open a text file and write player name with alignment spaces
        f = open("content/leaderboard.txt", "w")
        for key, value in sorted_words.items():
            f.write(key)
            for i in range(25 - len(key)):
                f.write(" ")

            #Turn seconds into other time formats
            t_value = value
            day = t_value // (24 * 3600)
            t_value = t_value % (24 * 3600)
            hour = t_value // 3600
            t_value %= 3600
            minutes = t_value // 60
            t_value %= 60
            seconds = t_value

            #Limiting floats to two decimal points and writing them
            day = int(day)
            hour = int(hour)
            minutes = int(minutes)
            seconds = int(seconds)

            f.write("  " + str(day) + " gün, " + str(hour) + " saat, " + str(minutes) + " dakika, " + str(seconds) + " saniye\n \n")
            counter += 1

            if counter == 5: break
        f.close()

    #Return if message author is bot
    if message.author == client.user:
        return

    if message.channel.name == "the-holy-a-chain":

        #If the last_poster is the same as the message author then print dissaproval text
        if str(message.author) == db[message.guild.name + ".last_poster"]:
            if (not is_disapproval_sent):
                await SendDisapproval()
            await message.delete()
            is_disapproval_sent = True
            return

        #If the message is 'a' then update the last poster, otherwise send dissapproval text
        if message.content == 'a':
            await UpdateScores()
            db[message.guild.name + ".last_poster"] = str(message.author) 
            is_disapproval_sent = False

            print(message.guild.name + ".player." + str(message.author) +
                  '  ' + str(db[message.guild.name + ".player." +
                                str(message.author)]))

        else:
            if (not is_disapproval_sent):
                await SendDisapproval()
            await message.delete()
            is_disapproval_sent = False

    if message.content.startswith("&lidertahtası"):
        await UpdateScores()
        await UpdateLeaderboard()
        f = open("content/leaderboard.txt")
        leaderboard_content = f.read()
        f.close()
        
        fnt = ImageFont.truetype('cool.otf', 20) #Setup font
        img = Image.new('RGB', (600, 300), color = (54, 56, 63)) #Create blank image

        #Draw the leaderboard text to the blank image
        d = ImageDraw.Draw(img)
        d.multiline_text((10,10), leaderboard_content, font=fnt, fill=(119, 51, 255))
        img.save("leaderboard.png")
        
        #Setup an embed that carries leaderboard image
        embed = discord.Embed(title="Leaderboard", description="ヾ( ・ω・ｏ)", color=0x00ff00)
        file = discord.File("leaderboard.png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        
        await message.channel.send(file=file, embed=embed)


    if message.content.startswith("&kınama"):
        if db[message.guild.name + ".mod." + str(message.author)]:
            if(is_disapproval_wanted):
                await message.channel.send("Kınamalar şimdi **kapalı**")
                is_disapproval_wanted = False
            else:
                await message.channel.send("Kınamalar şimdi **açık**")
                is_disapproval_wanted = True
    
    if message.content.startswith("&yardım"):        
        f = open("content/help.txt")
        embed = discord.Embed(title="Yardım!", description="", color=0x00ff00)
        embed.add_field(name = "Komutlar", value = f.read(), inline = True)
        await message.channel.send(embed = embed)
        f.close()

    if message.content.startswith("&ayarla_genel"):
        if db[message.guild.name + ".mod." + str(message.author)]:
            msg = message.content
            msg = msg.replace("&ayarla_genel", '')
            channel = client.get_channel(int(msg))
        

    if message.content.startswith("!fuck"):
        msg = message.content
        msg = msg.replace("!fuck ",  "")
        db[message.guild.name + ".body." + str(message.author)] += 1

    if message.content.startswith("&body"):
        await message.channel.send(str(db[message.guild.name + ".body." + str(message.author)]) + " kişi <:esebi_shy:891658390546284605> ")

    if message.content.startswith("&mod"):
        if message.author.name == "Jusrec":
            msg = message.content
            msg = msg.replace("!mod ",  "")
            db[message.guild.name + ".mod." + msg] = True
            



    
    await CheckDolar()




@client.event
async def on_guild_join(guild):
    #Wipe all the data when the bot joins a guild
    for key in db.keys():
        del db[key]

    #Create a key for everybody in the guild
    db[guild.name + ".last_poster"] = "Prophet of the A#4223"
    for member in guild.members:
        if not member.bot:
            db[guild.name + '.player.' + member.name + '#' +
            member.discriminator] = 0
            db[guild.name + '.body.' + member.name + '#' +
            member.discriminator] = 0

    db[guild.name + ".mod." + "Jusrec#1575"] = True
        


@client.event
async def on_member_join(member):
    #Create a key if a new member joins
    db[member.guild.name + '.player.' + member.name + '#' +
       member.discriminator] = 0



client.run(os.getenv('TOKEN'))

"""
To:Do

leaderboard font
remove bot score
OUJIA board
word count

"""
