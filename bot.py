import discord

# Create an instance of the client
client = discord.Client();

@client.event
async def on_ready():
  print('Successfully logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # The bot needs to ignore its own messages!
    if message.author == client.user:
        return

    # Detect if someone has two movie choices in their message
    if '\n' in message.content:
      await message.author.send('It looks like you just put two movies into one message! Please split your movies into two messages.')

@client.event
async def on_reaction_add(reaction, user):
  # Veto detection
  if reaction.emoji == '💩' and reaction.count == 1:
    await reaction.message.channel.send('{0} has been vetoed by ||{1}||!'.format(reaction.message.content, reaction.message.author.name))

client.run('NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU')
