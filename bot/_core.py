from discord.ext.commands import Bot as DiscordBot
from settings import PREFIX, DESCRIPTION
from .io import JsonIO, Globals
from .memory import *


class Cypher(DiscordBot):
	"""Singleton representing Cypher"""
	instance = None
	
	def __new__(cls):
		return Cypher.instance or object.__new__(cls)
	
	def __init__(self):
		if not Cypher.instance:
			intents = discord.Intents.default()
			intents.members = True
			
			super().__init__(
				command_prefix=PREFIX,
				description=DESCRIPTION,
				case_insensitive=True,
				intents=intents
			)
			
			self._memory = Memory()
			self.muted = []
			Cypher.instance = self
		
	def remember(self, guild, author, event_type, payload):
		self._memory.remember(MemoryEvent(guild, author, event_type, payload))
	
	async def load_memory_from(self, file_path):
		io = JsonIO(globals())
		self._memory = await io.finalize_async_loading(io.load(file_path, global_arguments=Globals(bot=self)))
	
	def dump_memory_in(self, file_path):
		io = JsonIO(globals())
		io.dump(self._memory, file_path, indent=4)
	
	def fetch_memory_event(self,
	                guild_id=None,
	                author_id=None,
	                event_type=None,
	                check=lambda x: True,
	                from_oldest_to_newest=False):
		
		overall_check = lambda e: (
			(guild_id is None or e.guild.id == guild_id) and
			(author_id is None or e.author.id == author_id) and
			(event_type is None or e.event_type == event_type) and
			check(e)
		)
		
		for event in (self._memory if from_oldest_to_newest else reversed(list(self._memory))):
			if overall_check(event):
				return event
			
