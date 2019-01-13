# Work with Python 3.6
import array
import discord
import math
import random
import re

#assumes your secret.txt has a newline following the token.
TOKEN = open("secret.txt","r").readlines()[0][:-1]
debug = True
client = discord.Client()

@client.event
async def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == client.user:
		return

	if message.content.startswith('!hello')|message.content.startswith('.hello'):
		msg = 'Hello {0.author.mention}'.format(message)
		await client.send_message(message.channel, msg)
		
	if message.content.startswith('!devhello')|message.content.startswith('.devhello'):
		await sayhello(client, message)

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
		
		
	if message.content.startswith('.devroll'):
		print("doing devroll")
		allrolls = message.content.split(" ")[1]
		print(allrolls)
		results = []
		dicepools = []
		total = 0
		simple = False
		simpleroll = ""
		#if(len(re.findall(r"[dD]", allrolls))==1):
			#display simple roll result
			#simple = True
		#else:
		rolls = re.findall(r"[\+\-]?[0-9a-zA-Z!,]+", allrolls)
		print(str(rolls))
		for roll in rolls:
			#if(simple and re.match("d",roll)):
			#	simpleroll = roll
			#	continue
			(result, dice) = await makeroll(client, message, roll, 0)
			results.append(result)
			dicepools.append(dice)
			total += result
		#if(simple):
		#	(result, dice) = makeroll(client, message, simpleroll, total)
		#else:
		await client.send_message(message.channel, "Total = {0} ({1})".format(str(total),str(results)))
		#end else on line 70
		#figure out how to delete calling message

async def sayhello(client,message):
	msg = 'Fuck off {0.author.mention}, you\'re not my real dad!'.format(message)
	await client.send_message(message.channel, msg)

async def makeroll(client, message, roll, mod):
	print("makeroll: roll={0}, mod={1}".format(roll,str(mod)))
	input = roll
	sign = ""
	num = 0
	sides = 0
	sort = ""
	keep = 0
	explodes = []
	dice = []
	result = 0
	explosions = []
	
	# Example input: +4d6h3!1,6
	# Parsed: sign="+", num=4, sides=6, sort="h", keep=3, explodes=[1,6]
	
	
	if debug: print("Check roll formatting to avoid crashes.")
	rollformat = r"(?:(?:[\+\-]?[0-9]*[dD][0-9]+(?:[lLhH][0-9]+)?(?:!(?:[0-9]+,)*[0-9]*)?)|(?:[\+\-]?[0-9]+))"
	match = re.match(rollformat, roll)
	if(match==None or match.group()!=roll):
		await client.send_message(message.channel, "I'm sorry, Dave. I'm afraid I can't do that.\nRoll format error on \"{0}\"".format(roll))
		return(-1,[])
	
	print("Check for positive/negative mod, peel it off.")
	if(roll.startswith(("+","-"))):
		sign = roll[0]
		roll = roll[1:]
	else:
		print("	unsigned rolls are positive")
		sign = "+"
		
	# roll = 4d6h3!1,6
	if debug: print("roll = " + roll)
	
	if debug: print("Check number of dice, peel off through [dD].")
	if any(d in roll for d in "Dd"):
		if debug: print("	dice phrase present")
		if roll[0] not in "Dd":
			#number of dice specified
			(num,roll) = re.split("[Dd]",roll)
			num = int(num)
		else:
			#assume 1 die
			num = 1
			roll = roll[1:]
	else:
		#no dice phrase - return flat mod.
		return(int(input),dice)
	
	# roll = 6h3!1,6
	if debug: print("roll = " + roll)
	
	if debug: print("Check for keep phrase, peel it off & parse/peel #sides.")
	if any(k in roll for k in "lLhH"):
		if debug: print("	keep phrase present - parse/peel sort, keep, & #sides.") 
		sort = re.findall(r"[lLhH][0-9]+",roll)[0]
		keep = int(sort[1:])
		sort = sort[0]
		sides = int(re.split(r"[lLhH]",roll)[0])
		roll = re.split(r"[lLhH][0-9]+",roll)[1]
	else:
		if debug: print("	no keep phrase - keep all, only peel #sides.")
		keep = num
		sides = int(roll.split("!")[0])
		if("!" in roll): roll = roll[roll.find("!"):]
		
	# roll = !1,6
	if debug: print("roll = " + roll)
	
	#TODO: add support for individual explodes
	if debug: print("Checking for explode phrase")
	if "!" in roll:
		if debug: print("	Explodes detected")
		explodes.append(sides)
		#assert [explodes] is not all results
		if(len(explodes)>=sides):
			await client.send_message(message.channel,  "I'm sorry, Dave. I'm afraid I can't do that.\nAll die results explode.")
			return(-1,[])
			
	if debug: print("Roll the dice")
	for i in range(num):
		#get <num> results
		dice.append(random.randint(1,sides))
	if(sort!=""):
		#if there's a keep phrase, sort dice
		dice = sorted(dice)
		
	if debug: print(str(dice))
		
	#Evaluate each kept die in order
	for i in range(keep):
		die = 0
		if sort in "hH":
			#if keeping highest, evaluate from the top.
			die = dice[len(dice)-1-i]
		else:
			die = dice[i]
		#Evaluate/cascade explosions
		if die in explodes:
			exproll = die
			while exproll in explodes:
				exproll = random.randint(1,sides)
				explosions.append(exproll)
				result = result + exproll
		result = result + die
	if(sign=="-"): result = -result
	if debug: print("Result = " + str(result) + ", mod = " + str(mod))
	result = result + mod
	
	#Display the results of the pool
	output = ""
	if(len(explosions)>0):
		#display output with explosions
		output = "{0} = {1} (dice: {2} + bonus: {3})".format(input, str(result), str(dice), str(explosions))
	else:
		#display output without explosions
		output = "{0} = {1} (dice: {2})".format(input, str(result), str(dice))
	if(mod!=0):
		if mod < 0:
			output = output + " - " + str(abs(mod))
		else:
			output = output + " + " + str(mod)
	await client.send_message(message.channel, output)
	return (result,dice)

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

client.run(TOKEN)