Changelog
=========

dev
---

* -

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
