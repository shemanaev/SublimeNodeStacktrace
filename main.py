import sys

# Disconnect from active session if any
from .node_debugger import globals
if globals.client:
	globals.client.disconnect()

# Make sure that ST3 updates all our modules
from .node_debugger.mod_prefix import full_prefix
reloader_name = full_prefix + '.reloader'
if reloader_name in sys.modules:
	from imp import reload
	reload(sys.modules[reloader_name])


from .node_debugger import reloader
from .node_debugger.commands import *
