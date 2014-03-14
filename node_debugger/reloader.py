import sys

from imp import reload
from .globals import prefix, full_prefix

reload_mods = []
for mod in sys.modules:
	if mod[0:len(prefix)] == prefix and sys.modules[mod] != None:
		reload_mods.append(mod)

mods_load_order = [
	'',

	'.logger',
	'.config',
	'.globals',
	'.clicks',
	'.debug_client',

	'.commands',
	'.commands.attach_debugger',
	'.commands.start_debugger',
	'.commands.insert_text',
	'.commands.event_listener',
]

for suffix in mods_load_order:
	mod = full_prefix + suffix
	if mod in reload_mods:
		reload(sys.modules[mod])
