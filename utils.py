def map_dict(function, dct):
	result = {}
	for key, value in dct.items():
		result[key] = function(value)
	return result
