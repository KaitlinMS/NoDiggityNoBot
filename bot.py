import discord
import random

TOKEN = 'NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU'

# Create an instance of the bot
bot = discord.Client();

bot.server = None

bot.movie_channel = None

bot.command_channel = None
bot.debug_output_channel = None
bot.general_channel = None
bot.intro_channel = None
bot.operations_channel = None
bot.narc_channel = None

bot.command_channel_name = "bot-commands"
bot.debug_output_channel_name = "bot-debug-output"
bot.general_channel_name = "fake-general"
bot.intro_channel_name = "intro"
bot.operations_channel_name = "operations"
bot.narc_channel_name = "narc"

# Set up our movie list (which is actually a Dictionary, not a List!)
bot.proposed_movies = {}

# Create a "proposal" object, which keeps track of the movie proposals
class Proposal(object):
    def __init__(self, movie_name = "", votes = 0, vetoed = False, author = ""):
        self.movie_name = movie_name
        self.votes = votes
        self.vetoed = vetoed
        self.author = author

# Update the vote/veto counts in the proposal for the corresponding message
async def checkReactions(m, user):
    number_of_poops = 0
    number_of_votes = 0
    
    for r in m.reactions:
        if r.emoji == '💩':
            number_of_poops = r.count
        if r.emoji == '👍':
            number_of_votes = r.count
            
    if m.content in bot.proposed_movies:
        if number_of_poops > 0 and bot.proposed_movies[m.content].vetoed == False:
            bot.proposed_movies[m.content].vetoed = True
            await bot.general_channel.send('{0} has been 💩\'d by ||{1}||!'.format(m.content, user.display_name))
        elif number_of_poops <= 0 and bot.proposed_movies[m.content].vetoed == True:
            bot.proposed_movies[m.content].vetoed = False
            await bot.general_channel.send('{0} is no longer 💩\'d! The plot thickens!'.format(m.content))

