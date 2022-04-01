import os
import discord
from dotenv import load_dotenv
from dbConnector import DbConnector
from eth import ETHBlockchain
from commands import commands_length
from currencies import currency

# Load token from .env file
load_dotenv()

LOG = "NONE" # NONE / DEBUG
ETH_TOKEN = os.getenv("ETH_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

DEFAULT_CURRENCY = currency.USD
ETH_ADDRESS_LENGTH = 42
CURRENCY_PARAMETER_LEGTH = 4

# Database format for users:
# id, name, nbAddress

# Database format for addresses:
# id, ethAddress, currency

client = discord.Client()
dbConnector = DbConnector()
ethBlockchain = ETHBlockchain(ETH_TOKEN)
suffix = "!eth"

print("Starting bot...")

@client.event
async def on_ready():
    dbConnector.init()
    # set activity of bot with eth price
    ethPrice = await ethBlockchain.getETHPrice()
    await client.change_presence(activity=discord.Game(name="ETH: " + str(ethPrice) + " USD"))
    print("1.0.0")
    print("Bot ready !")

# Add ETH address to database with !eth add <ETH address> <currency>
async def add(message):
    # Split message
    splitMessage = message.content.split(" ")
    # Verify if address is valid
    if (LOG == "DEBUG"):
        print(splitMessage)
    # Verify if currency is valid
    if (len(splitMessage) == 3):
        # Add default currency parameter
        splitMessage.append("USD")
        print(splitMessage)
    if (await ethBlockchain.isValidAddress(splitMessage[2])):
        errCode = dbConnector.addAddress(message.author.id, splitMessage[2], splitMessage[3])
        if (errCode == 0):
            await message.channel.send("Address added to database !")
        elif (errCode == -1):
            await message.channel.send("You already have this address linked to your account !")
        elif (errCode == -2):
            await message.channel.send("You don't have enough slot to add this address to your account !")
    else:
        await message.channel.send("Address invalid !")

# Get list of ETH addresses linked to user with !eth list
async def list(message):
    addresses = dbConnector.getAddresses(message.author.id)
    if (len(addresses) == 0):
        await message.channel.send("You don't have any address linked to your account !")
    else:
        await message.channel.send("You have the following addresses linked to your account:")
        userList = "```\n"
        for address in addresses:
            userList += address[1] + " " + address[2] + "\n"
        userList += "```"
        await message.channel.send(userList)

# Remove ETH address from database with !eth remove <ETH address>
async def remove(message):
    if (dbConnector.removeAddress(message.author.id, message.content[len(suffix) + commands_length.remove:]) == 0):
        await message.channel.send("Address removed from database !")
    else:
        await message.channel.send("You don't have this address linked to your account !")

# Verify if ETH address is valid
async def verifyETHAddress(message):
    if (await ethBlockchain.isValidAddress(message.content[len(suffix) + 6:])):
        return True
    else:
        return False

# Get ETH and USD balance for all ETH addresses linked to user with !eth balance
async def balance(message):
    addresses = dbConnector.getAddresses(message.author.id)
    if (len(addresses) == 0):
        await message.channel.send("You don't have any address linked to your account !")
    else:
        userList = "You have the following addresses linked to your account: ```\n"
        for address in addresses:
            ethBalance = await ethBlockchain.getETHBalance(address[1])
            if (address[2] == currency.USD.value):
                ethToCurrency = await ethBlockchain.ethToUSD(ethBalance)
            elif (address[2] == currency.EUR.value):
                ethToCurrency = await ethBlockchain.ethToEUR(ethBalance)
            userList += address[1] + ": " + str(ethBalance) + " ETH  (" + str("{:.2f}".format(ethToCurrency)) + " " + address[2] + ")\n"
        userList += "```"
        await message.channel.send(userList)

# Help command with description of all commands
async def help(message):
    await message.channel.send("```\n" +
                               "!eth add <ETH address>\n" +
                               "!eth list\n" +
                               "!eth remove <ETH address>\n" +
                               "!eth balance\n" +
                               "!eth info <ETH address>\n" +
                               "!eth help\n" +
                               "```")

# Detect message with suffixe and call function
# Check length of message to avoid error
@client.event
async def on_message(message):
    if (LOG == "DEBUG"):
        print("message received : " + message.content)
    if message.content.startswith(suffix + ' '):
        if message.content.startswith(suffix + " add "):
            if (len(message.content) == len(suffix) + commands_length.add.value + ETH_ADDRESS_LENGTH or
                len(message.content) == len(suffix) + commands_length.add.value + ETH_ADDRESS_LENGTH + CURRENCY_PARAMETER_LEGTH):
                await add(message)
        elif message.content.startswith(suffix + " help"):
            if (len(message.content) == len(suffix) + commands_length.help.value):
                await help(message)
        elif message.content.startswith(suffix + " list"):
            if (len(message.content) == len(suffix) + commands_length.list.value):
                await list(message)
        elif message.content.startswith(suffix + " remove "):
            if (len(message.content) == len(suffix) + commands_length.remove.value + ETH_ADDRESS_LENGTH):
                await remove(message)
        elif message.content.startswith(suffix + " balance"):
            if (len(message.content) == len(suffix) + commands_length.balance.value):
                await balance(message)
        else:
            await message.channel.send("Unknown command !")

@client.event
async def on_exit():
    await dbConnector.stopConnection()

client.run(DISCORD_TOKEN)