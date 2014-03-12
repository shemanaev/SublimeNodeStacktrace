import sublime, sublime_plugin

from .. import globals
from .. import logger
from .. import debug_client

log = logger.get('cmd_attach_debugger')

def scripts_callback(data):
	# globals.scripts = data['body']
	log('cb', data)

def exception_callback(data):
	# globals.scripts = data['body']
	log('exception', data)

def disconnect_handler(e):
	if globals.client: globals.client.close()
	globals.client = None
	log('disconnect_handler')

class AttachDebuggerCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# print(globals.client)
		if not globals.client is None:
			globals.client.execute('listbreakpoints')
			return

		try:
			globals.client = client = debug_client.DebugClient()

			client.add_handler('exception', exception_callback)
			client.on_disconnect(disconnect_handler)
			# client.execute('scripts', None, scripts_callback)
			client.execute('setexceptionbreak', type='uncaught', enabled=True)
			client.execute('backtrace', scripts_callback, True, inlineRefs=True)
		except (IOError) as e:
			# message = 'Error connecting to %s\n%s' % ('127.0.0.1', e)
			# sublime.error_message(message)
			log('Error connecting to %s' % '127.0.0.1', e)
