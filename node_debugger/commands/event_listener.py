import sublime, sublime_plugin
import time

from .. import config
from .. import globals

timing = time.time()

class EventListener(sublime_plugin.EventListener):
	def on_modified_async(self, view):
		view.erase_status('node_error')

	def on_close(self, view):
		view.erase_status('node_error')
		if config.get('show_stacktrace') and view.name() == config.get('stacktrace_name'):
			sublime.active_window().set_layout(globals.original_layout)

	def on_selection_modified(self, view):
		global timing
		if view.name() == config.get('stacktrace_name'):
			cursor = view.sel()[0].a
			globals.clicks.check(cursor)
