from ast import Try
import asyncio
from secrets import choice
from typing import Optional
from webbrowser import get
import discord
import requests
from discord import app_commands
from discord.app_commands import Choice
from discord.ui import View, Button
from rcon.source import Client, rcon
from discord.ext import tasks
import os
from dotenv import load_dotenv 

import ec2_control

MY_GUILD = discord.Object(id=1021758457818394664)  # replace with your guild id

load_dotenv()
TOKEN = os.getenv('TOKEN')
PASS = os.getenv('PASS')
IP = os.getenv('IP')

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)

greentick = "<:greentick:1023396034363281428>"
redx = "<:redx:1023396035625758770>"

@client.event
async def on_ready():
    update_channel.start()
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

# start command
@client.tree.command(name='start', description='Startuje serwer, wymaga specjalnej roli.')
async def start(interaction: discord.Interaction):
    # CHANNEL CHECK
    if interaction.channel.id != 1024078298147471443:
        await interaction.response.send_message('❌ Komenda działa tylko w kanale <#1021758531956899950>!', ephemeral=True)
        return

    # ROLE CHECK
    if discord.utils.get(interaction.user.roles, id=1021759370205339669) is None:
        embedVar = discord.Embed(title="Błąd", description=f"{redx} Nie masz prawidłowych roli, aby użyć tej komendy!", color=0xff0000)
        await interaction.response.send_message(embed=embedVar, ephemeral=True)
        return

    if ec2_control.instance_status("i-0f5911636a9843859") == 'running':
        embedVar = discord.Embed(title=f"{greentick} Serwer już chodzi", description=f"{redx} Serwer już chodzi! Spróbuj dołączyć, a jeśli są problemy to wyłącz i włącz serwer.", color=0x00ff00)
        await interaction.response.send_message(embed=embedVar, ephemeral=True)
        return
    try:
        ec2_control.start_instance('i-0f5911636a9843859')
    except Exception as e:
        embedVar = discord.Embed(title=f"{redx} Błąd", description=f"{redx} Wystąpił błąd podczas uruchamiania serwera. Spróbuj ponownie później.", color=0xff0000)
        await interaction.response.send_message(embed=embedVar, ephemeral=True)
        print(f"ERROR: {e}")
        return
    embedVar = discord.Embed(title=f"{greentick} Włączono Serwer", description="Maszyna startowała. Proszę parę minut poczekać zanim się serwer ARK uruchomi. Możesz sprawdzić czy jest uruchomiony za pomocą `/status`.", color=0x00ff00)
    # create a button that does /server status
    await interaction.response.send_message(embed=embedVar)
    print(f'{interaction.user} uruchomił serwer!')

# stop command
@client.tree.command(name='stop', description='Wyłącza serwer, wymaga specjalnej roli.')
async def stop(interaction: discord.Interaction):
    # CHANNEL CHECK
    if interaction.channel.id != 1024078298147471443:
        await interaction.response.send_message('❌ Komenda działa tylko w kanale <#1021758531956899950>!', ephemeral=True)
        return

    # ROLE CHECK
    if discord.utils.get(interaction.user.roles, id=1021759370205339669) is None:
        embedVar = discord.Embed(title="Error", description=f"{redx} Nie masz prawidłowych roli, aby użyć tej komendy!", color=0xff0000)
        await interaction.response.send_message(embed=embedVar, ephemeral=True)
        return

    # STOPPED CHECK
    if ec2_control.instance_status('i-0f5911636a9843859') == 'stopped':
        embedVar = discord.Embed(title=f"{redx} Serwer już jest wyłączony!", description="Serwer już jest wyłączony! Jeśli chcesz zagrać na nim to włącz serwer za pomocą `/start`.", color=0xff0000)
        await interaction.response.send_message(embed=embedVar, ephemeral=True)
        return

    # PLAYER CHECK
    players = await rcon(
        'ListPlayers',
    host=IP, port=27020, passwd=PASS
    )
    # if no players are online, the response starts with the letter N
    if players[0] == 'N':
        playercount = '0'
    else:
        players = players.split('\n')
        players = players[:-1]
        playercount = len(players)
    if playercount != '0':
        embedVar = discord.Embed(title=f"{redx} Błąd", description=f"{redx} Na serwerze jest {playercount} graczy. Wyłącz serwer, gdy wszyscy gracze opuszczą serwer.", color=0xff0000)
        await interaction.response.send_message(embed=embedVar, ephemeral=True)


    ec2_control.stop_instance('i-0f5911636a9843859')
    embedVar = discord.Embed(title=f"{redx} Serwer Zatrzymany", description="Maszyna została zatrzymana. Serwer ARK powinien się zapisać i wyłączyć. Możesz go ponownie uruchomić za pomocą `/start`.", color=0xff0000)
    await interaction.response.send_message(embed=embedVar)
    print(f'{interaction.user} zatrzymał serwer!')

