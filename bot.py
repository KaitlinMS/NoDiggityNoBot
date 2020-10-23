import os
import requests
import discord
import random
import giphy_client
import asyncio
from moviepy.editor import *
from moviepy.video.fx.all import *
from PIL import Image, ImageDraw
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

bot.preview_count = 8
bot.preview_size = 440, 187

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
async def check_reactions(m, user):
    await check_reactions_movie_channel(m, user)
    await check_reactions_operations_channel(m, user)
    await check_reactions_general_channel(m, user)
    await check_reactions_all_channels(m, user)

async def check_reactions_movie_channel(m, user):
    if m.channel != bot.movie_channel:
        return

    number_of_poops = 0
    number_of_votes = 0
    
    highest_emoji_count = 0

    for r in m.reactions:
        if r.emoji == '💩':
            number_of_poops = r.count
        elif r.count > highest_emoji_count:
            highest_emoji_count = r.count

    number_of_votes = highest_emoji_count

    if m.content in bot.proposed_movies:
        print("here") 
        if number_of_poops > 0 and bot.proposed_movies[m.content].vetoed == False:
            bot.proposed_movies[m.content].vetoed = True
            await bot.general_channel.send('{0} has been 💩\'d by ||{1}||!'.format(m.content, user.display_name))
        elif number_of_poops <= 0 and bot.proposed_movies[m.content].vetoed == True:
            bot.proposed_movies[m.content].vetoed = False
            await bot.general_channel.send('{0} is no longer 💩\'d! The plot thickens!'.format(m.content))

async def check_reactions_operations_channel(m, user):
    if m.channel != bot.operations_channel:
        return

    for key in bot.short_list:
        if m.content == key:
            for r in m.reactions:
                bot.short_list[key].emoji_icon = r.emoji

async def check_reactions_general_channel(m, user):
    if m.channel != bot.general_channel:
        return

    if bot.final_vote_message != None:
        if m.content == bot.final_vote_message.content:
            bot.final_message_reactions = m.reactions

async def check_reactions_all_channels(m, user):
    for r in m.reactions:
        if r.emoji == '🎴':
            await m.clear_reaction('🎴')
            await m.add_reaction('🤖')

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

    submissions_category = discord.utils.get(bot.server.categories, name='submissions')
    channels = submissions_category.channels
    if len(channels) > 1:
        await bot.debug_output_channel.send("🚨 found more than one movie channel in the 'submissions' category! make sure there is only one")
    #elif len(channels) == 0:
    #    await bot.debug_output_channel.send("🚨 found no channel(s) in the 'submissions' category! make sure there is one and only one")
    elif len(channels) == 1:   
        bot.movie_channel = channels[0]
        #await bot.debug_output_channel.send('bot.movie_channel = {0.mention}'.format(bot.movie_channel))

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

async def loud_speaker(message):
    if message.channel == bot.loudspeaker_channel:
        await bot_say(message.content, bot.general_channel)

async def download_preview_command(message):
    if message.channel != bot.command_channel and message.channel != bot.general_channel:
        return

    lower_message = message.content.lower()
    if lower_message == 'preview' or lower_message == 'gif':
        await populate_proposed_movie_list()
        if len(bot.proposed_movies) == 0:
            await bot_say("nothing to preview!", bot.debug_output_channel)
        else:
            max_attempts = 100
            current_attempt = 1
            downloaded_count = 0
            not_yet_previewed_movies = {}
            random_key = random.choice(list(bot.proposed_movies))
            movie_request = bot.proposed_movies[random_key]
            movie_name = movie_request.movie_name
            urls_attempted = []

            await bot_say("attempting to generate preview for {}".format(movie_name), bot.debug_output_channel)

            while current_attempt < max_attempts:
                horny_index = random.randrange(9)
                if horny_index == 5:
                    gif_url = await bot_gif("horny")
                else:
                    gif_url = await bot_gif("{0}".format(movie_name))
                split_url = gif_url.split("-")
                mod_url = 'https://media4.giphy.com/media/{}/giphy.gif'.format(split_url[len(split_url) - 1])

                if mod_url not in urls_attempted:
                    urls_attempted.append(mod_url)

                    if download(mod_url, dest_folder="PreviewGifs", filename='preview_{}.gif'.format(downloaded_count)):
                        downloaded_count += 1

                if downloaded_count >= bot.preview_count:
                    break
                current_attempt += 1

            print("exitted download function after {0} attempts".format(current_attempt))
            if current_attempt < max_attempts:
                await stitch_preview(movie_name)
            else:
                await bot_say("failed to download the required gifs for preview!")

