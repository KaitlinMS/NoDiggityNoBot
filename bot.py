import discord
import random

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
async def checkReactions(m, user):
    server = m.guild
    general_channel = discord.utils.get(server.text_channels, name="general")

    number_of_poops = 0
    number_of_votes = 0
    
    for r in m.reactions:
        if r.emoji == '💩':
            number_of_poops = r.count
        if r.emoji == '👍':
            number_of_votes = r.count
            
    if m.content in proposed_movies:
        if number_of_poops > 0 and proposed_movies[m.content].vetoed == False:
            proposed_movies[m.content].vetoed = True
            await general_channel.send('{0} has been 💩\'d by ||{1}||!'.format(m.content, user.display_name))
        elif number_of_poops <= 0 and proposed_movies[m.content].vetoed == True:
            proposed_movies[m.content].vetoed = False
            await general_channel.send('{0} is no longer 💩\'d! The plot thickens!'.format(m.content))
        
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

    #--------- MOVIE CHANNEL BEHAVIOUR ---------
    if message.channel == bot.created_channel:
        # Detect if someone has two movie choices in their message
        if '\n' in message.content:
            await message.author.send('🛑👮🚓🚨 It looks like you just put two movies into one message! Please split your movies into two messages:')
            await message.author.send(message.content)
            await message.add_reaction('🛑')
            await message.add_reaction('👮')
            await message.add_reaction('🚓')
            await message.add_reaction('🚨')
        else:
            # Add a movie proposal to the list of all the proposals
            # This adds the movie as a key value pair, where the key is the movie name (content of the message) and the value is a new Proposal object
            proposed_movies[message.content] = Proposal(message.content, 0, False)
            print('Movie proposal: {}'.format(proposed_movies[message.content].movie_name))

    #--------- ANNOUNCMENT CHANNEL BEHAVIOUR ---------
    if message.channel == general_channel:
        lowerMessage = message.content.lower()

        #---------- NEW CHANNEL CREATION  ----------
        summon_movie_night_message = 'I summon'
        if message.content.find(summon_movie_night_message) >= 0:
            new_channel_name = message.content.replace(summon_movie_night_message, '')
            new_channel_name = new_channel_name.strip()

            bot.created_channel = await server.create_text_channel(new_channel_name)
            await message.channel.send('{0.mention} has been created!! Have a wonderful movie night friends!! :scorpion:'.format(bot.created_channel))
            print('{} has been created.'.format(bot.created_channel))

        #---------- SHORT LIST SUMMON ----------
        if lowerMessage == 'short list':
            short_list = {}

            top_vote = 0
            for key in proposed_movies:
                if proposed_movies[key].votes > top_vote and proposed_movies[key].vetoed == False:
                    top_vote = proposed_movies[key].votes

            print('Top vote value: {}'.format(top_vote))

            for key in proposed_movies:
                if proposed_movies[key].votes == top_vote:
                    short_list[key] = proposed_movies[key]

            if len(short_list) < 3:
                second_top_vote = 0
                for key in proposed_movies:
                    if proposed_movies[key].votes > second_top_vote and proposed_movies[key].votes < top_vote and proposed_movies[key].vetoed == False:
                        second_top_vote = proposed_movies[key].votes

                print('Second-top vote value: {}'.format(second_top_vote))

                for key in proposed_movies:
                    if proposed_movies[key].votes == second_top_vote:
                        short_list[key] = proposed_movies[key]

            if len(short_list) < 3:
                third_top_vote = 0
                for key in proposed_movies:
                    if proposed_movies[key].votes > third_top_vote and proposed_movies[key].votes < second_top_vote and proposed_movies[key].vetoed == False:
                        second_top_vote = proposed_movies[key].votes

                print('Third-top vote value: {}'.format(third_top_vote))

                for key in proposed_movies:
                    if proposed_movies[key].votes == third_top_vote:
                        short_list[key] = proposed_movies[key]

            output = ['🚨 --------------------- - 🚨 FINAL VOTE 🚨 - --------------------- 🚨']
            for key in short_list:
                movie_name = proposed_movies[key].movie_name
                output.append(movie_name)

            separator = '\n'
            await general_channel.send(separator.join(output))

        #---------- STATUS REPORT SUMMON ----------
        if lowerMessage == 'movie status' or lowerMessage == 'status report':
            vetoed_movies = {}
            output = ['>>>------------------ - 🌟 THE CURRENT STATUS 🌟 - ------------------<<<']

            sorted_movie_proposals = {}
            for key in proposed_movies:
                sorted_movie_proposals[key] = proposed_movies[key].votes

            sorted_movie_proposals = sorted(sorted_movie_proposals.items(), key=lambda x: x[1], reverse=True)

            for obj in sorted_movie_proposals:
                key = obj[0]
                movie_name = proposed_movies[key].movie_name
                vote_count = proposed_movies[key].votes
                if proposed_movies[key].vetoed == False:
                    if vote_count == 0:
                        output.append('0👍 - {0} - has received no love.'.format(movie_name))
                    elif vote_count == 1:
                        output.append('1👍 - {0} - holds 1 vote!'.format(movie_name))
                    else: 
                        output.append('{1}👍 - {0} - holds {1} votes!!'.format(movie_name, vote_count))
                else:
                    vetoed_movies[key] = proposed_movies[key]

            if len(vetoed_movies) > 0:
                output.append('>>>-------------------- HONOURABLE MENTIONS --------------------<<<')
                poop_phrases = ['has been 💩 upon!', 
                'ate a 💩 sandwich!', 
                "got the ol' 💩 n' scoop!", 
                'is covered in 💩!', 
                'stepped in a big pile of 💩!', 
                'is also full of 💩!', 
                'got the 💩!', 
                'got soft-served 💩!', 
                'got flung into 💩!', 
                'got got 💩!', 
                'got stanked 💩!']
                
                sorted_vetoed_proposals = {}
                for key in vetoed_movies:
                    sorted_vetoed_proposals[key] = vetoed_movies[key].votes

                sorted_vetoed_proposals = sorted(sorted_vetoed_proposals.items(), key=lambda x: x[1], reverse=True)

                for obj in sorted_vetoed_proposals:
                    key = obj[0]
                    movie_name = proposed_movies[key].movie_name
                    vote_count = proposed_movies[key].votes
                    poop_phrase_index = random.randrange(len(poop_phrases))
                    poop_phrase = poop_phrases[poop_phrase_index]
                    if vote_count == 0:
                        output.append('💩{}👍 - {} - has received no votes and {}!'.format(vote_count, movie_name, poop_phrase))
                    elif vote_count == 1:
                        output.append('💩{}👍 - {} - holds 1 vote, but {}!'.format(vote_count, movie_name, poop_phrase))
                    else:
                        output.append('💩{1}👍 - {0} - holds {1} votes, but {2}!'.format(movie_name, vote_count, poop_phrase))
                    
            output.append('>>>---------------------------------------------------------------------------<<<')
            separator = '\n'
            await general_channel.send(separator.join(output))

@bot.event
async def on_reaction_add(reaction, user):
    await checkReactions(reaction.message, user)
    
@bot.event
async def on_reaction_remove(reaction, user):
    await checkReactions(reaction.message, user)

    
# Run the bot and init channels
bot.run(TOKEN)