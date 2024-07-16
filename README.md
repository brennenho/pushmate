# `pm`

A CLI utilizing LLMs for git commits and PRs

**Usage**:

```console
$ pm [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `commit`: Generate a commit message
* `config`: View and set configuration options
* `pr`: Generate a pull request
* `test`: Test command

## `pm commit`

Generate a commit message

**Usage**:

```console
$ pm commit [OPTIONS]
```

**Options**:

* `--max-chars INTEGER`: Override default # of max characters for the commit message.
* `--help`: Show this message and exit.

## `pm config`

View and set configuration options

**Usage**:

```console
$ pm config [OPTIONS] [VALUE]
```

**Arguments**:

* `[VALUE]`: If provided, will be set as config value. Leave blank to view the current value.

**Options**:

* `--provider / --no-provider`: The LLM provider to use
* `--max-changes / --no-max-changes`: Maximum # of changes per file. Files with more changes will not be summarized. (Default: 500)
* `--max-chars / --no-max-chars`: Maximum # of characters the commit message should be (Default: 80)
* `--github-token / --no-github-token`: GitHub token to use for PRs
* `--openai / --no-openai`: OpenAI API Key
* `--help`: Show this message and exit.

## `pm pr`

Generate a pull request

**Usage**:

```console
$ pm pr [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `pm test`

Test command

**Usage**:

```console
$ pm test [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.
