#!/usr/bin/env python
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

import io
import unittest
from unittest import mock

from git_edit_index import parse_args


# Do not inherit from unittest.TestCase because WithPatching is a mixin, not a
# base class for tests.
class WithPatching:
    """Mixin for tests that perform patching during their setup."""

    def patch(self, what, with_what):
        """Patches `what` with `with_what`."""
        patcher = mock.patch(what, with_what)
        patcher.start()
        self.addCleanup(patcher.stop)


class ParseArgsTests(unittest.TestCase, WithPatching):
    """Tests for `parse_args()`."""

    def setUp(self):
        super().setUp()

        self.stdout = io.StringIO()
        self.patch('sys.stdout', self.stdout)

        self.stderr = io.StringIO()
        self.patch('sys.stderr', self.stderr)

    def test_prints_help_and_exits_when_requested(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['git-edit-index', '--help'])
        self.assertEqual(cm.exception.code, 0)

    def test_prints_error_message_and_exits_when_invalid_parameter_is_given(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['git-edit-index', '--xyz'])
        self.assertNotEqual(cm.exception.code, 0)
