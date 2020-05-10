import discord

# Create an instance of the client
client = discord.Client();

# Set up our movie list (which is actually a Dictionary, not a List!)
proposed_movies = {}

# Create a "proposal" object, which keeps track of the movie proposals
class Proposal(object):
  def __init__(self, movie_name = "", votes = 0, vetoed = False):
    self.movie_name = movie_name
    self.votes = votes
    self.vetoed = vetoed

# Now we start listening to all the different Discord events!

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
      return

    # Add a movie proposal to the list of all the proposals
    # TODO: This should only occur when the proposal is made in the designated movie channel
    # This adds the movie as a key value pair, where the key is the movie name (content of the message) and the value is a new Proposal object
    proposed_movies[message.content] = Proposal(message.content, 0, False)
    print(proposed_movies) # TODO: print the contents of the value... my brain can't handle that right now

@client.event
async def on_reaction_add(reaction, user):
  # Veto detection
  if reaction.emoji == '💩' and reaction.count == 1:
    await reaction.message.channel.send('{0} has been vetoed by ||{1}||!'.format(reaction.message.content, reaction.message.author.name))

# Finally: run the bot!

client.run('NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU')
