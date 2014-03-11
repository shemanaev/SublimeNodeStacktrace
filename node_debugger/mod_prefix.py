from os import path

# Get package prefix for our modules.
# Basically, it's just plugin root directory name.
# Holy sh.. Crappy, but dunno better way for now
prefix = path.basename(path.normpath(path.join(path.dirname(__file__), '..')))

full_prefix = prefix + '.node_debugger'
