import discord

# Create an instance of the client
client = discord.Client();

@client.event
async def on_ready():
  print ('We have logged in as {user.0}').format(client())

@client.event
async def on_message():
  # This is called every time there's a message, so make sure that it wasn't us that sent the message!
  if message.author == client.user:
    return

  if message.content.startswith('$hello'):
    await message.channel.send('Hello!')

client.run('NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU')
