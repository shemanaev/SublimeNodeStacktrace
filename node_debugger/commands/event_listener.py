import sublime, sublime_plugin

from .. import config
from .. import globals

class EventListener(sublime_plugin.EventListener):
	def on_modified_async(self, view):
		view.erase_status('node_error')

	def on_close(self, view):
		view.erase_status('node_error')
		if config.get('modify_layout') and view.name() == config.get('stacktrace_name'):
			sublime.active_window().set_layout(globals.original_layout)
