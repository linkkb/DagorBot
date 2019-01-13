# Work with Python 3.6
import array
import discord
import math
import random
import re


TOKEN = open("secret.txt","r").readlines()[0]

client = discord.Client()

@client.event
async def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == client.user:
		return

	if message.content.startswith('!hello')|message.content.startswith('.hello'):
		msg = 'Hello {0.author.mention}'.format(message)
		await client.send_message(message.channel, msg)

	if message.content.startswith('!fix')|message.content.startswith('.fix'):
		msg = 'No, no {0.author.mention}, not the ice pick!'.format(message)
		await client.send_message(message.channel, msg)
		
	if message.content.startswith('!roll')|message.content.startswith('.roll'):
		
		#DEFINE VARS		
		rollList = []
		rollResult = 0
		m = 0
		x = message.content
		
		#PARSE
		roll = x.split(" ")[1]
		rollNat = re.split("\W", roll, 1)[0] #split off "natural roll" from additive/subtractive modifiers.
		(n,s) = rollNat.split("d") #n = number of dice, s = sides
		modifiers = re.findall(r"[+|-][0-9]+", roll) #populate list of modifiers
		for x in modifiers:
			m += (int(x)) #calculate net modifier
			
		#ROLL
		for x in range(int(n)): 
			rollList.append(random.randint(1,int(s))) 
		for i in range(int(n)):
			rollResult += rollList[i]
		rollResultMod = rollResult + m #add calculated modifier

		#DISPLAY
		msg = ('{0.author.mention} rolled ' + roll + ' and got **' + str(rollResultMod) + '**.\n*' + rollNat + ' = (' + str(rollList)[1:-1] + ').*').format(message)
		await client.send_message(message.channel, msg)

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

client.run(TOKEN)