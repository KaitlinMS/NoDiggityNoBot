import discord

TOKEN = 'NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU'

# Create an instance of the bot
bot = discord.Client();
#bot.server = bot.guild
bot.created_channel = None

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
    announcement_channel = bot.get_channel(channel_general)
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

@bot.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    # The bot needs to ignore its own messages!
    if message.author == bot.user:
        return

    server = message.guild
    general_channel = discord.utils.get(server.text_channels, name="general")

    #---------- New Movie Night Channel Creation ----------
    summon_movie_night_message = 'I summon'

    if message.content.find(summon_movie_night_message) >= 0:
        new_channel_name = message.content.replace(summon_movie_night_message, '')
        new_channel_name = new_channel_name.strip()

        bot.created_channel = await server.create_text_channel(new_channel_name)
        await message.channel.send('{0.mention} has been created!! Have a wonderful movie night friends!! :scorpion:'.format(bot.created_channel))
        #await created_channel.delete()

    #-----------------
    if message.channel == bot.created_channel:
        await general_channel.send('Got one!')


"""


    announcement_channel = bot.get_channel(channel_general)
    movie_channel = bot.get_channel(channel_movie_proposals)
    
    # The bot needs to ignore its own messages!
    if message.author == bot.user:
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
            print('Movie proposal: {}'.format(proposed_movies[message.content].movie_name))"""

@bot.event
async def on_reaction_add(reaction, user):
    await checkReactions(reaction.message)
    
@bot.event
async def on_reaction_remove(reaction, user):
    await checkReactions(reaction.message)

    
# Run the bot and init channels
bot.run(TOKEN)