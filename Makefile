#
# Project:   git-edit-index
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#
# A GNU Makefile for the project.
#

.PHONY: help clean lint tests tests-coverage

help:
	@echo "Use \`make <target>', where <target> is one of the following:"
	@echo "  clean          - remove all generated files"
	@echo "  lint           - check code style with flake8"
	@echo "  tests          - run tests"
	@echo "  tests-coverage - obtain test coverage"

clean:
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '*.py[co]' -exec rm -f {} +
	@rm -rf .coverage coverage

lint:
	@flake8 --ignore=E501 git-edit-index tests/git_edit_index_tests.py

tests:
	@nosetests tests

tests-coverage:
	@nosetests tests \
		--with-coverage \
		--cover-package git_edit_index \
		--cover-erase \
		--cover-html \
		--cover-html-dir coverage
