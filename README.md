# Sublime node.js stacktrace

It's purpose: display stacktrace in handy way on uncaught exceptions.
Just run your script with `ctrl+b` when build system is 'node stacktrace'. See the demo below:

![SublimeNodeStarcktrace](https://dl.dropboxusercontent.com/u/8021778/img/sublime_node_stacktrace.gif)

You also can attach to any node process that was run with `--debug-brk` flag by adding some keybinding:

```
[
...
  { "keys": ["alt+a"], "command": "node_debugger_attach" }
...
]
```

## Installation

#### Git
Clone the repository by executing the following command in your Packages directory:
```git clone https://github.com/DeniSix/SublimeNodeStacktrace.git NodeStacktrace```

#### Download
Get the latest [source from GitHub](https://github.com/DeniSix/SublimeNodeStacktrace/archive/master.zip), extract the source into your Packages directory and rename directory to `NodeStacktrace`.

## Limitations

* node.js version at least 0.11.3 (you can't handle `uncaughtException` by debugger in earlier versions)
* scripts must be run with `node --debug-brk script.js` (there is build system for that)
* you can't view internal node.js libraries (like `net.js`, `timers.js`, etc...)

## License

[MIT](http://opensource.org/licenses/MIT)
