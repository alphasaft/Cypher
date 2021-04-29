import discord
from typing import Any, Dict
from enum import Enum, auto
from dataclasses import dataclass

from .io import JsonIOSupporter, LoadAsync


class EventType(Enum):
	PUBLISH = auto()
	MESSAGE_POST = auto()
	MESSAGE_EDIT = auto()
	REACTION_ADD = auto()
	REACTION_REMOVE = auto()


class Memory(JsonIOSupporter):
	def __init__(self, items=None, size=100):
		self._items = items or []
		self._size = size
		
	def remember(self, item):
		self._items.append(item)
		if len(self._items) > self._size:
			self._items.pop(0)
		return item
	
	def __iter__(self):
		return self._items.__iter__()
	
	def filter(self, key):
		return filter(key, self)
	
	def __dump__(self):
		dumper = self._get_dumper()
		dumper.add("_items")
		dumper.add("_size")
		return dumper.to_dict()
	
	@classmethod
	def __load__(cls, gbls, items, size):
		async def async_loader():
			return Memory([await it.load() for it in items], size)
		return LoadAsync(async_loader)


@dataclass
class MemoryEvent(JsonIOSupporter):
	guild: discord.Guild
	author: discord.Member
	event_type: EventType
	payload: Dict[str, JsonIOSupporter]
	
	def __dump__(self):
		dumper = self._get_dumper()
		dumper.create_field("guild_id", self.guild.id)
		dumper.create_field("author_id", self.author.id)
		dumper.create_field("event_name", self.event_type.name)
		dumper.add("payload", transform=lambda p: {key: DiscordObject(value) for key, value in p.items()})
		return dumper.to_dict()

	@classmethod
	def __load__(cls, gbls, guild_id, author_id, event_name, payload):
		bot = gbls.require("bot")
		
		async def async_loader():
			guild = bot.get_guild(guild_id) ; assert guild is not None
			author = bot.get_user(author_id) ; assert author is not None
			event_type = [it for it in EventType if it.name == event_name][0]
			loaded_payload = {key: await value.load() for key, value in payload.items()}
			
			return MemoryEvent(
				guild,
				author,
				event_type,
				loaded_payload
			)
		
		return LoadAsync(async_loader)
		

class DiscordObject(JsonIOSupporter):
	def __init__(self, obj):
		self._obj = obj
	
	@classmethod
	def __load__(cls, gbls, type, **kwargs):
		async def async_load():
			bot = gbls.require("bot")
			
			if type == "Message":
				return await bot.get_channel(kwargs["channel_id"]).fetch_message(kwargs["id"])
			elif type == "Raw":
				return kwargs["value"]
		
		return LoadAsync(async_load)
			
	
	def __dump__(self):
		dumper = self._get_dumper()
		
		if isinstance(self._obj, discord.Message):
			dumper.create_field("type", "Message")
			dumper.create_field("channel_id", self._obj.channel.id)
			dumper.create_field("id", self._obj.id)
		else:
			dumper.create_field("type", "Raw")
			dumper.create_field("value", self._obj)
		
		return dumper.to_dict()
		
		
	
