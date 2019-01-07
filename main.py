import discord
import os
from keep_alive import keep_alive
from insults import insult_generator
from compliments import compliment_generator
from tts import create_announcement

client = discord.Client()

@client.event
async def on_ready():
        ## Intialise the channel_dict then add the channel names and ids 
        global text_channel_dict
        global voice_channel_dict
        
        text_channel_dict = {}
        voice_channel_dict = {}

        for channel in client.get_all_channels():
            if str(channel.type) == 'text': 
                text_channel_dict.update({channel.name:channel.id})
            if str(channel.type) == 'voice': 
                voice_channel_dict.update({channel.name:channel.id})
        ## Print the channel_dict                 
        print("text channel dict - ", text_channel_dict)
        print("voice channel dict - ", voice_channel_dict)

        ## text_channel_dict = {'general': '299268380823650304'}
        ## voice_channel_dict = {'big onoyon': '299268380823650305'}

        ## Print the bot status
        print(client.user, "connected")
        
        ## Sends a message to the server stating the bot is alive and how to use it
        general_channel = client.get_channel(text_channel_dict['general'])
        await client.send_message(general_channel, 'Hi, I\'m shit bot!')
        await client.send_message(general_channel, 'You can ask me to insult people with !insult {their name}.')
        await client.send_message(general_channel, 'You can ask me to compliment people with !compliment {their name}.')
        await client.send_message(general_channel, 'I\'m a shitty robot!')

## This will wait for a message event to occur in the form of a command.
##    !join: will ask the bot to join your current voice channel
##    !leave: will ask the bot to leave any voice channels     
##    !insult: will ask the bot to insult someone, if the bot is in voice it will attempt to do this through text to speech, otherwise it will type the insult
##    !compliment: will ask the bot to compliment someone, if the bot is in voice it will attempt to do this through text to speech, otherwise it will type the insult
@client.event
async def on_message(message):
        if message.content[0] == "!":
            message.content = message.content[1:].lower()

            ## This will instruct the bot to join the channel the user is currently in
            if message.content.startswith('join'):
                if message.author.voice_channel != None and client.is_voice_connected(message.server) != True:
                    ## Creates a voiceClient object
                    await voice = client.join_voice_channel(client.get_channel(message.author.voice_channel.id))

                elif message.author.voice_channel == None:
                    await client.send_message(message.channel, 'You are not in a voice channel.')

                else:
                    await client.send_message(message.channel, 'I am already in a voice channel. Use !leave to make me leave.')
        
            # This will leave the current voice channel
            elif message.content.startswith('leave'):
                await client.disconnect()
                voice = None

            ## Will insult the target
            elif message.content.startswith('insult'):
                insult = insult_generator()
                name = message.content[6:]
                await client.send_message(message.channel, name + " " + insult)
                
            ## Will compliment the target
            elif message.content.startswith('compliment'):
                print(tts_indicator)
                compliment = compliment_generator()
                name = message.content[9:]
                await client.send_message(message.channel, "Hey " + name + ", " + compliment)


# Announce the change in voice state through text to speech (ignores mutes/deafens)
@client.event
async def on_voice_state_update(before, after):
    # Ensure bot is connected to voice client - !join has been used
    if client.is_voice_connected(before.server) == True:
        global player
        previousChannel = before.voice_channel
        newChannel = after.voice_channel

        # Bot only talks when user's channel changes, not on mutes/deafens
        if previousChannel != newChannel:
            # When user joins or moves to bot's channel
            if newChannel == currentChannel:
                tts.create_announcement(after.name, 'has joined the channel')

            # When user leaves bot's channel
            elif previousChannel != None and newChannel == None and previousChannel == currentChannel:
                tts.create_announcement(after.name, 'has left the channel')

            # When user moves out of bot's channel to a new channel
            elif previousChannel == currentChannel and newChannel != currentChannel:
                tts.create_announcement(after.name, 'had moved to another channel')

            # After user joins, leaves or moves, announce the new announcement
            if (newChannel == currentChannel or previousChannel != None and
                newChannel == None and previousChannel == currentChannel or
                previousChannel == currentChannel and newChannel != currentChannel):

                try:
                    if player.is_playing() == False:
                        player = voice.create_ffmpeg_player('announce.mp3')
                        player.start()

                except NameError:
                    player = voice.create_ffmpeg_player('announce.mp3')
                    player.start()


## This block will call the keep alive function to create the flask application, then create the token object and finally run the bot
if __name__ == "__main__":
    keep_alive()

    ##Need to insert this into the environment var and replace the below
    token = os.environ.get("DISCORD_BOT_SECRET")
    
    client.run(token)

