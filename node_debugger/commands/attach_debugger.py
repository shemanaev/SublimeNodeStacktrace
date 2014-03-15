import sublime, sublime_plugin

from .. import config
from .. import globals
from .. import logger
from ..debug_client import DebugClient
from ..clicks import Clicks

log = logger.get('cmd_attach_debugger')

def lookup_ref(id, refs):
	for ref in refs:
		if id == ref['handle']:
			return ref
	return None

def open_file(data):
	if '/' not in data['script'].replace('\\', '/'):
		print('[NDBG] Internal scripts (%s) doesn\'t supported for now. Sorry :(' % data['script'])
		return
	# TODO: fetch node's internal scripts with `scripts` request
	window = sublime.active_window()
	filename = '%s:%d:%d' % (data['script'], data['line'], data['column'])
	src = window.open_file(filename, sublime.ENCODED_POSITION)
	window.set_view_index(src, 0, 0)
	if 'exception' in data:
		src.set_status('node_error', data['exception'])

def trace_callback(data):
	body = data['body']
	refs = data['refs']
	trace = []
	funcLen = 0
	for frame in body['frames']:
		func = frame['func']['name'] or frame['func']['inferredName'] or 'Anonymous'
		script = lookup_ref(frame['script']['ref'], refs)
		trace.append({'func': func, 'script': script['name'], 'line': int(frame['line']) + 1, 'column': int(frame['column']) + 1})
		l = len(func)
		if funcLen < l:
			funcLen = l

	text = '%s\n' % globals.exception
	globals.exception = None
	for line in trace:
		s = '\t%s (%s:%d:%d)\n' % (line['func'].ljust(funcLen), line['script'], line['line'], line['column'])
		globals.clicks.add(sublime.Region(len(text), len(text + s)), open_file, line)
		text = text + s
	globals.st.run_command('node_debugger_insert_text', {'text': text})

def exception_callback(data):
	log('exception', data)
	body = data['body']
	window = sublime.active_window()
	if config.get('show_stacktrace'):
		globals.exception = body['exception']['text']
		window.set_layout(config.get('debug_layout'))
		# Create new buffer for stacktrace
		globals.st = st = window.new_file()
		st.set_scratch(True)
		st.set_name(config.get('stacktrace_name'))
		st.settings().set('word_wrap', False)
		st.settings().set('syntax', 'Packages/' + globals.prefix + '/node stacktrace.tmLanguage')
		window.set_view_index(st, 1, 0)
		# Request backtrace
		globals.client.execute('backtrace', trace_callback, inlineRefs=True)

	# Open file with error
	open_file({'script': body['script']['name'], 'line': body['sourceLine'] + 1, 'column': body['sourceColumn'] + 1, 'exception': body['exception']['text']})

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
			globals.clicks = Clicks()

			globals.client = client = DebugClient(address)
			client.on_disconnect(disconnect_handler)
			# client.add_handler('break', exception_callback)
			client.add_handler('exception', exception_callback)
			client.add_handler('afterCompile', after_compile_callback)
			client.execute_sync('setexceptionbreak', lambda data: client.execute('continue', lambda x: str(1)), type='uncaught', enabled=True)
		except (IOError) as e:
			log('Error connecting to %s' % address, e)
			message = 'Node Debugger: Error connecting to node.js instance at %s' % address
			sublime.error_message(message)
