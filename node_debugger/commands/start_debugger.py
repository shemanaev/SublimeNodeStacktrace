import sublime, sublime_plugin

from .. import logger

log = logger.get('cmd_start_debugger')

class NodeDebuggerStartCommand(sublime_plugin.WindowCommand):
	def run(self, shell_cmd):
		self.window.run_command('exec', {'shell_cmd': shell_cmd})
		self.window.run_command('node_debugger_attach')
