#
# Tests for git-edit-index.
#
# Home page:
#
#    https://github.com/s3rvac/git-edit-index
#
# License:
#
#    The MIT License (MIT)
#
#    Copyright (c) 2015-2016 Petr Zemek <s3rvac@gmail.com> and contributors.
#
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation
#    the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#

import os
import unittest

try:
    from cStringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO  # Python 3

try:
    from unittest import mock  # Python 3
except ImportError:
    import mock  # Python 2

from git_edit_index import Index
from git_edit_index import IndexEntry
from git_edit_index import NoIndexEntry
from git_edit_index import __version__
from git_edit_index import editor_cmd
from git_edit_index import git_status
from git_edit_index import main
from git_edit_index import perform_git_action
from git_edit_index import reflect_index_change
from git_edit_index import reflect_index_changes
from git_edit_index import remove
from git_edit_index import repository_path


# Do not inherit from unittest.TestCase because WithPatching is a mixin, not a
# base class for tests.
class WithPatching:
    """Mixin for tests that perform patching during their setup."""

    def patch(self, what, with_what):
        """Patches `what` with `with_what`."""
        patcher = mock.patch(what, with_what)
        patcher.start()
        self.addCleanup(patcher.stop)


class IndexTests(unittest.TestCase):
    """Tests for `Index`."""

    def test_entry_for_returns_no_index_entry_when_there_is_no_entry(self):
        index = Index()

        self.assertIsInstance(index.entry_for('file.txt'), NoIndexEntry)

    def test_entry_for_returns_correct_entry_when_it_exists(self):
        entry = IndexEntry('M', 'file1.txt')
        index = Index([entry])

        self.assertEqual(index.entry_for('file1.txt'), entry)

    def test_from_text_returns_empty_index_when_there_are_no_lines(self):
        index = Index.from_text('')

        self.assertEqual(len(index), 0)

    def test_from_text_returns_correct_index_when_there_are_lines(self):
        index = Index.from_text(
            'M file1.txt\n'
            '? file2.txt\n'
        )

        self.assertEqual(len(index), 2)
        self.assertEqual(index.entry_for('file1.txt').status, 'M')
        self.assertEqual(index.entry_for('file2.txt').status, '?')

    def test_str_returns_correct_representation_when_there_are_no_entries(self):
        index = Index()

        self.assertEqual(str(index), '')

    def test_str_returns_correct_representation_when_there_are_entries(self):
        index = Index([
            IndexEntry('M', 'file1.txt'),
            IndexEntry('?', 'file2.txt')
        ])

        # The last entry has to end with a newline (otherwise, some editors may
        # have problems displaying it.
        self.assertEqual(str(index), 'M file1.txt\n? file2.txt\n')


class IndexEntryTests(unittest.TestCase):
    """Tests for `IndexEntry`."""

    def test_status_and_file_are_accessible_after_creation(self):
        entry = IndexEntry('M', 'file.txt')

        self.assertEqual(entry.status, 'M')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_none_for_empty_line(self):
        self.assertIsNone(IndexEntry.from_line(''))

    def test_from_line_returns_none_for_unknown_status(self):
        self.assertIsNone(IndexEntry.from_line('# file.txt'))

    def test_from_line_returns_correct_entry_for_added_file_git_format(self):
        entry = IndexEntry.from_line('M  file.txt')

        self.assertEqual(entry.status, 'A')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_added_file_our_format(self):
        entry = IndexEntry.from_line('M file.txt')

        self.assertEqual(entry.status, 'M')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_modified_file_git_format(self):
        entry = IndexEntry.from_line(' M file.txt')

        self.assertEqual(entry.status, 'M')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_modified_file_our_format(self):
        entry = IndexEntry.from_line('M file.txt')

        self.assertEqual(entry.status, 'M')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_deleted_file_git_format(self):
        entry = IndexEntry.from_line(' D file.txt')

        self.assertEqual(entry.status, 'D')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_deleted_file_our_format(self):
        entry = IndexEntry.from_line('D file.txt')

        self.assertEqual(entry.status, 'D')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_untracked_file_git_format(self):
        entry = IndexEntry.from_line('?? file.txt')

        self.assertEqual(entry.status, '?')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_untracked_file_our_format(self):
        entry = IndexEntry.from_line('? file.txt')

        self.assertEqual(entry.status, '?')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_ignores_case_of_status(self):
        entry = IndexEntry.from_line('a file.txt')

        self.assertEqual(entry.status, 'A')
        self.assertEqual(entry.file, 'file.txt')

    def test_str_returns_correct_representation(self):
        entry = IndexEntry('M', 'file.txt')

        self.assertEqual(str(entry), 'M file.txt')


