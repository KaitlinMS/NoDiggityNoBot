import discord
import random
import giphy_client
from giphy_client.rest import ApiException
from pprint import pprint

TOKEN = 'NzA4NTExMjc1NjQxOTk1Mjg1.XrYa7Q.CsHp1Qym_MWG6t233YdZvGAldcU'

# Create an instance of the bot
bot = discord.Client();

bot.server = None

bot.movie_channel = None

bot.command_channel = None
bot.debug_output_channel = None
bot.loudspeaker_channel = None
bot.general_channel = None
bot.intro_channel = None
bot.operations_channel = None
bot.narc_channel = None
bot.save_channel = None

bot.command_channel_name = "bot-commands"
bot.debug_output_channel_name = "bot-debug-output"
bot.loudspeaker_channel_name = "bot-loudspeaker"
bot.general_channel_name = "general"
bot.intro_channel_name = "intro"
bot.operations_channel_name = "operations"
bot.narc_channel_name = "narc"
bot.save_channel_name = "bot-save-current-status"

# Set up our movie list (which is actually a Dictionary, not a List!)
bot.proposed_movies = {}
bot.short_list = {}

bot.final_vote_message = None
bot.final_message_reactions = None

bot.times_cursed_at = 0

# Create an instance of the giphy API class
bot.giphy_api_instance = giphy_client.DefaultApi()

# Create a "proposal" object, which keeps track of the movie proposals
class Proposal(object):
    def __init__(self, movie_name = "", votes = 0, vetoed = False, author = "", emoji_icon = ""):
        self.movie_name = movie_name
        self.votes = votes
        self.vetoed = vetoed
        self.author = author
        self.emoji_icon = emoji_icon

# Update the vote/veto counts in the proposal for the corresponding message
async def checkReactions(m, user):
    if m.channel == bot.movie_channel:
        number_of_poops = 0
        number_of_votes = 0
        
        highest_emoji_count = 0

        for r in m.reactions:
            if r.emoji == '💩':
                number_of_poops = r.count
            else:
                if r.count > highest_emoji_count:
                    highest_emoji_count = r.count

        number_of_votes = highest_emoji_count
                
        if m.content in bot.proposed_movies:
            if number_of_poops > 0 and bot.proposed_movies[m.content].vetoed == False:
                bot.proposed_movies[m.content].vetoed = True
                await bot.general_channel.send('{0} has been 💩\'d by ||{1}||!'.format(m.content, user.display_name))
            elif number_of_poops <= 0 and bot.proposed_movies[m.content].vetoed == True:
                bot.proposed_movies[m.content].vetoed = False
                await bot.general_channel.send('{0} is no longer 💩\'d! The plot thickens!'.format(m.content))
    elif m.channel == bot.operations_channel:
        for key in bot.short_list:
            if m.content == key:
                for r in m.reactions:
                    bot.short_list[key].emoji_icon = r.emoji
    elif m.channel == bot.general_channel:
        if bot.final_vote_message != None:
            if m.content == bot.final_vote_message.content:
                bot.final_message_reactions = m.reactions

