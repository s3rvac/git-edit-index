git-edit-index
==============

[![Build Status](https://github.com/s3rvac/git-edit-index/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/s3rvac/git-edit-index/actions/workflows/tests.yml?query=branch%3Amaster)
[![Coverage Status](https://coveralls.io/repos/github/s3rvac/git-edit-index/badge.svg?branch=master)](https://coveralls.io/github/s3rvac/git-edit-index?branch=master)
[![PyPI Version](https://badge.fury.io/py/git-edit-index.svg)](https://pypi.python.org/pypi/git-edit-index)

This command represents a faster alternative to `git add -i` or `git gui`. It
allows you to stage or unstage files from the index in an editor, just like
when you perform an interactive rebase.

![Screencast](resources/screencast.gif "git-edit-index in action")

For example, let's assume you have the following three modified files (`git
status --short`):

    M path/to/file1
    M another/path/to/file2
    M yet/another/path/to/file3

After running `git edit-index`, an editor will show up with the above output.
To stage (add) the first two files, simply change the text to

    A path/to/file1
    A another/path/to/file2
    M yet/another/path/to/file3

You can also unstage (`reset`) files, add only parts of files (`add -p`), or
delete files (`rm`).

Requirements
------------

The script requires Python 2.7 or Python >= 3.7. Both CPython and PyPy
implementations are supported.

Installation
------------

Either install the script from [Python Package
Index](https://pypi.python.org/pypi/git-edit-index) (PyPI) with
[pip](http://www.pip-installer.org/):

    $ pip install git-edit-index

or install it manually by performing the following two steps:
* Put the
  [`git-edit-index`](https://raw.githubusercontent.com/s3rvac/git-edit-index/master/git-edit-index)
  script to a directory that is in your `$PATH`.
* Ensure that the script is executable (`chmod a+x git-edit-index`).

Usage
-----

Run `git edit-index` to display an editor with the current index. In it, you
can stage or unstage files from the index simply by changing their status:

* To stage a modified or deleted file, change its status from `M` or `D` to
  `A`. This runs `git add FILE`. If you use `P` instead of `A`, it will run
  `git add -p FILE` instead.
* To unstage a modified file, change its status from `A` to `M`. This runs `git
  reset FILE`.
* To unstage a deleted file, change its status from `A` to `D`. This also runs
  `git reset FILE`. If you use `P` instead of `D`, it will run `git reset -p
  FILE` instead.
* To add an untracked file, change its status from `?` to `A`. This runs `git
  add FILE`.
* To stop tracking of a file, change its status to `?`. This runs `git rm
  --cached FILE`.
* To add an ignored file, change its status from `!` to `A`. This runs `git add
  -f FILE`.
* To delete an untracked or ignored file, remove the line with the file. This
  deletes the file by using the operating system's file-deletion facilities.
* To revert changes done to a file since the last commit, remove the line with
  the file. This runs `git checkout FILE` (if the file is staged, it first runs
  `git reset FILE`).

The status is case-insensitive, e.g. both `A` and `a` stage the given file
(lower-case letters are easier to type).

As with `git status`, ignored files aren't being shown by default,
instead the flag `--ignored` has to be set.

Selecting an Editor
-------------------

The editor can be specified either by setting
[core.editor](http://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration#Basic-Client-Configuration)
in your Git config:

    git config --global core.editor "gvim -f"

or by setting the `EDITOR`, `VISUAL`, or `GIT_EDITOR` environment variable in
your shell:

    export EDITOR="gvim -f"

See the VARIABLES section in the [manual pages for
`git-var`](http://git-scm.com/docs/git-var) for the used order of preference.

Using an Alias
--------------

Of course, instead of typing `git edit-index`, you can setup a [git
alias](https://git-scm.com/book/tr/v2/Git-Basics-Git-Aliases):

    git config --global alias.ei edit-index

Then, all you have to do is to type <code>git ei</code>.

Configuration Options
---------------------

The command supports the following configuration options via [Git's
configuration
system](https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration).

### git-edit-index.onEmptyBuffer [ask|act|nothing]

What should be done when the editor buffer is empty (i.e. all lines were
deleted). Possible values:
* `ask`: Ask the user by showing him or her a `y/N` prompt. This is the default
  behavior of the command since version `0.5`.
* `act`: Reflect the changes, without asking. This was the default behavior of
  the command until version `0.5`.
* `nothing`: Do not reflect any changes, without asking. This corresponds to
  the default behavior of many other Git commands.

Default: **ask**.

Limitations
-----------

* Only the following statuses are currently supported:

  * `A`: Added file (staged).
  * `D`: Deleted file (not staged).
  * `M`: Modified file (not staged).
  * `?`: Untracked file.
  * `!`: Ignored file.

* Working with files having merge conflicts (status `U`,
  [#5](https://github.com/s3rvac/git-edit-index/issues/5)), renamed files
  (status `R`, [#6](https://github.com/s3rvac/git-edit-index/issues/6)), copied
  files (status `C`, [#7](https://github.com/s3rvac/git-edit-index/issues/7)),
  and partially staged files (status `MM`,
  [#8](https://github.com/s3rvac/git-edit-index/issues/8)) is currently not
  supported.

License
-------

Copyright (c) 2015 Petr Zemek (s3rvac@gmail.com) and contributors.

Distributed under the MIT license. See the
[`LICENSE`](https://github.com/s3rvac/git-edit-index/blob/master/LICENSE) file
for more details.
