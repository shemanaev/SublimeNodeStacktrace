import json
import queue
import socket
import threading

import sublime

from . import globals

class DebugClient(object):
	"""Implementation of V8 debug protocol client."""

	def __init__(self):
		self._reqId = 0
		self._callbacks = {}
		self._event_handlers = {}
		self._conn = socket.create_connection(("127.0.0.1", 5858))
		self._reader = DebugReader(self, self._conn)
		self._reader.start()

	def _invoke_callback(self, data):
		cb = self._callbacks[data['request_seq']]
		if not cb is None:
			cb(data)

	def _invoke_event(self, data):
		cb = self._event_handlers[data['command']]
		if not cb is None:
			cb(data)

	def _make_request(self, data):
		"""Generate request data."""

		jsonData = json.dumps(data)
		buf = 'Content-Length: ' + str(len(jsonData)) + '\r\n\r\n' + jsonData
		return bytes(buf, 'utf8')

	def execute(self, command, args=None, callback=None):
		"""Execute remote V8 debugger command."""

		data = {}
		data['seq'] = self._reqId
		data['type'] = 'request'
		data['command'] = command
		if not args is None:
			data['arguments'] = args
		if not callback is None:
			self._callbacks[self._reqId] = callback

		self._reqId = self._reqId + 1

		buf = self._make_request(data)
		self._conn.send(buf)

	def get_reply(self):
		"""Get reply from V8 debugger."""

		return self._reader.queue.get_nowait()

	def close(self):
		"""Close connection to debugger."""

		# self.execute('disconnect')
		self._reader._stop()
		self._conn.close()

	def add_handler(self, event, callback):
		"""Register handler for debugger event"""
		self._event_handlers[event] = callback


class DebugReader(threading.Thread):
	"""Reads debugger replies in another thread."""

	def __init__(self, client, conn):
		super(DebugReader, self).__init__()
		self.conn = conn
		self.daemon = True
		self.queue = queue.Queue()

	def run(self):
		c = self.conn
		q = self.queue
		buf = b''
		length = 0
		needHeaders = True
		while True:
			try:
				data = c.recv(4 * 1024)
			except (IOError) as e:
				sublime.error_message('Connection closed: %s' % e)
				if globals.client: globals.client.close()
				globals.client = None
				data = None
			if data is None:
				q.put(data)
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
				print('[DEBUG]', 'Headers', headers)

			if not needHeaders:
				if len(buf) != length: continue
				# JSON body received
				tmp = buf.decode('utf8')
				if len(tmp) > 0:
					# print('[DEBUG]', 'RAW', buf)
					# TODO: handle json errors
					tmp = json.loads(tmp)
					q.put(tmp)
					if tmp['type'] == 'response':
						client._invoke_callback(tmp)
					else: # type: 'event'
						client._invoke_event(tmp)
				print('[DEBUG]', 'Data', tmp)
				buf = b''
				needHeaders = True
