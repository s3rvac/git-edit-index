Changelog
=========

dev
---

0.7 (2022-07-11)
----------------

* FEA: Added support for deleting symlinks
  ([087acf7](https://github.com/s3rvac/git-edit-index/commit/087acf75fc169a8c54e71befb124546261d6a723)).
* DEL: Dropped official support for Python 3.5 and 3.6 as [they are
  EOL](https://devguide.python.org/#branchstatus).

0.6 (2019-07-21)
----------------

* FEA: Added support for staging ignored files
  ([#9](https://github.com/s3rvac/git-edit-index/pull/9)). To show ignored
  files, you need to run `git edit-index` with the `--ignored` parameter.
* DEL: Dropped official support for Python 3.2, 3.3, and 3.4 as [they are
  EOL](https://devguide.python.org/#branchstatus).

0.5.2 (2018-04-08)
------------------

* FIX: Fixed `TypeError: fdopen() takes no keyword arguments` when running the
  command via Python 2.7
  ([#3](https://github.com/s3rvac/git-edit-index/issues/3)).

0.5.1 (2018-04-01)
------------------

* FIX: Fixed the opening of the editor on Windows. Due to file locking on
  Windows, we need to write the index and close the temporary file before we
  open the editor. Otherwise, the editor is not able to read or change the
  file.

0.5 (2016-10-23)
----------------

* FEA: When the editor buffer is empty (i.e. all lines were deleted), the
  command now asks the user whether he or she wants to reflect the changes
  ([#1](https://github.com/s3rvac/git-edit-index/issues/1)). This makes the
  deletion of files or changes more foolproof. The default behavior can be
  changed by setting the `onEmptyBuffer` config option (see the `README` file
  for more details).
* FIX: Do not print a backtrace when an external command (e.g. `git`) fails.
  That only clutters the screen, thus making the real error printed by the
  external command less apparent.

0.4 (2016-06-26)
----------------

* FEA: Changing file status from `M` or `D` to `P` runs `git add --patch FILE`.
* FEA: Changing file status from `D` to `P` runs `git reset --patch FILE`.
* FEA: Added the script to PyPI so it can be installed via `pip install
  git-edit-index`.
* FIX: Fixed unit tests under Python 2 and PyPy.

0.3.2 (2015-10-09)
------------------

* FIX: Fixed displaying of the index in editors that have problems when the
  overall text does not end with a newline.

0.3.1 (2015-09-03)
------------------

* FIX: Fixed removal of files or directories when not being inside the
  repository's root path. Previously, this failed with an exception.
* FIX: When an untracked directory is to be removed, use `shutil.rmtree()`
  instead of `os.remove()` because `os.remove()` does not work on directories.

0.3 (2015-08-07)
----------------

* FEA: Allow staging, unstaging, and reverting changes of deleted files.
* FEA: Allow removing an untracked file by removing the corresponding line in
  the editor.
* FEA: Allow setting the editor also by setting the `GIT_EDITOR` or `VISUAL`
  environment variables.
* FEA: When the index is empty, do not show an empty editor.

0.2 (2015-05-25)
----------------

* FEA: Allow reverting changes done to a file since the last commit by removing
  the line with the file from the editor.
* FIX: Use `--` before files when running Git commands to prevent confusion
  when a file looks like a branch or tag.
* FIX: Added a missing description of the `?` status into README.
* FIX: Fall back to `$EDITOR` if Git's `core.editor` is not set.

0.1 (2015-05-23)
----------------

Initial release.