class NoIndexEntryTests(unittest.TestCase):
    """Tests for `NoIndexEntry`."""

    def test_status_is_always_none(self):
        entry = NoIndexEntry('file.txt')

        self.assertIsNone(entry.status)

    def test_file_returns_correct_value(self):
        entry = NoIndexEntry('file.txt')

        self.assertEqual(entry.file, 'file.txt')

    def test_str_returns_correct_representation(self):
        entry = NoIndexEntry('file.txt')

        self.assertEqual(str(entry), '- file.txt')


class GitStatusTests(unittest.TestCase, WithPatching):
    """Tests for `git_status()`."""

    def setUp(self):
        super(GitStatusTests, self).setUp()

        self.subprocess = mock.Mock()
        self.patch('git_edit_index.subprocess', self.subprocess)

    def test_calls_correct_git_command_and_returns_correct_status(self):
        STATUS = 'status'
        self.subprocess.check_output.return_value = STATUS

        status = git_status()

        self.assertEqual(status, STATUS)
        self.subprocess.check_output.assert_called_once_with(
            ['git', 'status', '--porcelain', '-z'],
            universal_newlines=True
        )


class EditorCmdTests(unittest.TestCase, WithPatching):
    """Tests for `editor_cmd()`."""

    def setUp(self):
        super(EditorCmdTests, self).setUp()

        self.subprocess = mock.Mock()
        self.patch('git_edit_index.subprocess', self.subprocess)

    def test_calls_correct_git_command_and_returns_correct_cmd(self):
        CMD = ['gvim', '-f']
        self.subprocess.check_output.return_value = '{}\n'.format(
            ' '.join(CMD)
        )

        cmd = editor_cmd()

        self.subprocess.check_output.assert_called_once_with(
            ['git', 'var', 'GIT_EDITOR'],
            universal_newlines=True
        )
        self.assertEqual(cmd, CMD)


class ReflectIndexChangesTests(unittest.TestCase, WithPatching):
    """Tests for `reflect_index_changes()`."""

    def setUp(self):
        super(ReflectIndexChangesTests, self).setUp()

        self.reflect_index_change = mock.Mock()
        self.patch('git_edit_index.reflect_index_change', self.reflect_index_change)

    def test_calls_reflect_index_change_for_correct_entries(self):
        entry1 = IndexEntry('M', 'file1.txt')
        entry2 = IndexEntry('M', 'file2.txt')
        entry3 = IndexEntry('?', 'file1.txt')
        orig_index = Index([entry1, entry2])
        new_index = Index([entry3, entry2])

        reflect_index_changes(orig_index, new_index)

        self.reflect_index_change.assert_called_once_with(entry1, entry3)


