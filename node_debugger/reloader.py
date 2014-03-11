import sys

from imp import reload
from .mod_prefix import prefix, full_prefix

reload_mods = []
for mod in sys.modules:
	if mod[0:len(prefix)] == prefix and sys.modules[mod] != None:
		reload_mods.append(mod)

mods_load_order = [
	'',

	'.node_debugger',
	'.node_debugger.globals',
	'.node_debugger.debug_client',

	'.commands',
	'.commands.attach_debugger'
]

for suffix in mods_load_order:
	mod = full_prefix + suffix
	if mod in reload_mods:
		reload(sys.modules[mod])