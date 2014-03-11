import sublime, sublime_plugin

import sys
import json
import queue
import socket
import threading

# Make sure that ST3 updates all our modules
from .debugger.mod_prefix import prefix
reloader_name = prefix + '.debugger.reloader'
if reloader_name in sys.modules:
	from imp import reload
	reload(sys.modules[reloader_name])


from .debugger import reloader
from .debugger import globals
from .debugger import debug_client


class NodeDebuggerView(object):
	def __init__(self, view, reader):
		self._view = view
		self._reader = reader
		self.update_view_loop()

	def update_view_loop(self):
		is_still_working = self.handle_repl_output()
		if is_still_working:
			sublime.set_timeout(self.update_view_loop, 100)
		else:
			self.write("\n***Repl Closed***\n")
			self._view.set_read_only(True)

	def handle_repl_output(self):
		"""Returns new data from Repl and bool indicating if Repl is still
			 working
		"""
		try:
			while True:
				packet = self._reader.get_reply()
				if packet is None:
					# sublime.error_message('Connection closed')
					return False

				self.handle_repl_packet(packet)

		except queue.Empty:
			return True

	def handle_repl_packet(self, packet):
		self.write(packet)

	def write(self, unistr):
		"""Writes output from Repl into this view."""
		pass

class RunNodeDebuggerCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if not globals.client is None:
			globals.client.execute('listbreakpoints')
			return

		try:
			globals.client = debug_client.DebugClient()
			NodeDebuggerView(self.view, globals.client)

			globals.client.execute('scripts')
		except (IOError) as e:
			message = 'Error connecting to %s\n%s' % ('127.0.0.1', e)
			sublime.error_message(message)
