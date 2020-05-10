import discord

TOKEN = 'NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU'

# Create an instance of the client
client = discord.Client();

# Store functional channels based on their ID
# This feels a bit rigid but general should never change and since the bot will create the movie channel it will store that down the road...
# Could get 'general' channel by name or ask for the desired target name when the bot starts.
channel_general = 708518180095655998

# Set up our movie list (which is actually a Dictionary, not a List!)
proposed_movies = {}

# Create a "proposal" object, which keeps track of the movie proposals
class Proposal(object):
    def __init__(self, movie_name = "", votes = 0, vetoed = False):
        self.movie_name = movie_name
        self.votes = votes
        self.vetoed = vetoed

# Update the vote/veto counts in the proposal for the corresponding message
async def checkReactions(m):
    announcementChannel = client.get_channel(channel_general)
    numberOfPoops = 0
    numberOfVotes = 0
    
    for r in m.reactions:
        if r.emoji == '💩':
            numberOfPoops += 1
        if r.emoji == '👍':
            numberOfVotes += 1
            
    if numberOfPoops > 0 and proposed_movies[m.content].vetoed == False:
        proposed_movies[m.content].vetoed = True
        await announcementChannel.send('{0} has been vetoed by ||{1}||!'.format(m.content, m.author.name))
    elif numberOfPoops <= 0 and proposed_movies[m.content].vetoed == True:
        proposed_movies[m.content].vetoed = False
        await announcementChannel.send('{0} is no longer vetoed! The plot thickens!'.format(m.content))
        
    proposed_movies[m.content].votes = numberOfVotes
    
    
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
    movieNumber = 0
    for key in proposed_movies:
        print('Movie ' + str(movieNumber) + ':')
        print('Title:')
        print(proposed_movies[key].movie_name)
        print('Current votes:')
        print(proposed_movies[key].votes)
        print('IsVetoed:')
        print(proposed_movies[key].vetoed)

@client.event
async def on_reaction_add(reaction, user):
    await checkReactions(reaction.message)
    
@client.event
async def on_reaction_remove(reaction, user):
    await checkReactions(reaction.message)

# Run the client and init channels
client.run(TOKEN)