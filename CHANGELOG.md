Changelog
=========

dev
---

* -

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
