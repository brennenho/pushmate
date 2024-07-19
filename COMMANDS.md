# PushMate Commands

PushMate: automate your git workflow with AI.

**Usage**:

```console
$ pm [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `commit`: Automatically generate a git commit based on the currently staged changes.
* `config`: Set or view PushMate configuration options.
* `pr`: Automatically generate a GitHub pull request based on the currently branch's HEAD.

## `pm commit`

Automatically generate a git commit based on the currently staged changes.

**Usage**:

```console
$ pm commit [OPTIONS]
```

**Options**:

* `--max-chars INTEGER`: Override default # of max characters for the commit message.
* `--help`: Show this message and exit.

## `pm config`

Set or view PushMate configuration options.

**Usage**:

```console
$ pm config [OPTIONS] [VALUE]
```

**Arguments**:

* `[VALUE]`: The value to set an option to. Leave blank to view the current value.

**Options**:

* `--provider`: Provider to use for LLM calls.
* `--max-changes`: Maximum # of changes to automatically include in a commit message. Files with more changes will be prompted for inclusion. (Default: 500)
* `--max-chars`: Maximum # of characters for a commit message. (Default: 50)
* `--github-token`: GitHub API Token.
* `--openai`: OpenAI API Key.
* `--help`: Show this message and exit.

## `pm pr`

Automatically generate a GitHub pull request based on the currently branch's HEAD.

**Usage**:

```console
$ pm pr [OPTIONS]
```

**Options**:

* `--branch TEXT`: The branch to pull request against. Leave blank to use the default branch.
* `--help`: Show this message and exit.
