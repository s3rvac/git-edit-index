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
#    Copyright (c) 2015 Petr Zemek <s3rvac@gmail.com> and contributors.
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
from git_edit_index import ask_user_whether_reflect_changes_on_empty_buffer
from git_edit_index import current_index
from git_edit_index import edit_index
from git_edit_index import editor_cmd
from git_edit_index import git_status
from git_edit_index import main
from git_edit_index import perform_git_action
from git_edit_index import reflect_index_change
from git_edit_index import reflect_index_changes
from git_edit_index import remove
from git_edit_index import repository_path
from git_edit_index import should_reflect_changes_on_empty_buffer
from git_edit_index import value_for_config_option


# Do not inherit from unittest.TestCase because WithPatching is a mixin, not a
# base class for tests.
class WithPatching:
    """Mixin for tests that perform patching during their setup."""

    def patch(self, what, with_what, create=False):
        """Patches what with with_what."""
        patcher = mock.patch(what, with_what, create=create)
        patcher.start()
        self.addCleanup(patcher.stop)


class IndexTests(unittest.TestCase):
    """Tests for Index."""

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
            '! file3.txt\n'
        )

        self.assertEqual(len(index), 3)
        self.assertEqual(index.entry_for('file1.txt').status, 'M')
        self.assertEqual(index.entry_for('file2.txt').status, '?')
        self.assertEqual(index.entry_for('file3.txt').status, '!')

    def test_repr_returns_correct_representation(self):
        index = Index([IndexEntry('M', 'file1.txt')])

        self.assertEqual(repr(index), "Index([IndexEntry('M', 'file1.txt')])")

    def test_str_returns_correct_representation_when_there_are_no_entries(self):
        index = Index()

        self.assertEqual(str(index), '')

    def test_str_returns_correct_representation_when_there_are_entries(self):
        index = Index([
            IndexEntry('M', 'file1.txt'),
            IndexEntry('?', 'file2.txt'),
            IndexEntry('!', 'file3.txt')
        ])

        # The last entry has to end with a newline. Otherwise, some editors may
        # have problems displaying it.
        self.assertEqual(str(index), 'M file1.txt\n? file2.txt\n! file3.txt\n')


class IndexEntryTests(unittest.TestCase):
    """Tests for IndexEntry."""

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

    def test_from_line_returns_correct_entry_for_ignored_file_git_format(self):
        entry = IndexEntry.from_line('!! file.txt')

        self.assertEqual(entry.status, '!')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_ignored_file_our_format(self):
        entry = IndexEntry.from_line('! file.txt')

        self.assertEqual(entry.status, '!')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_returns_correct_entry_for_custom_patch_status(self):
        entry = IndexEntry.from_line('P file.txt')

        self.assertEqual(entry.status, 'P')
        self.assertEqual(entry.file, 'file.txt')

    def test_from_line_ignores_case_of_status(self):
        entry = IndexEntry.from_line('a file.txt')

        self.assertEqual(entry.status, 'A')
        self.assertEqual(entry.file, 'file.txt')

    def test_repr_returns_correct_representation(self):
        entry = IndexEntry('M', 'file.txt')

        self.assertEqual(repr(entry), "IndexEntry('M', 'file.txt')")

    def test_str_returns_correct_representation(self):
        entry = IndexEntry('M', 'file.txt')

        self.assertEqual(str(entry), 'M file.txt')


class NoIndexEntryTests(unittest.TestCase):
    """Tests for NoIndexEntry."""

    def test_status_is_always_none(self):
        entry = NoIndexEntry('file.txt')

        self.assertIsNone(entry.status)

    def test_file_returns_correct_value(self):
        entry = NoIndexEntry('file.txt')

        self.assertEqual(entry.file, 'file.txt')

    def test_repr_returns_correct_representation(self):
        entry = NoIndexEntry('file.txt')

        self.assertEqual(repr(entry), "NoIndexEntry('file.txt')")

    def test_str_returns_correct_representation(self):
        entry = NoIndexEntry('file.txt')

        self.assertEqual(str(entry), '- file.txt')


