import sublime

def get(key):
	# Config MUST be loaded here
	config = sublime.load_settings('node stacktrace.sublime-settings')
	return config.get(key)
