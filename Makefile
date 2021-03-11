# Make sure ansible can find our collection without having to install it.
export ANSIBLE_COLLECTIONS_PATHS ?= $(realpath $(CURDIR)/../../..)

.PHONY: docs
docs:
	pip install -r docs.requirements
	$(MAKE) -C docs -f Makefile.custom docs

.PHONY: clean
clean:
	$(MAKE) -C docs -f Makefile.custom clean
