from PIL import Image, ImageOps, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import discord

headerMessage = "Welcome"

#Make welcome banner
def bannerMake(avUrl,userName):
    #get profile picture
    url = avUrl
    name = userName.upper()
    response = requests.get(url)
    pfpImg = Image.open(BytesIO(response.content))
    pfpImg = pfpImg.resize((128, 128));

    #crop circular pfp
    bigsize = (pfpImg.size[0] * 3, pfpImg.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfpImg.size, Image.ANTIALIAS)
    pfpImg.putalpha(mask)
    output = ImageOps.fit(pfpImg, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    #add pfp to background
    background = Image.open('bg_temp.jpg')
    background = background.resize((background.width // 2, background.height // 2))
    background.paste(pfpImg,((background.width // 15)*6, background.height // 4), pfpImg)

    #Text
    W, H = (background.width,background.height)
    draw = ImageDraw.Draw(background)
    #Discord Name
    font = ImageFont.truetype('Fonts/arialbd.ttf', 30)
    w, h = draw.textsize(name, font=font)
    x, y = ((W-w)/2,4*(H-h)/5)
    draw.text((x-1, y), name, font=font, fill="black")
    draw.text((x+1, y), name, font=font, fill="black")
    draw.text((x, y-1), name, font=font, fill="black")
    draw.text((x, y+1), name, font=font, fill="black")
    draw.text((x, y), name, font=font, fill="white")
    #background.show()

    #Header
    header = headerMessage
    font = ImageFont.truetype('Fonts/arialbd.ttf', 36)
    w, h = draw.textsize(header, font=font)
    x, y = ((W-w)/2,(H-h)/8)
    draw.text((x-1, y), header, font=font, fill="black")
    draw.text((x+1, y), header, font=font, fill="black")
    draw.text((x, y-1), header, font=font, fill="black")
    draw.text((x, y+1), header, font=font, fill="black")
    draw.text((x, y), header, font=font, fill="white")
    #background.show()
    if os.path.exists('output.png'):
        os.remove('output.png')
        background.save('output.png')
    else:
        background.save('output.png')

#Discord Py
client = discord.Client()

#Config
"""
discordToken = ""
channel_id =
count_channel_id =
guild_id =
"""
#Heroku
discordToken = os.environ['TOKEN']
channel_id = os.environ['CHANNELID']
count_channel_id = os.environ['COUNTID']
guild_id = os.environ['GUILDID']

#Bot ready
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

#Member Join event
@client.event
async def on_member_join(member):
    await client.wait_until_ready()
    url = member.avatar_url
    name = member.name + "#" + member.discriminator
    print("User %s Joined"%name)
    bannerMake(url,name)
    channel = client.get_channel(int(channel_id))
    await channel.send(file=discord.File('output.png'))
    #Delete output file for welcome banner
    if os.path.exists('output.png'):
        os.remove('output.png')
    else:
        print('No output file')
    guild = client.get_guild(int(guild_id))
    total_members = guild.member_count
    count_channel = client.get_channel(int(count_channel_id))
    await count_channel.edit(name="Member Count: %d"%total_members)
    print("Updating Count Channel")
#Member Leave event
@client.event
async def on_member_remove(member):
    await client.wait_until_ready()
    name = member.name
    print("User %s Left"%name)
    guild = client.get_guild(int(guild_id))
    total_members = guild.member_count
    count_channel = client.get_channel(int(count_channel_id))
    await count_channel.edit(name="Member Count: %d"%total_members)
    print("Updating Count Channel")
#Run bot
client.run(discordToken)