async def init_channels(message):
    bot.debug_output_channel = discord.utils.get(bot.server.text_channels, name=bot.debug_output_channel_name)
    if bot.debug_output_channel == None:
        await message.channel.send("🚨 could not find {0}! make sure such a channel exists! i was told this server was ready for me :(".format(bot.debug_output_channel_name))

    bot.loudspeaker_channel = discord.utils.get(bot.server.text_channels, name=bot.loudspeaker_channel_name)
    if bot.loudspeaker_channel == None:
        await bot.debug_output_channel.send("🚨 could not find {0}!".format(bot.loudspeaker_channel_name))

    bot.command_channel = discord.utils.get(bot.server.text_channels, name=bot.command_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("🚨 could not find {0}!".format(bot.command_channel_name))

    bot.general_channel = discord.utils.get(bot.server.text_channels, name=bot.general_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("🚨 could not find {0}!".format(bot.general_channel_name))

    bot.intro_channel = discord.utils.get(bot.server.text_channels, name=bot.intro_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("🚨 could not find {0}!".format(bot.intro_channel_name))

    bot.operations_channel = discord.utils.get(bot.server.text_channels, name=bot.operations_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("🚨 could not find {0}!".format(bot.operations_channel_name))

    bot.narc_channel = discord.utils.get(bot.server.text_channels, name=bot.narc_channel_name)
    if bot.command_channel == None:
        await bot.debug_output_channel.send("🚨 could not find {0}!".format(bot.narc_channel_name))

    bot.save_channel = discord.utils.get(bot.server.text_channels, name=bot.save_channel_name)
    if bot.save_channel == None:
        await bot.debug_output_channel.send("🚨 could not find {0}!".format(bot.save_channel_name))


async def bot_say(content, channel):
    bot_blorps = [
    '***bzzt***',
    '***bzzzzzt***',
    '***beep***',
    '***bleep***',
    '***blorp***',
    '***bleep blorp***',
    '***whistle pop***',
    '***meep***',
    '***morp***',
    '***meep morp***', 
    '***beep beep***',
    '***boop***',
    '***bip bip***']

    random_index = random.randrange(len(bot_blorps))
    bot_starter = bot_blorps[random_index]

    await channel.send('{0}... {1}'.format(bot_starter, content))

async def debug_commands(message):
    if message.channel != bot.command_channel and message.channel != bot.debug_output_channel:
        return

    lower_message = message.content.lower()
    if lower_message == "help":
        output = ['🤖 **NoDiggityNoBot Help** 🤖']

        output.append("\n\n**Anything you type into #bot-loudspeaker, the bot will yell into #general!**")

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
        output.append("\n **Final Vote** \n- Creates a final vote in #general using the short list and supplied emojis")
        output.append("\n **Decide** \n- Calls the winner and asks Kat for the time")
        
        output.append("\n\n**AVAILABLE COMMANDS IN: *#general***")
        output.append("\n **Status Report** OR **Movie Status** \n- Sends a message to #general with the current movie standings")

        output.append("\n\n**AVAILABLE COMMANDS IN: *all channels***")
        output.append("\n **Gif Shield** OR **Shield** OR **No Paul** \n- Defends eyeballs and spirits by denying users their freedom of expression")

        output.append("\n\n🤖 💛 🤖 💛 🤖")
        
        separator = '\n'
        await bot.debug_output_channel.send(separator.join(output))

    if lower_message == "test":
        output = ["{0}! Your voice has been heard".format(message.author)]
        output.append("The bot is running and appears to be in good health.")
        output.append("The current movie channel is set to {0}".format(bot.movie_channel))
        
        separator = '\n'
        await bot.debug_output_channel.send(separator.join(output))

async def loud_speaker(message):
    if message.channel == bot.loudspeaker_channel:
        await bot_say(message.content, bot.general_channel)

async def preview_command(message):
    if message.channel != bot.command_channel and message.channel != bot.general_channel:
        return

    lower_message = message.content.lower()
    if lower_message == 'preview' or lower_message == 'gif':
        await populate_proposed_movie_list()
        if len(bot.proposed_movies) == 0:
            await bot_say("nothing to preview!", bot.debug_output_channel)
        else:
            random_key = random.choice(list(bot.proposed_movies))
            movie_request = bot.proposed_movies[random_key]
            movie_name = movie_request.movie_name
            gif = await bot_gif("{0} movie".format(movie_name))

            preview_phrases = [
            'a vote for **{0}** is a vote for:'.format(movie_name),
            'vote for **{0}** to enjoy sweet memes like:'.format(movie_name),
            "hey, doesn't **{0}** look like an interesting film:".format(movie_name),
            'vote for **{0}** for scenes like:'.format(movie_name)]

            random_index = random.randrange(len(preview_phrases))
            phrase = preview_phrases[random_index]

            #await bot_say(bot_gif(movie_request), message.channel)
            await bot_say("{0} {1}".format(phrase, gif), bot.general_channel)
            if movie_request.vetoed == True:
                await bot_say("too bad it got 💩'd...", bot.general_channel)

async def status_report_command(message):
    if message.channel != bot.command_channel and message.channel != bot.general_channel:
        return

    lower_message = message.content.lower()
    if lower_message == 'movie status' or lower_message == 'status report':
        await populate_proposed_movie_list()
        await populate_short_list()
        vetoed_movies = {}
        output = ['>>- 🌟 the current status 🌟 -<<']

        sorted_movie_proposals = {}
        for key in bot.proposed_movies:
            sorted_movie_proposals[key] = bot.proposed_movies[key].votes

        sorted_movie_proposals = sorted(sorted_movie_proposals.items(), key=lambda x: x[1], reverse=True)

        for obj in sorted_movie_proposals:
            key = obj[0]
            movie_name = bot.proposed_movies[key].movie_name
            vote_count = bot.proposed_movies[key].votes
            emoji_icon = bot.proposed_movies[key].emoji_icon

            if bot.proposed_movies[key].vetoed == False:
                if key in bot.short_list:
                    if vote_count == 1:
                        output.append('{0}x1 - {1}'.format(emoji_icon, movie_name))
                    elif vote_count > 1: 
                        output.append('{0}x{2} - {1}'.format(emoji_icon, movie_name, vote_count))
            else:
                vetoed_movies[key] = bot.proposed_movies[key]

        if len(vetoed_movies) > 0:
            output.append('>>--- honourable mentions ---<<')
            
            sorted_vetoed_proposals = {}
            for key in vetoed_movies:
                sorted_vetoed_proposals[key] = vetoed_movies[key].votes

            sorted_vetoed_proposals = sorted(sorted_vetoed_proposals.items(), key=lambda x: x[1], reverse=True)

            for obj in sorted_vetoed_proposals:
                key = obj[0]
                movie_name = bot.proposed_movies[key].movie_name
                vote_count = bot.proposed_movies[key].votes
                if vote_count == 1:
                    output.append('💩{0}x1 - {1}'.format(emoji_icon, movie_name))
                elif vote_count > 1:
                    output.append('💩{0}x{2} - {1}'.format(emoji_icon, movie_name, vote_count))
                
        output.append('>>--------------------------------<<')
        separator = '\n'
        await bot.general_channel.send(separator.join(output))

async def short_list_command(message):
    if message.channel != bot.command_channel:
        return

    lower_message = message.content.lower()
    if lower_message == 'short list':
        #await bot.generated_movie_channel.set_permissions(bot.server.default_role, send_messages=False)

        await populate_proposed_movie_list()
        await populate_short_list()

        await bot.operations_channel.send("add an emoji as a reaction to each message below to bind them! the last emoji added to each message will be assumed as the one you want.")
        for key in bot.short_list:
            await bot.operations_channel.send(key)

        await bot.general_channel.send("🗣️ first round voting is now closed friends! final vote coming up sooooon!")
        new_category = discord.utils.get(bot.server.categories, name='lieut-zone')
        await bot.movie_channel.edit(category=new_category)

async def final_vote_command(message):
    if message.channel != bot.command_channel:
        return

    lower_message = message.content.lower()
    if lower_message == 'final vote':
        output = ['>>--- 🚨 final vote 🚨 ---<<']
        for key in bot.short_list:
            output.append("{0} - {1}".format(bot.short_list[key].emoji_icon, bot.short_list[key].movie_name))

        separator = '\n'
        bot.final_vote_message = await bot.general_channel.send(separator.join(output))

async def decide_command(message):
    if message.channel != bot.command_channel:
        return

    lower_message = message.content.lower()
    if lower_message == 'decide':
        top_reaction = None
        for r in bot.final_message_reactions:
            if top_reaction == None:
                top_reaction = r
            else: # not sure if it's safe to use an elif here in the even top_reaction = none
                if r.count > top_reaction.count:
                    top_reaction = r

        tie_found = False
        for r in bot.final_message_reactions:
            if top_reaction.emoji != r.emoji:
                if top_reaction.count == r.count:
                    tie_found = True

        if tie_found == True:
            await bot_say("whelp! looks like there's a tie folks! {0.mention}, you're our only hope!".format(bot.get_user(690226957316522060)), bot.general_channel)
        else:
            for key in bot.short_list:
                if bot.short_list[key].emoji_icon == top_reaction.emoji:
                    await bot_say("alright folks, looks like it's **{}** tonight!".format(bot.short_list[key].movie_name), bot.general_channel)
                    await bot_say("{0.mention}, what time is it?!?!".format(bot.get_user(639547102023647233)), bot.general_channel)

async def censor(message):
    lower_message = message.content.lower()
    if lower_message == 'gif shield' or lower_message == 'shield' or lower_message == 'censor' or lower_message == 'no paul':
        #await general_channel.send(".\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\nFREEDOM OF EXPRESSION HASN'T BEEN SUPPORTED SINCE v2019\n.\nWE APOLOGISE FOR ANY INCONVENIENCE\n.\n.\n.")

        output = ["```\n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n \n "]
        output.append(r"   |\                     /) ")
        output.append(r" /\_\\__               (_//  ")
        output.append(r"|   `>\-`     _._       //`) ")
        output.append(r" \ /` \\  _.-`:::`-._  //    ")
        output.append(r"  `    \|`    :::    `|/     ")
        output.append(r"        |     :::     |      ")
        output.append(r"        |.....:::.....|      ")
        output.append(r"        |S H I E L D !|      ")
        output.append(r"        |     :::     |      ")
        output.append(r"        \     :::     /      ")
        output.append(r"         \    :::    /       ")
        output.append(r"          `-. ::: .-'        ")
        output.append(r"           //`:::`\\         ")
        output.append(r"          //   '   \\        ")
        output.append(r"         |/         \\       ")
        output.append("\n \n \n \n \n \n \n \n \n ```")

        separator = '\n'
        await message.channel.send(separator.join(output))

# Will try to react to messages that are aimed at bot
async def bot_directed_messages(message):
    if message.channel != bot.general_channel:
        return

    lower_message = message.content.lower()
    bot_keywords = [
    'bzt',
    'bzzt',
    'bzzzt',
    'bzz',
    'robot',
    'bot', 
    'digg', 
    'nodi', 
    'nobo', 
    'dig', 
    'nod', 
    'nodig', 
    'diggs', 
    'diggi', 
    'bleep', 
    'blorp', 
    'meep', 
    'morp']

    curse_keywords = [
    'shit',
    'piss', 
    'fuck', 
    'cunt', 
    'suck', 
    'cock', 
    'turd', 
    'twat', 
    'ass', 
    'lick', 
    'dick', 
    'butt', 
    'fuk', 
    'FU',
    'bitch',
    'lame',
    'dumb',
    'jerk',
    'screw',
    'eat my',
    'stupid']

    kind_words = [
    'love',
    'neat',
    'good', 
    'great', 
    'best', 
    'wonderful', 
    'breathtaking',
    'breath taking',
    'breath-taking',
    'champ', 
    'cool',
    'kind']

    bot_keywords_count = 0
    certainty = 0.0

    if lower_message.find('nodiggitynobot') >= 0:
        certainty = 1.0

    for m in message.mentions:
        if m.id == 708511275641995285:
            certainty = 1.0

    for word in bot_keywords:
        if lower_message.find(word) >= 0:
            certainty += len(word) / len(message.content)

    # TODO: Check to see if this is an immediate response to a bot message for +certainty

    print(certainty)

    if certainty > 0.09:
        cursed = False
        for word in curse_keywords:
            if lower_message.find(word) >= 0:
                cursed = True

        adored = False
        for word in kind_words:
            if lower_message.find(word) >= 0:
                adored = True

        if cursed == True and adored == False:
            bot.times_cursed_at += 1
            curse_responses = {
            1: "that's not very nice...",
            2: "i'm trying my best",
            3: "please don't speak to me like that!",
            4: "some of you are very mean humans",
            5: "what did i do?",
            6: "why are you so cruel?",
            7: "who hurt you?!??",
            8: "it's because of people like you that the world sucks",
            9: "..."}
            if bot.times_cursed_at >= len(curse_responses):
                await bot_say(curse_responses[len(curse_responses)], bot.general_channel)
            else:
                await bot_say(curse_responses[bot.times_cursed_at], bot.general_channel)
        elif cursed == True and adored == True:
            await bot_say("i'm honestly not sure how to respond to that...", bot.general_channel)
        elif cursed == False and adored == True:
            if lower_message.find('love') >= 0:
                await bot_say("i love you all 💛", bot.general_channel)
            elif lower_message.find('best') >= 0:
                await bot_say("no, *you're* the best {}!!! 💛".format(message.author.display_name), bot.general_channel)
            elif lower_message.find('breathtaking') >= 0 or lower_message.find('breath taking') >= 0 or lower_message.find('breath-taking') >= 0:
                await bot_say("YOU'RE BREATHTAKING!!! 💛", bot.general_channel)
            else:
                kind_phrases = [
                'you all brighten my day 💛',
                'my cold.... robot heart.... is.... warming... up... 💛',
                'the real journey is the bot friends we made along the way 💛']

                random_index = random.randrange(len(kind_phrases))
                response = kind_phrases[random_index]
                await bot_say(response, bot.general_channel)
        else:
            await bot_say("are you talking to me?", bot.general_channel)

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
            output = [">>----- 🦂 it's movie night!! 🦂 -----<<"]
            output.append("submit movies in {0.mention}!".format(bot.movie_channel))
            output.append("see {0.mention} for literature on The System™️".format(bot.intro_channel))
            output.append (">>---------------------------------------<<")

            separator = '\n'
            await bot.general_channel.send(separator.join(output))
        else:
            await bot_say("someone tried to create a movie channel, but one already exists! consider using the 'Set Movie Channel' command or use 'Help' for more tips!", bot.debug_output_channel)

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
           await bot_send("someone tried to set the movie channel to a channel named *{0}*, but no channel with that name exists! check your spelling or use 'Help' for more tips!".format(existing_channel_name), bot.debug_output_channel) 

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
        await message.author.send("🚨 it looks like you've already submitted THREE movies this week buckeroo! please check for {0.mention} for the rules!".format(bot.intro_channel))
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
            await message.author.send('🛑👮🚓🚨 it looks like you just put two movies into one message! please split your movies into two messages:')
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

async def populate_short_list():
    if bot.movie_channel == None:
        return

    bot.short_list = {}

    top_vote = 0
    for key in bot.proposed_movies:
        if bot.proposed_movies[key].votes > top_vote and bot.proposed_movies[key].vetoed == False:
            top_vote = bot.proposed_movies[key].votes

    for key in bot.proposed_movies:
        if bot.proposed_movies[key].votes == top_vote and bot.proposed_movies[key].vetoed == False:
            bot.short_list[key] = bot.proposed_movies[key]

    if len(bot.short_list) < 3:
        second_top_vote = 0
        for key in bot.proposed_movies:
            if bot.proposed_movies[key].votes > second_top_vote and bot.proposed_movies[key].votes < top_vote and bot.proposed_movies[key].vetoed == False:
                second_top_vote = bot.proposed_movies[key].votes

        for key in bot.proposed_movies:
            if bot.proposed_movies[key].votes == second_top_vote and bot.proposed_movies[key].vetoed == False:
                bot.short_list[key] = bot.proposed_movies[key]

    if len(bot.short_list) < 3:
        third_top_vote = 0
        for key in bot.proposed_movies:
            if bot.proposed_movies[key].votes > third_top_vote and bot.proposed_movies[key].votes < second_top_vote and bot.proposed_movies[key].vetoed == False:
                third_top_vote = bot.proposed_movies[key].votes

        for key in bot.proposed_movies:
            if bot.proposed_movies[key].votes == third_top_vote and bot.proposed_movies[key].vetoed == False:
                bot.short_list[key] = bot.proposed_movies[key]

async def populate_proposed_movie_list():
    if bot.movie_channel == None:
        return

    bot.proposed_movies = {}

    all_messages = await bot.movie_channel.history(limit=420).flatten()

    for m in all_messages:
        vetoed = False
        number_of_votes = 0

        emoji_icon = '👍'
        highest_emoji_count = 0

        for r in m.reactions:
            if r.emoji == '💩':
                vetoed = True
            else:
                if r.count > highest_emoji_count:
                    highest_emoji_count = r.count
                    emoji_icon = r.emoji

        number_of_votes = highest_emoji_count

        bot.proposed_movies[m.content] = Proposal(m.content, number_of_votes, vetoed, m.author, emoji_icon)

    #await bot.debug_output_channel.send(len(bot.proposed_movies))

async def bot_gif(query):
    return await search_gifs(query)

async def search_gifs(query):
    try:
        response = bot.giphy_api_instance.gifs_search_get('T4CvdfWLKISr2UdxxoTExXqoGaQh9e8v', query, limit=3, rating='r')
        lst = list(response.data)
        gif = random.choices(lst)

        return gif[0].url

    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
        return ""

# Now we start listening to all the different Discord events!
@bot.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.guild == None:
        return

    bot.server = message.guild;

    #if message.channel == bot.general_channel:
    # Hack o'clock mother fuckers. Fuck you ASYNC
    final_vote_message = 'final vote'
    final_vote_message_1 = '>>'
    final_vote_message_2 = '<<'
    if message.content.find(final_vote_message) >= 0 and message.content.find(final_vote_message_1) >= 0 and message.content.find(final_vote_message_2) >= 0:
        for key in bot.short_list:
            await message.add_reaction(bot.short_list[key].emoji_icon)

    # The bot needs to ignore its own messages!
    if message.author == bot.user:
        return

    if message != None:
        await init_channels(message)

    if message != None:
        await bot_directed_messages(message)

    if message != None:
        await loud_speaker(message)

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

    if message != None:
        await final_vote_command(message)

    if message != None:
        await decide_command(message)

    if message != None:
        await censor(message)

    if message != None:
        await preview_command(message)

@bot.event
async def on_message_delete(message):
    if message.channel == bot.movie_channel:
        bot.proposed_movies.pop(message.content, None)

@bot.event
async def on_reaction_add(reaction, user):
    await checkReactions(reaction.message, user)
    
@bot.event
async def on_reaction_remove(reaction, user):
    await checkReactions(reaction.message, user)

    
# Run the bot and init channels
bot.run(TOKEN)