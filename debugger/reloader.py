import sys

from imp import reload
from .mod_prefix import prefix

reload_mods = []
for mod in sys.modules:
	if mod[0:len(prefix)] == prefix and sys.modules[mod] != None:
		reload_mods.append(mod)

mods_load_order = [
	'',
	'.debugger.globals',
	'.debugger.debug_client'
]

for suffix in mods_load_order:
	mod = prefix + suffix
	if mod in reload_mods:
		reload(sys.modules[mod])
