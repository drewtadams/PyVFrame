from functools import wraps


def ignore(ignore_except=Exception, default_val=None):
	"""
	Ignores any exception and provides a default return value

	Parameters:
	ignore_except (Exception, optional): exception to be caught
	default_val (object, optional): value to be returned if exception is caught

	Returns:
	wrapped function's value if no exception is caught, otherwise default_val
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except ignore_except:
				return default_val
		return wrapper
	return decorator