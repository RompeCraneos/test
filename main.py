import discord
from ruamel.yaml import YAML
import re
import random

token = YAML().load(open("token.yaml"))["token"]
config = YAML().load(open("config.yaml"))

prefix = config["prefix"]
whitelist = config["reactions"]["whitelist"]
blacklist = config["reactions"]["blacklist"]


def get_id_from_str(string):
    results = re.findall(r"(\d+)", string)
    return None if len(results) == 0 else results[0]


def is_member_valid(member):
    if len([role for role in member.roles if role.id in whitelist]) == 0:  # no role in whitelist = deny
        return False
    return len([role for role in member.roles if role.id in blacklist]) > 0  # role in blacklist = deny


def has_perms(member, channel):
    if client.user.id == "431980306111660062" and member.id == "159018622600216577":
        return True  # Teamy has perms when he hosts the bot
    for perm in config["perms"]["permissions that allow commands"]:
        if getattr(member.permissions_in(channel), perm):
            return True
    return any([role.id in config["perms"]["roles that allow commands"] for role in member.roles])


async def get_reactors(reactions):
    rtn = []
    for reaction in reactions:
        while len(rtn) < reaction.count:
            rtn += await client.get_reaction_users(reaction, after=None if len(rtn) == 0 else rtn[-1])
    return set([member for member in rtn if not member.bot])


async def notify_winner(member):
    await client.send_message(member, config["winner direct message"])


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged in as {}".format(client.user.name))
        await client.change_presence(
            game=discord.Game(name=config["presence"]["text"], type=config["presence"]["type"]))

    async def on_message(self, message):
        if message.server is None:
            return
        if not has_perms(message.author, message.channel):
            return
        if prefix not in message.content or message.content.index(prefix) != 0:
            return
        args = message.content[len(prefix):].split()
        if args[0] == "help":
            await client.send_message(message.channel, "https://github.com/TeamDman/Pick-Bot")
        elif args[0] == "eval":
            result = eval(str.join(" ", args[1:]))
            em = discord.Embed()
            em.description = str(result)
            await client.send_message(message.channel, embed=em)
        elif args[0] == "aval":
            result = await eval(str.join(" ", args[1:]))
            em = discord.Embed()
            em.description = str(result)
            await client.send_message(message.channel, embed=em)
        elif args[0] == "react":
            if not len(args) == 4:
                await client.send_message(message.channel, "Invalid arguments. Required:\nreact channel message emote")
                return
            react = args[3]
            messageid = args[2]
            channelid = get_id_from_str(args[1])
            channel = client.get_channel(channelid)
            message = await client.get_message(channel, messageid)
            await client.add_reaction(message, react)
        elif args[0] == "start":
            if not len(args) == 3:
                await client.send_message(message.channel, "Invalid arguments. Required:\nstart channel emote")
                return
            try:
                await client.add_reaction(message, args[2])
            except discord.errors.HTTPException:
                await client.send_message(message.channel, "The bot can't use that emote. Try again.")
                return
            em = discord.Embed()
            em.title = config["embed start"]["title"]
            em.colour = config["embed start"]["colour"]
            em.description = config["embed start"]["description"]
            for field in config["embed start"]["fields"]:
                em.add_field(name=field["name"], value=field["value"])

            channelid = get_id_from_str(args[1])
            channel = client.get_channel(channelid)
            sent = await client.send_message(channel, embed=em)
            await client.add_reaction(sent, args[2])
            await client.send_message(message.channel, "Sent message id: {}".format(sent.id))
        elif args[0] == "end":
            if not len(args) == 4:
                await client.send_message(message.channel,
                                          "Invalid arguments. Required:\nend channel message winner_count")
                return
            channelid = get_id_from_str(args[1])
            channel = client.get_channel(channelid)
            sent = await client.get_message(channel, args[2])
            winners = await get_reactors(sent.reactions)
            if len(winners) < int(args[3]) or int(args[3]) < 0:
                await client.send_message(message.channel, "Pick count invalid. (0-{})".format(len(winners)))
                return
            winners = random.sample(winners, int(args[3]))

            for winner in winners:
                await notify_winner(winner)

            em = discord.Embed()
            em.title = config["embed end"]["title"]
            em.colour = config["embed end"]["colour"]
            em.description = config["embed end"]["description"].format("\n".join([u.mention for u in winners]))
            for field in config["embed end"]["fields"]:
                em.add_field(name=field["name"], value=field["value"])

            await client.send_message(sent.channel, embed=em)
        elif args[0] == "who":
            if not len(args) == 3:
                await client.send_message(message.channel, "Invalid arguments. Required:\nwho channel message")
                return
            channelid = get_id_from_str(args[1])
            channel = client.get_channel(channelid)
            sent = await client.get_message(channel, args[2])
            winners = await get_reactors(sent.reactions)
            em = discord.Embed()
            em.title = "React WhoIs"
            em.add_field(name="Unique", value="{} users".format(len(winners)))
            em.add_field(name="Random 10", value="\n".join(
                [user.name for user in random.sample(winners, len(winners) if len(winners) < 10 else 10)]))
            await client.send_message(message.channel, embed=em)

    async def on_reaction_add(self, reaction, user):
        if not is_member_valid(user):
            client.remove_reaction(reaction.message, reaction.emoji, user)


print("Creating client")
client = MyClient()
if token is None or len(token) == 0:
    print("Please set a token in token.yaml")
    raise SystemError
client.run(token)
