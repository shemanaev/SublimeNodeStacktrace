import sublime

config = sublime.load_settings('Node Debugger.sublime-settings')

def get(key):
	return config.get(key)
