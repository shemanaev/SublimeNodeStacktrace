import sublime, sublime_plugin

from .. import globals
from .. import debug_client

class AttachDebuggerCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not globals.client is None:
			globals.client.execute('listbreakpoints')
			return

		try:
			globals.client = debug_client.DebugClient()

			globals.client.execute('scripts')
		except (IOError) as e:
			message = 'Error connecting to %s\n%s' % ('127.0.0.1', e)
			sublime.error_message(message)