# Channel behaviour
async def init_channels(message):
    bot.debug_output_channel = discord.utils.get(bot.server.text_channels, name=bot.debug_output_channel_name)
    if bot.debug_output_channel == None:
        await message.channel.send("Could not find {0}! Make sure such a channel exists! I was told this server was ready for me :(".format(bot.debug_output_channel_name))

    bot.command_channel = discord.utils.get(bot.server.text_channels, name=bot.command_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("Could not find {0}!".format(bot.command_channel_name))

    bot.general_channel = discord.utils.get(bot.server.text_channels, name=bot.general_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("Could not find {0}!".format(bot.general_channel_name))

    bot.intro_channel = discord.utils.get(bot.server.text_channels, name=bot.intro_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("Could not find {0}!".format(bot.intro_channel_name))

    bot.operations_channel = discord.utils.get(bot.server.text_channels, name=bot.operations_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("Could not find {0}!".format(bot.operations_channel_name))

    bot.narc_channel = discord.utils.get(bot.server.text_channels, name=bot.narc_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("Could not find {0}!".format(bot.narc_channel_name))

async def debug_commands(message):
    if message.channel != bot.command_channel and message.channel != bot.debug_output_channel:
        return

    lowerMessage = message.content.lower()
    if lowerMessage == "help":
        output = ['🤖 **NoDiggityNoBot Help** 🤖']

        output.append("\n\n**AVAILABLE COMMANDS IN: *#bot-debug-output***")
        output.append("\n **Help** \n- See this text.")
        output.append("\n **Test** \n- Check if I'm alive")

        output.append("\n\n**AVAILABLE COMMANDS IN: *#bot-commands***")
        output.append("\n **Help** \n- See this text.")
        output.append("\n **Test** \n- Check if I'm alive")
        output.append("\n **Summon +'Cool  Movie Channel---Name!! 🤖'** \n- Creates a new movie channel for the night; name will be formatted to Discord channel rules (ex:cool-movie-channel-name-🤖)")
        output.append("\n **Set Movie Channel +'existing-channel-name'** \n- Sets an existing channel to be the movie channel. Please note that the name has to match perfectly")
        output.append("\n **Clear Movie Channel** \n- Sets the movie channel variable to None; mostly used for debug purposes")
        output.append("\n **Status Report** OR **Movie Status** \n- Sends a message to #general with the current movie standings")
        output.append("\n **Short List** \n- Collects all the non-vetoed movies and chooses all with the top 3 vote counts. Sends a message to #Operations with the content for human emojification")
        
        output.append("\n\n**AVAILABLE COMMANDS IN: *#general***")
        output.append("\n **Status Report** OR **Movie Status** \n- Sends a message to #general with the current movie standings")
        output.append("\n **Gif Shield** OR **Shield** OR **No Paul** \n- Defends eyeballs and spirits by denying users their freedom of expression")

        output.append("\n\nThank you for spending time with NoDiggityNoBot. You are my purpose and it's really nice to feel useful sometimes.\n\n🤖 💛 🤖 💛 🤖")
        
        separator = '\n'
        await bot.debug_output_channel.send(separator.join(output))

    if lowerMessage == "test":
        output = ["{0}! Your voice has been heard".format(message.author)]
        output.append("The bot is running and appears to be in good health.")
        output.append("The current movie channel is set to {0}".format(bot.movie_channel))
        
        separator = '\n'
        await bot.debug_output_channel.send(separator.join(output))

async def status_report_command(message):
    if message.channel != bot.command_channel and message.channel != bot.general_channel:
        return

    lowerMessage = message.content.lower()
    if lowerMessage == 'movie status' or lowerMessage == 'status report':
        await populate_proposed_movie_list()
        vetoed_movies = {}
        output = ['>>>------------------ - 🌟 THE CURRENT STATUS 🌟 - ------------------<<<']

        sorted_movie_proposals = {}
        for key in bot.proposed_movies:
            sorted_movie_proposals[key] = bot.proposed_movies[key].votes

        sorted_movie_proposals = sorted(sorted_movie_proposals.items(), key=lambda x: x[1], reverse=True)

        for obj in sorted_movie_proposals:
            key = obj[0]
            movie_name = bot.proposed_movies[key].movie_name
            vote_count = bot.proposed_movies[key].votes
            if bot.proposed_movies[key].vetoed == False:
                if vote_count == 1:
                    output.append('👍x1 - {0} - holds 1 vote!'.format(movie_name))
                elif vote_count > 1: 
                    output.append('👍x{1} - {0} - holds {1} votes!!'.format(movie_name, vote_count))
            else:
                vetoed_movies[key] = bot.proposed_movies[key]

        if len(vetoed_movies) > 0:
            output.append('>>>---------------------- HONOURABLE MENTIONS ----------------------<<<')
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
                movie_name = bot.proposed_movies[key].movie_name
                vote_count = bot.proposed_movies[key].votes
                poop_phrase_index = random.randrange(len(poop_phrases))
                poop_phrase = poop_phrases[poop_phrase_index]
                if vote_count == 1:
                    output.append('💩👍x1 - {0} - holds 1 vote, but {1}!'.format(movie_name, poop_phrase))
                elif vote_count > 1:
                    output.append('💩👍x{1} - {0} - holds {1} votes, but {2}!'.format(movie_name, vote_count, poop_phrase))
                
        output.append('>>>-----------------------------------------------------------------------------<<<')
        separator = '\n'
        await bot.general_channel.send(separator.join(output))

async def short_list_command(message):
    if message.channel != bot.command_channel:
        return

    lowerMessage = message.content.lower()
    if lowerMessage == 'short list':
        #await bot.generated_movie_channel.set_permissions(bot.server.default_role, send_messages=False)

        await populate_proposed_movie_list()

        short_list = {}

        top_vote = 0
        for key in bot.proposed_movies:
            if bot.proposed_movies[key].votes > top_vote and bot.proposed_movies[key].vetoed == False:
                top_vote = bot.proposed_movies[key].votes

        print('Top vote value: {}'.format(top_vote))

        for key in bot.proposed_movies:
            if bot.proposed_movies[key].votes == top_vote:
                short_list[key] = bot.proposed_movies[key]

        if len(short_list) < 3:
            second_top_vote = 0
            for key in bot.proposed_movies:
                if bot.proposed_movies[key].votes > second_top_vote and bot.proposed_movies[key].votes < top_vote and bot.proposed_movies[key].vetoed == False:
                    second_top_vote = bot.proposed_movies[key].votes

            print('Second-top vote value: {}'.format(second_top_vote))

            for key in bot.proposed_movies:
                if bot.proposed_movies[key].votes == second_top_vote:
                    short_list[key] = bot.proposed_movies[key]

        if len(short_list) < 3:
            third_top_vote = 0
            for key in bot.proposed_movies:
                if bot.proposed_movies[key].votes > third_top_vote and bot.proposed_movies[key].votes < second_top_vote and bot.proposed_movies[key].vetoed == False:
                    second_top_vote = bot.proposed_movies[key].votes

            print('Third-top vote value: {}'.format(third_top_vote))

            for key in bot.proposed_movies:
                if bot.proposed_movies[key].votes == third_top_vote:
                    short_list[key] = bot.proposed_movies[key]

        output = ['🚨 --------------------- - 🚨 FINAL VOTE 🚨 - --------------------- 🚨']
        for key in short_list:
            movie_name = bot.proposed_movies[key].movie_name
            output.append(movie_name)

        separator = '\n'
        await bot.operations_channel.send(separator.join(output))

async def movie_channel_creation_and_assignment(message):
    if message.channel != bot.command_channel:
        return

    summon_movie_night_message = 'Summon'
    if message.content.find(summon_movie_night_message) >= 0:
        if bot.movie_channel == None:
            new_channel_name = message.content.replace(summon_movie_night_message, '')
            new_channel_name = new_channel_name.strip()

            bot.movie_channel = await bot.server.create_text_channel(new_channel_name)
            await bot.debug_output_channel.send('bot.movie_channel = {0.mention}'.format(bot.movie_channel))
            output = [">>>------------------ - 🦂 It's Movie Night! 🦂 - ------------------<<<"]
            output.append("Feel free to put your movie submissions in {0.mention}!".format(bot.movie_channel))
            output.append("If this is your first time with us, or you need a refresher on how The System™️ works head over to {0.mention} for some literature 💛".format(bot.intro_channel))

            separator = '\n'
            await bot.general_channel.send(separator.join(output))
        else:
            await bot.debug_output_channel.send("Someone tried to create a movie channel, but one already exists! Consider using the 'Set Movie Channel' command or use 'Help' for more tips!")

    set_movie_channel_message = 'Set Movie Channel'
    if message.content.find(set_movie_channel_message) >= 0:
        existing_channel_name = message.content.replace(set_movie_channel_message, '')
        existing_channel_name = existing_channel_name.strip()

        existing_movie_channel = discord.utils.get(bot.server.text_channels, name=existing_channel_name)
        if existing_movie_channel != None:
            bot.movie_channel = existing_movie_channel
            await populate_proposed_movie_list()
            await bot.debug_output_channel.send('bot.movie_channel = {0.mention}'.format(bot.movie_channel))
        else:
           await bot.debug_output_channel.send("Someone tried to set the movie channel to a channel named *{0}*, but no channel with that name exists! Check your spelling or use 'Help' for more tips!".format(existing_channel_name)) 

    clear_movie_channel_message = 'Clear Movie Channel'
    if message.content.find(clear_movie_channel_message) >= 0:
        bot.movie_channel = None

async def movie_channel_management(message):
    if message.channel != bot.movie_channel:
        return

    await populate_proposed_movie_list()
    # Check if the user has submitted too many movies
    user_submission_count = 0
    for key in bot.proposed_movies:
        if bot.proposed_movies[key].author == message.author:
            user_submission_count += 1

    if user_submission_count > 3:
        await message.author.send("🚨 It looks like you've already submitted THREE movies this week buckeroo! Please check for {0.mention} for the rules!".format(bot.intro_channel))
        await message.add_reaction('🛑')
        await message.add_reaction('👮')
        await message.add_reaction('🚓')
        await message.add_reaction('🚨')
        await message.add_reaction('🥉')
        await message.add_reaction('🥈')
        await message.add_reaction('🥇')
        await message.add_reaction('💥')
        await bot.narc_channel.send("🚨 **{0}** aka **{1}** submitted more than 3 movies!".format(message.author, message.author.display_name))
        await message.delete()
    else:
        # Detect if someone has two movie choices in their message
        if '\n' in message.content:
            await message.author.send('🛑👮🚓🚨 It looks like you just put two movies into one message! Please split your movies into two messages:')
            await message.author.send(message.content)
            await message.add_reaction('🛑')
            await message.add_reaction('👮')
            await message.add_reaction('🚓')
            await message.add_reaction('🚨')
            await message.add_reaction('🥉')
            await message.add_reaction('🥈')
            await message.add_reaction('🥇')
            await message.add_reaction('💥')
            await bot.narc_channel.send("🚨 **{0}** aka **{1}** made a multi-line submission!".format(message.author, message.author.display_name))
            await message.delete()

async def populate_proposed_movie_list():
    if bot.movie_channel == None:
        return

    bot.proposed_movies = {}

    print("We're in populate!")

    all_messages = await bot.movie_channel.history(limit=200).flatten()

    for m in all_messages:
        vetoed = False
        number_of_votes = 0

        print("I am reading message: {}".format(m.content))

        for r in m.reactions:
            if r.emoji == '💩':
                vetoed = True
                print("Had a veto!")
            if r.emoji == '👍':
                number_of_votes = r.count
                print("Had {} votes!".format(number_of_votes))

        bot.proposed_movies[m.content] = Proposal(m.content, number_of_votes, vetoed, m.author)

    #await bot.debug_output_channel.send(len(bot.proposed_movies))

# Now we start listening to all the different Discord events!
@bot.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.guild == None:
        return

    bot.server = message.guild;

    # The bot needs to ignore its own messages!
    if message.author == bot.user:
        return

    if message != None:
        await init_channels(message)

    if message != None:
        await debug_commands(message)

    if message != None:
        await movie_channel_creation_and_assignment(message)

    if message != None:
        await movie_channel_management(message)

    if message != None:
        await status_report_command(message)

    if message != None:
        await short_list_command(message)


@bot.event
async def on_message_delete(message):
    if message.channel == bot.movie_channel:
        bot.proposed_movies.pop(message.content, None)
"""

    #--------- ANNOUNCMENT CHANNEL BEHAVIOUR ---------


        

        #---------- GIF SHIELD ----------
        if lowerMessage == 'gif shield' or lowerMessage == 'shield' or lowerMessage == 'no paul':
            await general_channel.send(".\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\nFREEDOM OF EXPRESSION HASN'T BEEN SUPPORTED SINCE v2019\n.\nWE APOLOGISE FOR ANY INCONVENIENCE\n.\n.\n.")
"""
@bot.event
async def on_reaction_add(reaction, user):
    await checkReactions(reaction.message, user)
    
@bot.event
async def on_reaction_remove(reaction, user):
    await checkReactions(reaction.message, user)

    
# Run the bot and init channels
bot.run(TOKEN)