async def stitch_preview(movie_name):
    clips = []

    def append_clip(clip):
        aspect_ratio = clip.w / clip.h
        dimensions = 1, 1
        if aspect_ratio > 2.35:
            dimensions = clip.h*2.35, clip.h
        else:
            dimensions = clip.w, clip.w/2.35

        clip = crop(clip, width=dimensions[0], height=dimensions[1], x_center=clip.w/2, y_center=clip.h/2)
        clip = clip.resize(bot.preview_size)
        clips.append(clip)

    clip_file_path = os.path.join('PreviewGifs', 'trailer_card.gif')
    clip = VideoFileClip(clip_file_path)
    append_clip(clip)

    for x in range(0, bot.preview_count):
        clip_file_path = os.path.join('PreviewGifs', 'preview_{0}.gif'.format(x))
        clip = VideoFileClip(clip_file_path)
        append_clip(clip)

    text_card_size = int(bot.preview_size[0]/5), int(bot.preview_size[1]/5) # this is a hack to make text bigger without dealing with font size
    img = Image.new('RGB', (text_card_size[0], text_card_size[1]), color=0)
    text = movie_name.upper()
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(text)
    draw.text(((text_card_size[0]-w)/2,(text_card_size[1]-h)/2), text, fill="white")

    dest_file_path = os.path.join('PreviewGifs', 'movie_name.png')
    img.save(dest_file_path)

    clip = ImageClip(dest_file_path).set_duration(4)
    append_clip(clip)

    if not os.path.exists('StitchedPreview'):
        os.makedirs('StitchedPreview') 

    dest_file_path = os.path.join('StitchedPreview', 'preview.gif')

    max_attempts = 15
    attempt = 0
    size_ratio = 1
    stitched_clip = concatenate_videoclips(clips)

    while attempt < max_attempts:
        stitched_clip = stitched_clip.resize((bot.preview_size[0] / size_ratio, bot.preview_size[1] / size_ratio))
        stitched_clip.write_gif(dest_file_path, program='ffmpeg', fps=15)
        file_size = os.stat(dest_file_path).st_size
        if file_size > 8300000:
            size_ratio = 1 + (0.1 * attempt)
            attempt += 1
        else:
            print("stiched preview generated after {0} attempts".format(attempt + 1))
            await bot_say("generated stitched preview under 8mb after {0} attempts!".format(attempt), bot.debug_output_channel)
            break

    if attempt > max_attempts:
        print("failed to create a gif under 8mb")
        await bot_say("failed to generate a gif preview under 8mb after {0} attempts".format(attempt), bot.debug_output_channel)
    else:
        await upload_preview(movie_name)            

async def upload_preview(movie_name):
    file_path = os.path.join('StitchedPreview', 'preview.gif')
    file = discord.File(file_path, filename="preview.gif")
    embed = discord.Embed()
    embed.set_image(url="attachment://preview.gif")
    if bot.proposed_movies[movie_name].vetoed == False:
        await bot.general_channel.send(content="coming soon, to a netflix movie night near you:", file=file)
    else:
        await bot.general_channel.send(content="in netflixes this fall, a film shat-on before it's time:", file=file)

