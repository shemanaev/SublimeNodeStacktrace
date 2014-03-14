import sublime_plugin

class NodeDebuggerInsertTextCommand(sublime_plugin.TextCommand):
	def run(self, edit, text):
		self.view.insert(edit, 0, text)