class CurrentIndexTests(unittest.TestCase, WithPatching):
    """Tests for current_index()."""

    def setUp(self):
        super(CurrentIndexTests, self).setUp()

        self.git_status = mock.Mock()
        self.patch('git_edit_index.git_status', self.git_status)

    def test_creates_index_from_git_status(self):
        self.git_status.return_value = 'M file1\0M file2\0'

        index = current_index()

        self.assertEqual(len(index), 2)
        self.assertEqual(index[0].file, 'file1')
        self.assertEqual(index[1].file, 'file2')


class GitStatusTests(unittest.TestCase, WithPatching):
    """Tests for git_status()."""

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

    def test_calls_correct_git_command_with_ignored_files(self):
        STATUS = 'status'
        self.subprocess.check_output.return_value = STATUS

        status = git_status(show_ignored='traditional')

        self.assertEqual(status, STATUS)
        self.subprocess.check_output.assert_called_once_with(
            ['git', 'status', '--porcelain', '-z', '--ignored=traditional'],
            universal_newlines=True
        )


class EditIndexTests(unittest.TestCase, WithPatching):
    """Tests for edit_index()."""

    def setUp(self):
        super(EditIndexTests, self).setUp()

        self.os = mock.MagicMock()
        self.patch('git_edit_index.os', self.os)

        self.subprocess = mock.Mock()
        self.patch('git_edit_index.subprocess', self.subprocess)

        self.tempfile = mock.MagicMock()
        self.patch('git_edit_index.tempfile', self.tempfile)

        self.open = mock.MagicMock()
        self.patch('git_edit_index.open', self.open)

        self.editor_cmd = mock.Mock()
        self.patch('git_edit_index.editor_cmd', self.editor_cmd)

    def test_stores_index_to_file_and_shows_it_to_user_and_returns_new_index(self):
        index = Index([IndexEntry('M', 'file.txt')])
        self.editor_cmd.return_value = ['vim']
        tmp_fd = 123
        tmp_path = 'git-edit-index-temp'
        self.tempfile.mkstemp.return_value = tmp_fd, tmp_path
        tmp_f1 = self.os.fdopen.return_value.__enter__.return_value
        tmp_f2 = self.open.return_value.__enter__.return_value
        tmp_f2.read.return_value = 'A file.txt\n'

        new_index = edit_index(index)

        self.assertEqual(len(new_index), 1)
        self.assertEqual(new_index[0].status, 'A')
        self.assertEqual(new_index[0].file, 'file.txt')
        tmp_f1.write.assert_called_once_with('M file.txt\n')
        self.subprocess.call.assert_called_once_with(
            self.editor_cmd() + [tmp_path]
        )
        tmp_f2.read.assert_called_once_with()
        self.os.remove.assert_called_once_with(tmp_path)