async def status_report_command(message):
    if message.channel != bot.command_channel and message.channel != bot.general_channel:
        return

    lower_message = message.content.lower()
    if lower_message == 'movie status' or lower_message == 'status report' or lower_message == 'status':
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
            output.append('>>-- honourable pooptions --<<')
            
            sorted_vetoed_proposals = {}
            for key in vetoed_movies:
                sorted_vetoed_proposals[key] = vetoed_movies[key].votes

            sorted_vetoed_proposals = sorted(sorted_vetoed_proposals.items(), key=lambda x: x[1], reverse=True)

            for obj in sorted_vetoed_proposals:
                key = obj[0]
                movie_name = bot.proposed_movies[key].movie_name
                vote_count = bot.proposed_movies[key].votes
                emoji_icon = bot.proposed_movies[key].emoji_icon
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

async def matt_firsteenth(message):
    if message.channel != bot.general_channel:
        return

    lower_message = message.content.lower()
    if lower_message.find('what') >= 0 and lower_message.find('day') >= 0 and lower_message.find('what a') < 0:
        file_path = os.path.join('Gifs', 'MattFirsteenth.gif')
        file = discord.File(file_path, filename="MattFirsteenth.gif")
        embed = discord.Embed()
        embed.set_image(url="attachment://MattFirsteenth.gif")
        await bot.general_channel.send(content="same day it was yesterday; same day it's going to be tomorrow:", file=file)

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

async def coin_flip(message):
    if message.channel != bot.command_channel and message.channel != bot.general_channel:
        return

    lower_message = message.content.lower()
    if lower_message == 'coin flip' or lower_message == 'flip a coin':
        await bot.debug_output_channel.send('initiating coin flip!')

        file_path = os.path.join('CoinFlip', 'flip_start.gif')
        file = discord.File(file_path, filename="flip_start.gif")
        embed = discord.Embed()
        embed.set_image(url="attachment://flip_start.gif")
        await bot.general_channel.send(file=file)
        await asyncio.sleep(5)

        file_path = os.path.join('CoinFlip', 'flip_spin_0.gif')
        file = discord.File(file_path, filename="flip_spin_0.gif")
        embed = discord.Embed()
        embed.set_image(url="attachment://flip_spin_0.gif")
        await bot.general_channel.send(file=file)
        await asyncio.sleep(5.5)

        file_path = os.path.join('CoinFlip', 'flip_spin_1.gif')
        file = discord.File(file_path, filename="flip_spin_1.gif")
        embed = discord.Embed()
        embed.set_image(url="attachment://flip_spin_1.gif")
        await bot.general_channel.send(file=file)
        await asyncio.sleep(5.5)

        result = random.randrange(2)

        if result == 0:
            file_path = os.path.join('CoinFlip', 'flip_heads.gif')
            file = discord.File(file_path, filename="flip_heads.gif")
            embed = discord.Embed()
            embed.set_image(url="attachment://flip_heads.gif")
            await bot.general_channel.send(file=file)
        else:
            file_path = os.path.join('CoinFlip', 'flip_tails.gif')
            file = discord.File(file_path, filename="flip_tails.gif")
            embed = discord.Embed()
            embed.set_image(url="attachment://flip_tails.gif")
            await bot.general_channel.send(file=file)

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

async def alert_commands(message):
    if message.channel != bot.command_channel and message.channel != bot.general_channel:
        return

    alertStatus = ''

    lower_message = message.content.lower()
    if lower_message.find('alert') >= 0:
        if lower_message.find('blue') >= 0:
            alertStatus = 'blue'
        if lower_message.find('yellow') >= 0:
            alertStatus = 'yellow'
        if lower_message.find('red') >= 0:
            alertStatus = 'red'
        if lower_message.find('boner') >= 0:
            alertStatus = 'boner'

        if alertStatus == 'blue':
            await bot.general_channel.send('https://media2.giphy.com/media/zGmilchBguJeU/giphy.gif')
        elif alertStatus == 'yellow':
            await bot.general_channel.send('https://media4.giphy.com/media/L8yQ0RQBItqso/giphy.gif')
        elif alertStatus == 'red':
            await bot.general_channel.send('https://media4.giphy.com/media/Jpp7TR2Rv4vTizHj5g/giphy.gif')
        elif alertStatus == 'boner':
            await bot.general_channel.send('https://media3.giphy.com/media/nm53RKtqcczp6/giphy.gif')
        else:
            await bot.general_channel.send(await bot_gif(message.content))

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
    'stupid',
    'hate']

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
            await message.add_reaction('🤖')