class ReflectIndexChangeTests(unittest.TestCase, WithPatching):
    """Tests for `reflect_index_change()`."""

    def setUp(self):
        super(ReflectIndexChangeTests, self).setUp()

        self.remove = mock.Mock()
        self.patch('git_edit_index.remove', self.remove)

        self.perform_git_action = mock.Mock()
        self.patch('git_edit_index.perform_git_action', self.perform_git_action)

    def test_performs_correct_action_when_untracked_file_is_to_be_added(self):
        orig_entry = IndexEntry('?', 'file.txt')
        new_entry = IndexEntry('A', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with('add', 'file.txt')

    def test_performs_correct_action_when_untracked_file_is_to_be_deleted(self):
        orig_entry = IndexEntry('?', 'file.txt')
        new_entry = NoIndexEntry('file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.remove.assert_called_once_with('file.txt')
        self.assertFalse(self.perform_git_action.called)

    def test_performs_correct_action_when_modified_file_is_to_be_added(self):
        orig_entry = IndexEntry('M', 'file.txt')
        new_entry = IndexEntry('A', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with('add', 'file.txt')

    def test_performs_correct_action_when_deleted_file_is_to_be_added(self):
        orig_entry = IndexEntry('D', 'file.txt')
        new_entry = IndexEntry('A', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with('add', 'file.txt')

    def test_performs_correct_action_when_modified_staged_file_is_to_be_unstaged(self):
        orig_entry = IndexEntry('A', 'file.txt')
        new_entry = IndexEntry('M', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with('reset', 'file.txt')

    def test_performs_correct_action_when_deleted_staged_file_is_to_be_unstaged(self):
        orig_entry = IndexEntry('A', 'file.txt')
        new_entry = IndexEntry('D', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with('reset', 'file.txt')

    def test_performs_correct_action_when_modified_file_is_to_be_reset(self):
        orig_entry = IndexEntry('M', 'file.txt')
        new_entry = NoIndexEntry('file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with('checkout', 'file.txt')

    def test_performs_correct_actions_when_staged_file_is_to_be_reset(self):
        orig_entry = IndexEntry('A', 'file.txt')
        new_entry = NoIndexEntry('file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_has_calls([
            mock.call('reset', 'file.txt'),
            mock.call('checkout', 'file.txt', ignore_errors=True)
        ])

    def test_performs_correct_action_when_deleted_file_is_to_be_reset(self):
        orig_entry = IndexEntry('D', 'file.txt')
        new_entry = NoIndexEntry('file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with('checkout', 'file.txt')

    def test_performs_correct_action_when_modified_file_is_to_be_untracked(self):
        orig_entry = IndexEntry('M', 'file.txt')
        new_entry = IndexEntry('?', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with(
            ['rm', '--cached'], 'file.txt'
        )


class RemoveTests(unittest.TestCase, WithPatching):
    """Tests for `remove()`."""

    def setUp(self):
        super(RemoveTests, self).setUp()

        self.repository_path = mock.Mock()
        self.patch('git_edit_index.repository_path', self.repository_path)

        self.os_path_isdir = mock.Mock()
        self.patch('git_edit_index.os.path.isdir', self.os_path_isdir)

        self.os_remove = mock.Mock()
        self.patch('git_edit_index.os.remove', self.os_remove)

        self.shutil_rmtree = mock.Mock()
        self.patch('git_edit_index.shutil.rmtree', self.shutil_rmtree)

    def test_correct_command_is_called_to_remove_file(self):
        self.repository_path.return_value = '/'
        self.os_path_isdir.return_value = False

        remove('file.txt')

        self.os_remove.assert_called_once_with(os.path.join('/', 'file.txt'))

    def test_correct_command_is_called_to_remove_directory(self):
        self.repository_path.return_value = '/'
        self.os_path_isdir.return_value = True

        remove('dir')

        self.shutil_rmtree.assert_called_once_with(os.path.join('/', 'dir'))


class PerformGitActionTests(unittest.TestCase, WithPatching):
    """Tests for `perform_git_action()`."""

    def setUp(self):
        super(PerformGitActionTests, self).setUp()

        self.subprocess = mock.Mock()
        self.patch('git_edit_index.subprocess', self.subprocess)

        self.repository_path = mock.Mock()
        self.patch('git_edit_index.repository_path', self.repository_path)

    def test_calls_git_with_proper_arguments_when_action_is_single_command(self):
        self.repository_path.return_value = '/'

        perform_git_action('add', 'file.txt')

        self.subprocess.call.assert_called_once_with(
            ['git', 'add', '--', os.path.join('/', 'file.txt')],
            stdout=self.subprocess.PIPE,
            stderr=None
        )

    def test_calls_git_with_proper_arguments_when_action_is_compound_command(self):
        self.repository_path.return_value = '/'

        perform_git_action(['rm', '--cached'], 'file.txt')

        self.subprocess.call.assert_called_once_with(
            ['git', 'rm', '--cached', '--', os.path.join('/', 'file.txt')],
            stdout=self.subprocess.PIPE,
            stderr=None
        )

    def test_ignores_errors_when_requested(self):
        self.repository_path.return_value = '/'

        perform_git_action('checkout', 'file.txt', ignore_errors=True)

        self.subprocess.call.assert_called_once_with(
            ['git', 'checkout', '--', os.path.join('/', 'file.txt')],
            stdout=self.subprocess.PIPE,
            stderr=self.subprocess.PIPE
        )


class RepositoryPathTests(unittest.TestCase, WithPatching):
    """Tests for `repository_path()`."""

    def setUp(self):
        super(RepositoryPathTests, self).setUp()

        self.subprocess = mock.Mock()
        self.patch('git_edit_index.subprocess', self.subprocess)

    def test_calls_correct_git_command_and_returns_correct_path(self):
        REPOSITORY_PATH = '/path/to/repo'
        self.subprocess.check_output.return_value = '{}\n'.format(
            REPOSITORY_PATH
        )

        path = repository_path()

        self.assertEqual(path, REPOSITORY_PATH)
        self.subprocess.check_output.assert_called_once_with(
            ['git', 'rev-parse', '--show-toplevel'],
            universal_newlines=True
        )


class MainTests(unittest.TestCase, WithPatching):
    """Tests for `main()` and `parse_args()`."""

    def setUp(self):
        super(MainTests, self).setUp()

        self.stdout = StringIO()
        self.patch('sys.stdout', self.stdout)

        self.stderr = StringIO()
        self.patch('sys.stderr', self.stderr)

        self.current_index = mock.Mock()
        self.patch('git_edit_index.current_index', self.current_index)

        self.edit_index = mock.Mock()
        self.patch('git_edit_index.edit_index', self.edit_index)

        self.reflect_index_changes = mock.Mock()
        self.patch('git_edit_index.reflect_index_changes', self.reflect_index_changes)

    def test_prints_help_to_stdout_and_exits_with_zero_when_requested(self):
        with self.assertRaises(SystemExit) as cm:
            main(['git-edit-index', '--help'])
        self.assertIn('help', self.stdout.getvalue())
        self.assertEqual(cm.exception.code, 0)

    def test_prints_version_to_stdout_and_exits_with_zero_when_requested(self):
        with self.assertRaises(SystemExit) as cm:
            main(['git-edit-index', '--version'])
        # Python < 3.4 emits the version to stderr, Python >= 3.4 to stdout.
        output = self.stdout.getvalue() + self.stderr.getvalue()
        self.assertIn(__version__, output)
        self.assertEqual(cm.exception.code, 0)

    def test_exits_with_non_zero_return_code_when_invalid_parameter_is_given(self):
        with self.assertRaises(SystemExit) as cm:
            main(['git-edit-index', '--xxx'])
        self.assertIn('--xxx', self.stderr.getvalue())
        self.assertNotEqual(cm.exception.code, 0)

    def test_shows_editor_to_user_and_reflects_changes_when_index_is_nonempty(self):
        orig_index = Index([IndexEntry('M', 'file.txt')])
        self.current_index.return_value = orig_index

        main(['git-edit-index'])

        self.edit_index.assert_called_once_with(orig_index)
        self.reflect_index_changes.assert_called_once_with(
            orig_index, self.edit_index.return_value
        )

    def test_does_not_show_editor_to_user_when_index_is_empty(self):
        self.current_index.return_value = Index()

        main(['git-edit-index'])

        self.assertFalse(self.edit_index.called)


if __name__ == '__main__':
    unittest.main()
