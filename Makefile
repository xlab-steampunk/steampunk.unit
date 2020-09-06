# Make sure we have ansible_collections/sensu/sensu_go as a prefix.
collection := $(notdir $(realpath $(CURDIR)      ))
namespace  := $(notdir $(realpath $(CURDIR)/..   ))
toplevel   := $(notdir $(realpath $(CURDIR)/../..))

err_msg := Place collection at <WHATEVER>/ansible_collections/steampunk/unit
ifneq (unit,$(collection))
  $(error $(err_msg))
else ifneq (steampunk,$(namespace))
  $(error $(err_msg))
else ifneq (ansible_collections,$(toplevel))
  $(error $(err_msg))
endif

# Make sure ansible can find our collection without having to install it.
export ANSIBLE_COLLECTIONS_PATHS ?= $(realpath $(CURDIR)/../../..)

# Because we are dynamically installing requirements and do not want to mess up
# the system, we require virtual environemnt to be active.
venv_msg := Run from the venv virtual environment

python_version := $(shell \
  python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' \
)


.PHONY: requirements
requirements:
	pip install -r 

.PHONY: update_argspecs
update_argspecs:
	ansible-argspec-gen --diff plugins/modules/*.py; true

.PHONY: sanity
sanity:
	ansible-argspec-gen --diff --dry-run plugins/modules/*.py
	flake8 --extend-exclude venv,tests/output
	ansible-lint -p roles/*
	ansible-test sanity \
	  --requirements \
	  --python $(python_version) \
	  --exclude tests/integration/molecule/

.PHONY: units
units:
	ansible-test units \
	  --requirements \
	  --python $(python_version)
