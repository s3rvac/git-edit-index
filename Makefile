#
# Project:   git-edit-index
# Copyright: (c) 2015 by Petr Zemek <s3rvac@petrzemek.net> and contributors
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
	@flake8 --ignore=E501 git-edit-index tests/test_git_edit_index.py setup.py

tests:
	@pytest tests

tests-coverage:
	@pytest tests \
		--cov=git_edit_index \
		--cov-report=term \
		--cov-report=html:coverage/html
