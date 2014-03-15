import sublime

def get(key):
	# Config MUST be loaded here
	config = sublime.load_settings('Node Debugger.sublime-settings')
	return config.get(key)
