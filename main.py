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


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged in as {}".format(client.user.name))

    async def on_message(self, message):
        if not message.author.id == "159018622600216577":
            return
        if prefix not in message.content or message.content.index(prefix) != 0:
            return
        args = message.content[len(prefix):].split()
        if args[0] == "help":
            await client.send_message(message.channel, "zoop")
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
            react = args[3]
            messageid = args[2]
            channelid = get_id_from_str(args[1])
            channel = client.get_channel(channelid)
            message = await client.get_message(channel, messageid)
            await client.add_reaction(message, react)
        elif args[0] == "start":
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
            channelid = get_id_from_str(args[1])
            channel = client.get_channel(channelid)
            sent = await client.get_message(channel, args[2])
            winners = []
            for reaction in sent.reactions:
                winners += await client.get_reaction_users(reaction, limit=reaction.count)
            winners = random.sample(winners, int(args[3]))

            em = discord.Embed()
            em.title = config["embed end"]["title"]
            em.colour = config["embed end"]["colour"]
            em.description = config["embed end"]["description"].format("\n".join([u.mention for u in winners]))
            for field in config["embed end"]["fields"]:
                em.add_field(name=field["name"], value=field["value"])

            await client.send_message(sent.channel, embed=em)

    async def on_reaction_add(self, reaction, user):
        if not is_member_valid(user):
            client.remove_reaction(reaction.message, reaction.emoji, user)


print("Creating client")
client = MyClient()
if token is None or len(token) == 0:
    print("Please set a token in token.yaml")
    raise SystemError
client.run(token)
