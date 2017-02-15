import os
import re

import discord
import asyncio

ROLES = ['tank', 'healer', 'dps']

raids = {}

async def schedule(message, raid, description):
    if raid in raids:
        ack_message = 'Raid with name "{}" has already been scheduled'
        subs = (raid,)
        embed = discord.Embed(color=discord.Color.red(),
                              title=ack_message.format(*subs))
        await client.send_message(message.channel, embed=embed)
        return

    raids[raid] = {
        'name': raid,
        'description': description,
        'members': {}
    }

    ack_message = 'Raid "{}" has been scheduled'
    subs = (raid,)
    embed = discord.Embed(color=discord.Color.green(),
                          title=ack_message.format(*subs))
    await client.send_message(message.channel, embed=embed)

async def start(message, raid):
    if raid not in raids:
        ack_message = 'Raid with name "{}" does not exist'
        subs = (raid,)
        embed = discord.Embed(color=discord.Color.red(),
                              title=ack_message.format(*subs))
        await client.send_message(message.channel, embed=embed)
        return

    current_raid = raids[raid]
    current_invites = ['/inv {}'.format(x) for x in current_raid['members']]

    ack_message = 'Raid "{}" has been started. {} users have joined the raid:'
    subs = (raid, len(current_invites))
    embed = discord.Embed(color=discord.Color.green(),
                          title=ack_message.format(*subs),
                          description='\n'.join(current_invites))
    await client.send_message(message.channel, embed=embed)

async def join(message, raid, role=None):
    if raid not in raids:
        ack_message = 'Raid with name "{}" does not exist'
        subs = (raid,)
        embed = discord.Embed(color=discord.Color.red(),
                              title=ack_message.format(*subs))
        await client.send_message(message.channel, embed=embed)
        return

    if role and role.lower() not in ROLES:
        ack_message = 'Available roles are: {}. Role "{}" is not one of them.'
        subs = (', '.join(ROLES), role)
        embed = discord.Embed(color=discord.Color.red(),
                              title=ack_message.format(*subs))
        await client.send_message(message.channel, embed=embed)
        return

    current_raid = raids[raid]
    user = message.author

    if message.author not in current_raid['members']:
        current_raid['members'][user] = {
            'roles': set()
        }

    current_user = current_raid['members'][user]

    if role:
        current_user['roles'].add(role)
        current_roles = current_user['roles']

        ack_message = 'User {} has been added to raid "{}" as {}'
        subs = (user.nick or user, raid, ', '.join(current_roles))
        embed = discord.Embed(color=discord.Color.green(),
                              title=ack_message.format(*subs))
        await client.send_message(message.channel, embed=embed)
        return
    else:
        ack_message = 'User {} has been added to raid "{}"'
        subs = (user.nick or user, raid)
        embed = discord.Embed(color=discord.Color.green(),
                              title=ack_message.format(*subs))
        await client.send_message(message.channel, embed=embed)
        return

commands = [{
    'regex': '^!schedule (.*)\n*(.*)',
    'handler': schedule
}, {
    'regex': '^!start (.*)',
    'handler': start
}, {
    'regex': '^!join (.*) as (\w+)',
    'handler': join
}, {
    'regex': '^!join (.*)',
    'handler': join
}]


token = os.environ.get('DISCORD_TOKEN', None)
if not token:
    raise ValueError('Token should be provided with DISCORD_TOKEN env variable')

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    for command in commands:
        match = re.match(command['regex'], message.content)
        if match:
            await command['handler'](message, *match.groups())
            break

client.run(token)
