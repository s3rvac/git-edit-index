#
# A setuptools-based setup module for the project.
#

import ast
import re
from setuptools import setup


# Utility function to read the contents of the given file.
def read_file(file_path):
    with open(file_path) as f:
        return f.read()


# Utility function to return the project version from the git-edit-index file.
def get_project_version():
    return ast.literal_eval(
        re.search(
            r'__version__\s+=\s+(.*)',
            read_file('git-edit-index')
        ).group(1)
    )


setup(
    name='git-edit-index',
    version=get_project_version(),
    description=(
        'A git command that opens an editor to stage or unstage files.'
    ),
    long_description="""
This command represents a faster alternative to ``git add -i`` or ``git gui``.
It allows you to stage or unstage files from the index in an editor, just like
when you perform an interactive rebase.

For example, lets assume you have the following three modified files (``git
status --short``):

.. code-block:: text

    M path/to/file1
    M another/path/to/file2
    M yet/another/path/to/file3

After running ``git edit-index``, an editor will show up with the above output.
To stage (add) the first two files, simply change the text to

.. code-block:: text

    A path/to/file1
    A another/path/to/file2
    M yet/another/path/to/file3

The supported statuses are ``M``, ``A``, ``D``, and ``?``. They allow you to
not only stage files but also unstage them, delete them, or revert changes done
to them since the last commit.

See the `project's homepage <https://github.com/s3rvac/git-edit-index>`_ for
more information.
    """.strip(),
    author='Petr Zemek',
    author_email='s3rvac@gmail.com',
    url='https://github.com/s3rvac/git-edit-index',
    license=read_file('LICENSE'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Version Control',
    ],
    keywords='git editor index staging unstaging',
    scripts=[
        'git-edit-index'
    ]
)