# status command
@client.tree.command(name='status', description='Sprawdza status serwera.')
async def status(interaction: discord.Interaction):
    # CHANNEL CHECK
    if interaction.channel.id != 1024078298147471443:
        await interaction.response.send_message('❌ Komenda działa tylko w kanale <#1021758531956899950>!', ephemeral=True)
        return

    awsserver = ec2_control.instance_status("i-0f5911636a9843859")
    if awsserver == 'running':
        awsserver = f'{greentick} Online'
    elif awsserver == 'stopped':
        awsserver = f'{redx} Offline'
    elif awsserver == 'pending':
        awsserver = '⏳ Uruchamianie'
    elif awsserver == 'shutting-down' or 'stopping':
        awsserver = '⏳ Zatrzymywanie'
    else:
        print(f'Nieznany status: {awsserver}')
        awsserver = '❓ Nieznany'
    r = requests.get(f'http://api.steampowered.com/ISteamApps/GetServersAtAddress/v0001?addr={IP}:27015&format=json')

    # IF THE SERVER IS OFFLINE
    if r.json()['response']['servers'] == []:
        arkserver = f'{redx} Offline'
        playercount = '❓ Offline'

    # IF THE SERVER IS ONLINE
    elif r.json()['response']['servers'][0]['gamedir'] == 'ark_survival_evolved':
        arkserver = f'{greentick} Online'
        players = await rcon(
        'ListPlayers',
        host=IP, port=27020, passwd=PASS
        )
        # if no players are online, the response starts with the letter N
        if players[0] == 'N':
            playercount = '0'
        else:
            players = players.split('\n')
            players = players[:-1]
            playercount = len(players)

    # IF SOMETHING IS FUCKED UP
    else:
        arkserver = '❓ Error'
        playercount = '❓ Error'

    embedVar = discord.Embed(title="📊 Status Serwera", description="Status maszyny oraz serwera ARK.", color=0x053552)
    embedVar.add_field(name="Maszyna", value=awsserver, inline=False)
    embedVar.add_field(name="Serwer ARK", value=arkserver, inline=False)
    if playercount != '❓ Offline':
        embedVar.add_field(name="Gracze", value=f"{playercount}", inline=False)
    await interaction.response.send_message(embed=embedVar, ephemeral=True)
    return

# IP command
@client.tree.command(name='ip', description='Pokazuje IP serwera.')
async def ip(interaction: discord.Interaction):
    # CHANNEL CHECK
    if interaction.channel.id != 1024078298147471443:
        await interaction.response.send_message('❌ Komenda działa tylko w kanale <#1021758531956899950>!', ephemeral=True)
        return

    ip = ec2_control.get_elastic_ip('i-0f5911636a9843859')
    embedVar = discord.Embed(title="🌐 IP Serwera", description="Jeśli chcesz połączyć się bezpośrednio do serwera (za pomocą server list w steamie) to połącz się do tego IP", color=0xFFD0A0)
    embedVar.add_field(name="IP", value=f"`{ip}`", inline=True)
    embedVar.add_field(name="Port", value="`27015`", inline=True)
    await interaction.response.send_message(embed=embedVar, ephemeral=True)
    return

@client.tree.command(name='forcestop', description='Wymusza zatrzymanie serwera.')
async def forcestop(interaction: discord.Interaction):
    # CHANNEL CHECK
    if interaction.channel.id != 1024078298147471443:
        await interaction.response.send_message('❌ Komenda działa tylko w kanale <#1021758531956899950>!', ephemeral=True)
        return

    # ADMIN CHECK
    if discord.utils.get(interaction.user.roles, id=1022625217656410152) is None:
        await interaction.response.send_message('❌ Nie jesteś administratorem!', ephemeral=True)
        return

    # STOPPED CHECK
    if ec2_control.instance_status('i-0f5911636a9843859') == 'stopped':
        embedVar = discord.Embed(title=f"{redx} Serwer już jest wyłączony!", description="Serwer już jest wyłączony! Jeśli chcesz zagrać na nim to włącz serwer za pomocą `/start`.", color=0xff0000)
        await interaction.response.send_message(embed=embedVar, ephemeral=True)
        return

    ec2_control.stop_instance('i-0f5911636a9843859')
    embedVar = discord.Embed(title=f"{redx} Serwer Zatrzymany", description="Maszyna została wymuszono zatrzymana. Serwer ARK powinien się zapisać i wyłączyć. Możesz go ponownie uruchomić za pomocą `/start`.", color=0xff0000)
    await interaction.response.send_message(embed=embedVar)
    print(f'{interaction.user} wymuszowo zatrzymał serwer!')

# Update channel status name every 5 minutes
@tasks.loop(minutes=5)
async def update_channel():
    r = requests.get(f'http://api.steampowered.com/ISteamApps/GetServersAtAddress/v0001?addr={IP}:27015&format=json')
    # If there is no data in server list, the server is offline
    if r.json()['response']['servers'] == []:
        status = f'OFFLINE'
        playercount = 'OFFLINE'
    elif r.json()['response']['servers'][0]['gamedir'] == 'ark_survival_evolved':
        status = f'ONLINE'
        players = await rcon(
        'ListPlayers',
        host=IP, port=27020, passwd=PASS
        )
        # if no players are online, the response starts with the letter N
        if players[0] == 'N':
            playercount = '0'
        else:
            players = players.split('\n')
            players = players[:-1]
            playercount = len(players)

    else:
        status = 'ERROR'

    channel = client.get_channel(1024317636697395241)
    if playercount == 'OFFLINE':
        await channel.edit(name=f'🔴 {status}')
    else:
        await channel.edit(name=f'🟢 {status} ({playercount})')

# Delete messages in command only channel
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id == 1024078298147471443:
        await message.delete()

client.run(TOKEN)