git-edit-index
==============

This command represents a faster alternative to `git add -i` or `git gui`. It
allows you to stage or unstage files from the index in an editor, just like
when you perform an interactive rebase.

For example, lets assume you have the following three modified files (`git
status --short`):

    M path/to/file1
    M another/path/to/file2
    M yet/another/path/to/file3

After running `git edit-index`, an editor will show up with the above output.
To stage (add) the first two files, simply change the text to

    A path/to/file1
    A another/path/to/file2
    M yet/another/path/to/file3

Requirements
------------

The script requires Python 2.7 or 3.x. Both CPython and PyPy implementations
are supported.

Installation
------------

* Put the `git-edit-index` script to a directory that is in your `$PATH`.
* Ensure that the script is executable (`chmod a+x git-edit-index`).

Usage
-----

Run `git edit-index` to display an editor with the current index. In it, you
can stage or unstage files from the index simply by changing their status:

* To stage a modified file, change its status from `M` to `A`. This runs `git
  add FILE`.
* To unstage a modified file, change its status from `A` to `M`. This runs `git
  reset FILE`.
* To add an untracked file, change its status from `?` to `A`. This runs `git
  add FILE`.
* To stop tracking of a file, change its status to `?`. This runs `git rm
  --cached FILE`.
* To delete an untracked file, remove the line with the file. This deletes the
  file by using the operating system's file-deletion facilities.
* To revert changes done to a file since the last commit, remove the line with
  the file. This runs `git checkout FILE` (if the file is staged, it first runs
  `git reset FILE`).

The status is case-insensitive, e.g. both `A` and `a` stage the given file
(lower-case letters are easier to type).

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

Limitations
-----------

* Only the following statuses are currently supported:

  * `A`: Added file (staged).
  * `M`: Modified file (not staged).
  * `?`: Untracked file.

* Staging of files during merge conflicts is currently not supported.

License
-------

Copyright (c) 2015 Petr Zemek (s3rvac@gmail.com) and contributors.

Distributed under the MIT license. See the `LICENSE` file for more details.
