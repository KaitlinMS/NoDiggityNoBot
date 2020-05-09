import discord

# Create an instance of the client
client = discord.Client();

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    print('There was a message!')
    print(message.content)
    if message.author == client.user:
        print('Message from self - ignore!')
        return

    if message.content.startswith('hello'):
        print('I see a hello!')
        await message.channel.send('Hello!')

client.run('NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU')