async def movie_channel_creation_and_assignment(message):
    if message.channel != bot.command_channel:
        return

    summon_movie_night_message = 'Summon'
    if message.content.find('Summon') >= 0 or message.content.find('summon')>= 0 and message.content.find('help')< 0:
        if bot.movie_channel == None:
            submissions_category = discord.utils.get(bot.server.categories, name='submissions')

            new_channel_name = message.content.replace(summon_movie_night_message, '')
            new_channel_name = new_channel_name.strip()

            bot.movie_channel = await bot.server.create_text_channel(new_channel_name)
            await bot.movie_channel.edit(category=submissions_category)

            await bot.debug_output_channel.send('bot.movie_channel = {0.mention}'.format(bot.movie_channel))
            output = [">>----- 🦂 it's movie night!! 🦂 -----<<"]
            output.append("submit movies in {0.mention}!".format(bot.movie_channel))
            output.append("see {0.mention} for literature on The System™️".format(bot.intro_channel))
            output.append (">>---------------------------------------<<")

            separator = '\n'
            await bot.general_channel.send(separator.join(output))
        else:
            await bot_say("someone tried to create a movie channel, but one already exists!", bot.debug_output_channel)

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

    #print('Updated proposed movies; new count: {0}'.format(len(bot.proposed_movies)))
    #for key in bot.proposed_movies:
    #    print(bot.proposed_movies[key].movie_name)

    #await bot.debug_output_channel.send(len(bot.proposed_movies))

async def bot_gif(query):
    return await search_gifs(query)

async def search_gifs(query):
    try:
        response = bot.giphy_api_instance.gifs_search_get('T4CvdfWLKISr2UdxxoTExXqoGaQh9e8v', query)
        lst = list(response.data)
        gif = random.choices(lst)

        return gif[0].url

    except ApiException as e:
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
        return ""

