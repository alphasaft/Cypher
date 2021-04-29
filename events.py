from bot import Cypher, EventType


async def on_disconnect():
	print("Disconnected")


async def on_ready():
	bot = Cypher()
	print("Logged in as : " + str(bot.user))
	await bot.load_memory_from("data/memory.json")
	print("Memory loaded.")


async def on_member_join(member):
	bot = Cypher()
	
	event = bot.fetch_memory_event(
		guild_id=member.guild.id,
		event_type=EventType.PUBLISH,
		check=lambda x: x.payload["publication_type"] == "video"
	)

	await member.send(
		"Bienvenue sur le serveur de SNIV ! N'hesite pas à aller vérifier sa dernière vidéo : %s !\n"
		"*chuchotte* Et abonne-toiiiii parce qu'il fait du bon boulot et que ça le soutiendrait !\n"
		"*chuchotte encore plus bas* Et un like aussi parce que t'es sympa"
		% event.payload["content"]
	)
