# key2pane

[![Tests](https://github.com/BartSte/tmux-key2pane/actions/workflows/test.yml/badge.svg)](https://github.com/BartSte/tmux-key2pane/actions/workflows/test.yml)

Sends a sequence of keys to any tmux pane, based on the pane's current command.

## Contents

<!--toc:start-->

- [Contents](#contents)
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

<!--toc:end-->

## Introduction

`key2pane` is a tmux plugin for sending a sequence of keys to a tmux pane, based
on the target pane's command that is running. Which keys are sent can be
configured in a json file:

```json
{
  // Other settings ...

  "actions": [
    {
      "regex": "bash|zsh|fish",
      "keys": ["echo 'Hello, World!'", "Enter"]
    }
  ]
}
```

When the command of the target pane matches the regex, the keys are sent to the
pane. In this case, the command: `echo 'Hello, World!'` is sent to the pane, and
then the `Enter` key is sent.

** TODO: Add a demo gif here **

## Installation

Install `key2pane` using pip:

```sh
pip install key2pane
```

which panel will install the `key2pane` command.

## Usage

Expanding on the example in the [introduction](#introduction), consider the
following configuration:

```json
{
  // Other settings ...

  "session": "test",
  "window": 0,
  "index": 0,
  "actions": [
    {
      "regex": "bash|zsh|fish",
      "keys": ["echo '{0} {1}'", "Enter"]
    }
  ]
}
```

When we run the `key2pane foo bar` command, the following will happen:

- For the session `test`, window `0`, and pane `0`, the command is retrieved.
- If this command matches the regex `bash|zsh|fish`, the keys `echo '{0} {1}'`
  are selected.
- The placeholders `{0}` and `{1}` are replaced with the positional arguments
  `foo` and `bar`.
- The formatted keys are send to the pane, using `tmux send-keys`. After that,
  the `Enter` key is sent.
- As a result, the command `echo 'foo bar'` is executed in the pane.

## Configuration

When you run the `key2pane` command for the first time, no configuration file
is exists yet. You need to create a configuration file in the default location
`~/.config/key2pane/config.json`, or specify a different location using the
`--config` option. As a starting point, you can use the following example:

```json
{
  "session": null,
  "window": null,
  "index": null,
  "reset": false,
  "logfile": null,
  "loglevel": null,
  "actions": [
    {
      "regex": "bash|zsh|fish",
      "keys": ["echo '{0}'", "Enter"]
    },
    {
      "regex": "python[0-9]*",
      "keys": ["print('{0}')", "Enter"]
    }
  ]
}
```

Since comments are not allowed in JSON, notes are placed here:

- **session**: the session name. Default: current session.
- **window**: the window index. Default: current window.
- **index**: the pane index. Default: current pane.
- **reset**: send a Ctrl-C before sending the keys. Default: false
- **logfile**: the log file. Default: ~/.local/state/key2pane/key2pane.log
- **loglevel**: the log level. Default: WARNING
- **actions**: a list of actions, containing a `regex`, and a `keys` property.
  The `keys` are send to the target pane when the `regex` matches the command
  of the target pane.

## Troubleshooting

If you encounter any issues, please report them on the issue tracker at:
[tmux-key2pane issues](https://github.com/BartSte/tmux-key2pane/issues)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING](./CONTRIBUTING.md) for
more information.

## License

Distributed under the [MIT License](./LICENCE).
