import json
from abc import ABC, abstractmethod
from re import compile

from utils import map_dict

COMPONENT_FLAG = "__component__"
STRING_REGEX = compile("'\w[\w0-9 ]*'")


class Globals:
	def __init__(self, **storage):
		self._storage = storage
		
	def require(self, item):
		value = self._storage.get(item)
		if value is None:
			raise NameError(f"A {item} argument seems to be required to decode the json file. Make sure you provided it.")
		return value
	

class JsonIOSupporter(ABC):
	@classmethod
	@abstractmethod
	def __load__(cls, gbls, **kwargs): ...
	
	@abstractmethod
	def __dump__(self): ...
	
	class __Dumper:
		def __init__(self, parent):
			self._fields = {COMPONENT_FLAG: parent.__class__.__name__}
			self._parent_dict = parent.__dict__
			
		def add(self, *fields, transform=lambda x: x):
			for field in fields:
				
				field_value = self._parent_dict.get(field)
				if field_value is None:
					raise NameError("Unknown field %s for class %s" % (field, self._fields[COMPONENT_FLAG]))
				
				if isinstance(field_value, JsonIOSupporter):
					if transform(field) is not field:
						raise ValueError("JsonIOSupporter aren't supposed to be transformed")
					field_value = field_value.__dump__()
				else:
					field_value = transform(field_value)
					
				self.create_field(field.lstrip("_"), field_value)
				
		def create_field(self, field, value):
			field_type = type(value).__name__
			
			if field_type == "str":
				self._fields[field] = value
			elif field_type == "list":
				self._fields[field] = [it.__dump__() if isinstance(it, JsonIOSupporter) else it for it in value]
			elif field_type == "dict":
				self._fields[field] = map_dict(lambda it: it.__dump__() if isinstance(it, JsonIOSupporter) else it, value)
			else:
				self._fields[field] = f"<{field_type}>{value}"
		
		def to_dict(self):
			return self._fields
	
	def _get_dumper(self):
		return JsonIOSupporter.__Dumper(self)
	

class LoadAsync:
	def __init__(self, loader):
		self._loader = loader
		
	async def load(self):
		return await self._loader()


class JsonIO:
	cast_regex = compile("(<(?P<data_type>\w[\w0-9]*)>)?(?P<raw_data>.*)")
	
	def __init__(self, scope):
		self._scope = scope
	
	def _cast_data(self, data):
		match = self.cast_regex.match(data)
		data_type = match.group("data_type")
		raw_data = match.group("raw_data")
		
		if data_type:
			return eval(data_type)(raw_data)
		
		return raw_data
	
	def hook(self, dct, global_arguments):
		
		for key, value in dct.items():
			if isinstance(value, str):
				dct[key] = self._cast_data(value)
		
		if dct.get(COMPONENT_FLAG):
			component_name = dct[COMPONENT_FLAG]
			try:
				component_class = eval(component_name, self._scope)
			except NameError as e:
				raise NameError("Cannot load component %s" % component_name) from e
			
			dct.pop(COMPONENT_FLAG)
			
			if not issubclass(component_class, JsonIOSupporter):
				raise TypeError("Component %s isn't a JsonIOSupporter subclass" % component_name)
			try:
				return component_class.__load__(gbls=global_arguments, **dct)
			except TypeError as e:
				if not "got an unexpected keyword argument" in str(e):
					raise
				
				raise TypeError("Cannot load component %s with argument %s" % (component_name, STRING_REGEX.search(str(e)).group())) from None
		
		return dct
	
	def prepare(self, obj):
		if isinstance(obj, dict):
			dct = obj
		else:
			dct = obj.__dump__()
		
		for key, value in dct.items():
			if isinstance(value, JsonIOSupporter):
				dct[key] = value.__dump__()
			elif isinstance(value, dict):
				dct[key] = self.prepare(value)
		return dct
	
	def load(self, file_path, *args, global_arguments=None, **kwargs):
		with open(file_path, "r") as file:
			return json.load(file, *args, **kwargs, object_hook=lambda obj: self.hook(obj, global_arguments or Globals()))
	
	def dump(self, obj, file_path, *args, **kwargs):
		result = json.dumps(self.prepare(obj), *args, **kwargs)
		with open(file_path, "w") as file:
			file.write(result)
	
	def dump_as(self, obj, name, file_path, *args, **kwargs):
		result = json.dumps(self.prepare({name: obj}), *args, **kwargs)
		with open(file_path, "w") as file:
			file.write(result)
	
	async def finalize_async_loading(self, obj):
		if isinstance(obj, dict):
			result = {}
			for key, value in obj.items():
				result[key] = await self.finalize_async_loading(value)
			return result
		
		elif isinstance(obj, list):
			result = []
			for item in obj:
				result.append(await self.finalize_async_loading(item))
			return result
		
		elif isinstance(obj, LoadAsync):
			return await obj.load()
		
		else:
			return obj
		