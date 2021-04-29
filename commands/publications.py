from discord.ext.commands import has_permissions
from bot import *

@has_permissions(administrator=True)
async def publish(ctx, publication_type, *content):
	"""Publie une nouveauté. Admins uniquement."""
	
	bot = Cypher()
	bot.remember(
		ctx.guild,
		ctx.author,
		EventType.PUBLISH,
		{
			"publication_type": publication_type,
			"content": " ".join(content)
		}
	)
	await ctx.channel.send("Publication enregistrée sous la catégorie '%s'" % publication_type)
	

async def news(ctx, publication_type):
	"""Vous informe de la derniere nouveauté dans la catégorie donnée"""
	
	bot = Cypher()
	event = bot.fetch_memory_event(
		guild_id=ctx.guild.id,
		event_type=EventType.PUBLISH,
		check=lambda e: e.payload["publication_type"] == publication_type
	)
	
	if not event:
		await ctx.channel.send("Pas de publications pour la catégorie %s" % publication_type)
		return
	
	await ctx.channel.send("Voici la dernière publication dans la catégorie %s : %s" % (
		publication_type,
		event.payload["content"]
	))
	