def download(url: str, dest_folder: str, filename: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        size  = r.headers.get("Content-Length")
        if int(size) < 10000000 / bot.preview_count and int(size) > 420000:
            print("attempting download of: {}".format(url))
            print("saving to", os.path.abspath(file_path))
            file  = open(file_path, 'wb')
            file.write(r.content)
            return True
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {0}\n{1}".format(r.status_code, r.text))

    return False

#----------------------------------------------------------------------------------------
#-------------------------- D E B U G --- C O M M A N D S -------------------------------
#----------------------------------------------------------------------------------------

async def debug_test_command(message):
    if message.channel != bot.command_channel and message.channel != bot.debug_output_channel:
        return

    lower_message = message.content.lower()
    if lower_message == "test":
        output = ["{0}! your voice has been heard".format(message.author)]
        submissions_category = discord.utils.get(bot.server.categories, name='submissions')
        channels = submissions_category.channels
        if len(channels) == 0:
            output.append("found no channel(s) in the 'submissions' category")
        else:
            output.append("the current movie channel is set to {0}".format(bot.movie_channel))
        
        separator = '\n'
        await message.channel.send(separator.join(output))

async def debug_help_command(message):
    lower_message = message.content.lower()
    if lower_message == "help" or lower_message == "/help":
        separator = '\n'
        if message.channel == bot.command_channel or message.channel == bot.debug_output_channel:
            output = ['🤖 **NoDiggityNoBot Help** 🤖']

            output.append("\n\n**hi! i'm nodiggs, and i can help you manage movie night!")

            output.append("\n\n**AMBIENT FEATURES:")
            output.append("\ni will react to any message that i think mentions me")
            output.append("\nanything you react to with '🎴'' i will react convert to my emoji")
            output.append("\nif there is a solo channel in category:SUBMISSIONS, it will be assumed as the movie channel")
            output.append("\ndon't be a jerk")

            output.append("\n\n**AVAILABLE COMMANDS IN: *#bot-commands***")
            output.append("\n**help OR /help** \n- you're looking at it.")
            output.append("\n**test** \n- check my status")
            output.append("\n**summon +'Cool  Movie Channel---Name!! 🤖'**\n-creates a new movie channel for the night\n-name will be formatted to discord channel rules:\n--(ex:cool-movie-channel-name-🤖)\n-general is notified that movie night has begun!")
            output.append("\n**short list** \n- collects all the non-vetoed movies and filters all with the top 3 vote counts. sends a message to #operations with the content for human emojification\n--last reaction emoji on each movie message in #operations will be treated as movie_name.emoji_icon for final vote")
            output.append("\n**final vote** \n- creates a final vote in #general using the short list and supplied emojis from #operations")
            output.append("\n**decide** \n- calls the winner; asks Ruth for help if there is a tie; asks Kat for the time")
            output.append("\n**status report** OR **movie status** OR **status** \n- sends a message to #general with the current movie standings")
            output.append("\n**preview** \n- creates a gif preview of one of the movies in the movie channel\n")
            
            await message.channel.send(separator.join(output))

            output = []

            output.append("\n**AVAILABLE COMMANDS IN #bot-debug-output***")
            output.append("\n**help OR /help** \n- you're looking at it")
            output.append("\n**test** \n- check my status")

            output.append("\n\n**AVAILABLE COMMANDS IN: *#general***")
            output.append("\n**help OR /help**\n- you're looking at it")
            output.append("\n**status report** OR **movie status** OR **status** \n- sends a message to #general with the current movie standings")
            output.append("\n**preview**\n- creates a gif preview of one of the movies in the movie channel")
            output.append("\n**'what' + 'day' - ' a '**\n- i tell you what day it is")
            output.append("\n**'.......' + alert**\n- i will try to properly alert you!")

            output.append("\n\n**AVAILABLE COMMANDS IN: *all channels***")
            output.append("\n**censor** OR **gif shield** OR **shield** OR **no paul**\n- i defend eyeballs and spirits by denying users their freedom of expression")

            output.append("\n\n🤖 💛 🤖 💛 🤖")

            await message.channel.send(separator.join(output))

        elif message.channel == bot.general_channel:
            output = ['🤖 **NoDiggityNoBot Help** 🤖']

            output.append("\n\n**hi! i'm nodiggs, and i can help you manage movie night!")

            output.append("\n\n**AVAILABLE COMMANDS IN: *#general***")
            output.append("\n**help**\n- you're looking at it")
            output.append("\n**status report** OR **movie status** OR **status** \n- sends a message to #general with the current movie standings")
            output.append("\n**preview**\n- creates a gif preview of one of the movies in the movie channel")
            output.append("\n**'what' + 'day' - ' a '**\n- i tell you what day it is")
            output.append("\n**'.......' + alert**\n- i will try to properly alert you!")

            output.append("\n\n**AVAILABLE COMMANDS IN: *all channels***")
            output.append("\n**censor** OR **gif shield** OR **shield** OR **no paul**\n- i defend eyeballs and spirits by denying users their freedom of expression")

            output.append("\n\n🤖 💛 🤖 💛 🤖")

            await message.channel.send(separator.join(output))
    

#----------------------------------------------------------------------------------------
#-------------------------- D I S C O R D --- E V E N T S -------------------------------
#----------------------------------------------------------------------------------------
# Now we start listening to all the different Discord events!
@bot.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.guild == None:
        return

    bot.server = message.guild;

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
        await debug_help_command(message)

    if message != None:
        await debug_test_command(message)

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
        await download_preview_command(message)

    if message != None:
        await alert_commands(message)

    if message != None:
        await matt_firsteenth(message)

    if message != None:
        await coin_flip(message)

@bot.event
async def on_message_delete(message):
    if message.channel == bot.movie_channel:
        bot.proposed_movies.pop(message.content, None)

@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    await check_reactions(message, user)
    
@bot.event
async def on_raw_reaction_remove(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    await check_reactions(message, user)

# Run the bot and init channels
bot.run(TOKEN)