import discord

TOKEN = 'NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU'

# Create an instance of the client
client = discord.Client();

# Store functional channels based on their ID
# This feels a bit rigid but general should never change and since the bot will create the movie channel it will store that down the road...
# Could get 'general' channel by name or ask for the desired target name when the bot starts.
channel_general = 708518180095655998
channel_movie_proposals = 708534785102053408

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
    announcement_channel = client.get_channel(channel_general)
    number_of_poops = 0
    number_of_votes = 0

    for r in m.reactions:
        if r.emoji == '💩':
            number_of_poops += 1
        if r.emoji == '👍':
            number_of_votes += 1

    if number_of_poops > 0 and proposed_movies[m.content].vetoed == False:
        proposed_movies[m.content].vetoed = True
        await announcement_channel.send('{0} has been vetoed by ||{1}||!'.format(m.content, m.author.name))
    elif number_of_poops <= 0 and proposed_movies[m.content].vetoed == True:
        proposed_movies[m.content].vetoed = False
        await announcement_channel.send('{0} is no longer vetoed! The plot thickens!'.format(m.content))

    proposed_movies[m.content].votes = number_of_votes


# Now we start listening to all the different Discord events!

@client.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    announcement_channel = client.get_channel(channel_general)
    movie_channel = client.get_channel(channel_movie_proposals)

    # The bot needs to ignore its own messages!
    if message.author == client.user:
        return

    #--------- ANNOUNCMENT CHANNEL BEHAVIOUR ---------
    if message.channel == announcement_channel:
        if message.content == 'Movie Status':
            vetoed_movies = {}
            output = ['🌟 THE CURRENT STATUS 🌟']
            # TODO sort these outputs by vote count
            for key in proposed_movies:
                if proposed_movies[key].vetoed == False:
                    output.append('{} - holds {} votes'.format(proposed_movies[key].movie_name, proposed_movies[key].votes))
                else:
                    vetoed_movies[key] = proposed_movies[key]

            if len(vetoed_movies) > 0:
                output.append('-------')
                for key in vetoed_movies:
                    output.append('{} - holds {} votes, but has been 💩 upon!'.format(proposed_movies[key].movie_name, proposed_movies[key].votes))

            separator = '\n'
            await announcement_channel.send(separator.join(output))

    #--------- MOVIE CHANNEL BEHAVIOUR ---------
    if message.channel == movie_channel:
        # Detect if someone has two movie choices in their message
        if '\n' in message.content:
            await message.author.send('It looks like you just put two movies into one message! Please split your movies into two messages.')
        else:
            # Add a movie proposal to the list of all the proposals
            # This adds the movie as a key value pair, where the key is the movie name (content of the message) and the value is a new Proposal object
            proposed_movies[message.content] = Proposal(message.content, 0, False)

@client.event
async def on_message_delete(message):
    movie_channel = client.get_channel(channel_movie_proposals)

    # Let's make sure we're in the movie channel first
    if message.channel == movie_channel:
        proposed_movies.pop(message.content)

@client.event
async def on_reaction_add(reaction, user):
    await checkReactions(reaction.message)

@client.event
async def on_reaction_remove(reaction, user):
    await checkReactions(reaction.message)


# Run the client and init channels
client.run(TOKEN)
