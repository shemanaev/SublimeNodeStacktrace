import sublime, sublime_plugin

from .. import config
from .. import globals
from .. import logger
from ..debug_client import DebugClient

log = logger.get('cmd_attach_debugger')

# TODO: implement `lookup_view` func
def trace_callback(data):
	globals.st.run_command('node_debugger_insert_text', {'pos': 0, 'text': str(data)})

def exception_callback(data):
	log('exception', data)
	body = data['body']
	window = sublime.active_window()
	if config.get('modify_layout'):
		window.set_layout(config.get('debug_layout'))
	# Create new buffer for stacktrace
	globals.st = st = window.new_file()
	st.set_scratch(True)
	st.set_name(config.get('stacktrace_name'))
	window.set_view_index(st, 1, 0)
	# Request backtrace
	globals.client.execute('backtrace', trace_callback, inlineRefs=True)
	# Open file with error
	filename = '%s:%d:%d' % (body['script']['name'], body['sourceLine'] + 1, body['sourceColumn'] + 1)
	src = window.open_file(filename, sublime.ENCODED_POSITION)
	window.set_view_index(src, 0, 0)
	src.set_status('node_error', body['exception']['text'])

def after_compile_callback(data):
	pass

def disconnect_handler(e):
	log('disconnect_handler', e)
	globals.client = None

class NodeDebuggerAttachCommand(sublime_plugin.ApplicationCommand):
	def run(self):
		if globals.client:
			globals.client.close()

		address = config.get('address')
		try:
			globals.original_layout = sublime.active_window().get_layout()

			globals.client = client = DebugClient(address)
			client.on_disconnect(disconnect_handler)
			client.add_handler('break', exception_callback)
			client.add_handler('exception', exception_callback)
			client.add_handler('afterCompile', after_compile_callback)
			client.execute_sync('setexceptionbreak', lambda data: client.execute('continue'), type='uncaught', enabled=True)
		except (IOError) as e:
			log('Error connecting to %s' % address, e)
			message = 'Node Debugger: Error connecting to node.js instance at %s' % address
			sublime.error_message(message)
