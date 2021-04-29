# -*- coding: utf-8 -*-

from events import *
from commands import *
from settings import *
from bot import Cypher

bot = Cypher()

bot.event(on_ready)
bot.event(on_disconnect)
bot.event(on_member_join)

bot.command()(ping)
bot.command()(clear)
bot.command()(perms)
bot.command()(members)
bot.command()(publish)
bot.command()(news)
bot.command()(exec)


@bot.command()
async def id(ctx):
	print(ctx.guild.id)


if __name__ == '__main__':
	bot.run(TOKEN)
	bot.dump_memory_in("data/memory.json")
