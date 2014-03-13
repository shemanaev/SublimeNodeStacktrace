import json
import socket
import threading

from . import logger

log = logger.get('debug_client')

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 5858

class DebugClient(object):
	"""Implementation of V8 debug protocol client."""

	def __init__(self, address=None):
		self._reqId = 0
		self._on_disconnect = None
		self._callbacks = {}
		self._event_handlers = {}
		self._conn = socket.create_connection(self._parse_address(address))
		self._reader = DebugReader(self)
		self._reader.start()

	def _parse_address(self, address):
		"""Convert address string into tuple."""
		if address is None:
			return (DEFAULT_IP, DEFAULT_PORT)
		idx = address.find(':')
		if idx != -1:
			return (address[:idx], int(address[idx + 1:]))
		return (address, DEFAULT_PORT)

	def _invoke_callback(self, data):
		log('_invoke_callback', data)
		try:
			c = self._callbacks
			k = data.get('request_seq', data['command'])
			c[k](data)
			del c[k]
		except (Exception) as e:
			log('_invoke_callback', 'Callback not found', e)

	def _invoke_event(self, data):
		log('_invoke_event', data)
		try:
			c = self._event_handlers
			k = data['event']
			c[k](data)
		except (Exception) as e:
			log('_invoke_event', 'Event handler not found', e)

	def _make_request(self, data):
		"""Generate request data."""
		jsonData = json.dumps(data)
		buf = 'Content-Length: ' + str(len(jsonData)) + '\r\n\r\n' + jsonData
		return bytes(buf, 'utf8')

	def _execute(self, command, callback, sync, args):
		log('execute', command, args, callback)
		data = {}
		data['seq'] = self._reqId
		data['type'] = 'request'
		data['command'] = command
		if args:
			data['arguments'] = args
		if callback:
			c = self._callbacks
			if sync:
				c[command] = callback
			else:
				c[self._reqId] = callback

		self._reqId = self._reqId + 1
		buf = self._make_request(data)
		log('sent', buf)
		self._conn.send(buf)

	# TODO: optional context for callback?
	def execute(self, command, callback=None, **args):
		"""Execute remote V8 debugger command."""
		self._execute(command, callback, False, args)

	def execute_sync(self, command, callback=None, **args):
		"""Execute remote V8 debugger command with broken `request_seq`."""
		if command in self._callbacks:
			raise Exception('Previous callback for sync command `%s` not fired yet!' % command)
		self._execute(command, callback, True, args)

	def close(self):
		"""Disconnect from active debugger session and close connection."""
		try:
			self.execute('disconnect')
		except:
			pass
		self._stop_all()

	def _stop_all(self):
		self._reader.stop()
		self._conn.close()

	def _disconnected(self, e):
		cb = self._on_disconnect
		if cb:
			cb(e)
		self._stop_all()

	def on_disconnect(self, callback):
		"""Register handler for `disconnect` event."""
		self._on_disconnect = callback

	def add_handler(self, event, callback):
		"""Register handler for debugger event."""
		self._event_handlers[event] = callback


class DebugReader(threading.Thread):
	"""Reads debugger replies in another thread."""

	def __init__(self, client):
		super(DebugReader, self).__init__()
		self._client = client
		self.daemon = True

	def stop(self):
		self.alive = False

	def run(self):
		c = self._client
		buf = b''
		length = 0
		needHeaders = True
		self.alive = True
		while self.alive:
			try:
				data = c._conn.recv(4 * 1024)
			except (IOError) as e:
				log('Connection closed', e)
				c._disconnected(e)
				break

			buf = buf + data

			if needHeaders:
				index = buf.find(b'\r\n\r\n')
				if index == -1: continue
				# Headers fully received
				headers = {}
				tmp = buf[:index].decode('utf8').splitlines()
				buf = buf[index + 4:]
				for line in tmp:
					t = line.split(': ')
					headers[t[0]] = t[1]
				needHeaders = False
				length = int(headers['Content-Length'])
				log('Headers', headers)

			if not needHeaders:
				if len(buf) != length: continue
				# JSON body received
				tmp = buf.decode('utf8')
				log('Data', tmp)
				if len(tmp) > 0:
					# TODO: handle json errors
					tmp = json.loads(tmp)
					if tmp['type'] == 'response':
						c._invoke_callback(tmp)
					else: # type: 'event'
						c._invoke_event(tmp)
				buf = b''
				needHeaders = True