class EditorCmdTests(unittest.TestCase, WithPatching):
    """Tests for editor_cmd()."""

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
    """Tests for reflect_index_changes()."""

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
    """Tests for reflect_index_change()."""

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

        self.perform_git_action.assert_called_once_with(['add', '-f'], 'file.txt')

    def test_performs_correct_action_when_untracked_file_is_to_be_deleted(self):
        orig_entry = IndexEntry('?', 'file.txt')
        new_entry = NoIndexEntry('file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.remove.assert_called_once_with('file.txt')
        self.assertFalse(self.perform_git_action.called)

    def test_performs_correct_action_when_ignored_file_is_to_be_added(self):
        orig_entry = IndexEntry('!', 'file.txt')
        new_entry = IndexEntry('A', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with(['add', '-f'], 'file.txt')

    def test_performs_correct_action_when_ignored_file_is_to_be_deleted(self):
        orig_entry = IndexEntry('!', 'file.txt')
        new_entry = NoIndexEntry('file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.remove.assert_called_once_with('file.txt')
        self.assertFalse(self.perform_git_action.called)

    def test_performs_correct_action_when_modified_file_is_to_be_added(self):
        orig_entry = IndexEntry('M', 'file.txt')
        new_entry = IndexEntry('A', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with(['add', '-f'], 'file.txt')

    def test_performs_correct_action_when_modified_file_is_to_be_partially_added(self):
        orig_entry = IndexEntry('M', 'file.txt')
        new_entry = IndexEntry('P', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with(
            ['add', '--patch'],
            'file.txt',
            ignore_stdout=False
        )

    def test_performs_correct_action_when_deleted_file_is_to_be_added(self):
        orig_entry = IndexEntry('D', 'file.txt')
        new_entry = IndexEntry('A', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with(['add', '-f'], 'file.txt')

    def test_performs_correct_action_when_deleted_file_is_to_be_partially_added(self):
        orig_entry = IndexEntry('D', 'file.txt')
        new_entry = IndexEntry('P', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with(
            ['add', '--patch'],
            'file.txt',
            ignore_stdout=False
        )

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

    def test_performs_correct_action_when_modified_staged_file_is_to_be_partially_reset(self):
        orig_entry = IndexEntry('A', 'file.txt')
        new_entry = IndexEntry('P', 'file.txt')

        reflect_index_change(orig_entry, new_entry)

        self.perform_git_action.assert_called_once_with(
            ['reset', '--patch'],
            'file.txt',
            ignore_stdout=False
        )

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
            mock.call('checkout', 'file.txt', ignore_stderr=True)
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
    """Tests for remove()."""

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
    """Tests for perform_git_action()."""

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

    def test_does_not_ignore_stdout_when_requested(self):
        self.repository_path.return_value = '/'

        perform_git_action(['add', '--patch'], 'file.txt', ignore_stdout=False)

        self.subprocess.call.assert_called_once_with(
            ['git', 'add', '--patch', '--', os.path.join('/', 'file.txt')],
            stdout=None,
            stderr=None
        )

    def test_ignores_stderr_when_requested(self):
        self.repository_path.return_value = '/'

        perform_git_action('checkout', 'file.txt', ignore_stderr=True)

        self.subprocess.call.assert_called_once_with(
            ['git', 'checkout', '--', os.path.join('/', 'file.txt')],
            stdout=self.subprocess.PIPE,
            stderr=self.subprocess.PIPE
        )


class RepositoryPathTests(unittest.TestCase, WithPatching):
    """Tests for repository_path()."""

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


class ShouldReflectChangesOnEmptyBufferTests(unittest.TestCase, WithPatching):
    """Tests for `should_reflect_changes_on_empty_buffer()`."""

    def setUp(self):
        super(ShouldReflectChangesOnEmptyBufferTests, self).setUp()

        self.stderr = StringIO()
        self.patch('sys.stderr', self.stderr)

        self.value_for_config_option = mock.Mock()
        self.patch(
            'git_edit_index.value_for_config_option',
            self.value_for_config_option
        )

        self.ask_user_whether_reflect_changes_on_empty_buffer = mock.Mock()
        self.patch(
            'git_edit_index.ask_user_whether_reflect_changes_on_empty_buffer',
            self.ask_user_whether_reflect_changes_on_empty_buffer
        )

    def test_returns_true_when_config_option_is_set_to_act(self):
        self.value_for_config_option.return_value = 'act'

        self.assertTrue(should_reflect_changes_on_empty_buffer())

    def test_returns_false_when_config_option_is_set_to_nothing(self):
        self.value_for_config_option.return_value = 'nothing'

        self.assertFalse(should_reflect_changes_on_empty_buffer())

    def test_asks_user_when_config_option_is_set_to_ask(self):
        self.ask_user_whether_reflect_changes_on_empty_buffer.return_value = True
        self.value_for_config_option.return_value = 'ask'

        self.assertTrue(should_reflect_changes_on_empty_buffer())
        self.assertTrue(self.ask_user_whether_reflect_changes_on_empty_buffer.called)

    def test_returns_asks_user_when_config_option_is_not_set(self):
        self.ask_user_whether_reflect_changes_on_empty_buffer.return_value = True
        self.value_for_config_option.return_value = None

        self.assertTrue(should_reflect_changes_on_empty_buffer())
        self.assertTrue(self.ask_user_whether_reflect_changes_on_empty_buffer.called)

    def test_prints_error_and_exits_when_config_option_is_set_to_unsupported_value(self):
        self.value_for_config_option.return_value = 'xxx'

        with self.assertRaises(SystemExit) as cm:
            should_reflect_changes_on_empty_buffer()
        self.assertIn('xxx', self.stderr.getvalue())
        self.assertEqual(cm.exception.code, 1)


class AskUserWhetherReflectChangesOnEmptyBufferTests(unittest.TestCase, WithPatching):
    """Tests for `ask_user_whether_reflect_changes_on_empty_buffer()`."""

    def setUp(self):
        super(AskUserWhetherReflectChangesOnEmptyBufferTests, self).setUp()

        self.input = mock.Mock()
        self.patch('git_edit_index.input', self.input)

    def test_asks_user_and_returns_true_when_user_answered_lowercase_y(self):
        self.input.return_value = 'y'

        self.assertTrue(ask_user_whether_reflect_changes_on_empty_buffer())

    def test_asks_user_and_returns_true_when_user_answered_uppercase_y(self):
        self.input.return_value = 'Y'

        self.assertTrue(ask_user_whether_reflect_changes_on_empty_buffer())

    def test_asks_user_and_returns_false_when_user_answered_n(self):
        self.input.return_value = 'n'

        self.assertFalse(ask_user_whether_reflect_changes_on_empty_buffer())

    def test_asks_user_and_returns_false_when_user_answered_enter(self):
        self.input.return_value = ''

        self.assertFalse(ask_user_whether_reflect_changes_on_empty_buffer())


class ValueForConfigOptionTests(unittest.TestCase, WithPatching):
    """Tests for `value_for_config_option()`."""

    def setUp(self):
        super(ValueForConfigOptionTests, self).setUp()

        self.subprocess = mock.Mock()
        self.patch('git_edit_index.subprocess', self.subprocess)

    def test_runs_correct_command_and_returns_its_output(self):
        self.subprocess.check_output.return_value = 'value\n'

        value = value_for_config_option('section.option')

        self.assertEqual(value, 'value')
        self.subprocess.check_output.assert_called_once_with(
            ['git', 'config', 'section.option'],
            universal_newlines=True
        )

    def test_returns_none_when_there_is_no_value_for_option(self):
        self.subprocess.CalledProcessError = RuntimeError
        self.subprocess.check_output.side_effect = self.subprocess.CalledProcessError

        value = value_for_config_option('section.option')

        self.assertIsNone(value)


class MainTests(unittest.TestCase, WithPatching):
    """Tests for main() and parse_args()."""

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

        self.should_reflect_changes_on_empty_buffer = mock.Mock()
        self.patch(
            'git_edit_index.should_reflect_changes_on_empty_buffer',
            self.should_reflect_changes_on_empty_buffer
        )

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

    def test_reflects_changes_when_changes_should_be_reflected_on_empty_buffer(self):
        self.current_index.return_value = Index([IndexEntry('M', 'file.txt')])
        self.edit_index.return_value = Index()
        self.should_reflect_changes_on_empty_buffer.return_value = True

        main(['git-edit-index'])

        self.assertTrue(self.should_reflect_changes_on_empty_buffer.called)
        self.assertTrue(self.reflect_index_changes.called)

    def test_does_not_reflect_changes_when_changes_should_not_be_reflected_on_empty_buffer(self):
        self.current_index.return_value = Index([IndexEntry('M', 'file.txt')])
        self.edit_index.return_value = Index()
        self.should_reflect_changes_on_empty_buffer.return_value = False

        main(['git-edit-index'])

        self.assertTrue(self.should_reflect_changes_on_empty_buffer.called)
        self.assertFalse(self.reflect_index_changes.called)

    def test_does_not_show_editor_to_user_when_index_is_empty(self):
        self.current_index.return_value = Index()

        main(['git-edit-index'])

        self.assertFalse(self.edit_index.called)


if __name__ == '__main__':
    unittest.main()
