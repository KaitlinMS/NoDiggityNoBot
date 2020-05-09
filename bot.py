import discord

# Create an instance of the client
client = discord.Client();

@client.event
async def on_ready():
  print('Successfully logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

@client.event
async def on_reaction_add(reaction, user):
  if reaction.emoji == '💩' and reaction.count == 1:
    await reaction.message.channel.send('{0} has been vetoed by ||{1}||!'.format(reaction.message.content, reaction.message.author.name))

client.run('NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU')
