import sys
import sublime, sublime_plugin

# Disconnect from active session if any
from .node_debugger import globals
if globals.client:
	globals.client.close()

# Make sure that ST3 updates all our modules
reloader_name = globals.full_prefix + '.reloader'
if reloader_name in sys.modules:
	from imp import reload
	reload(sys.modules[reloader_name])

from .node_debugger import reloader
from .node_debugger.commands import *
