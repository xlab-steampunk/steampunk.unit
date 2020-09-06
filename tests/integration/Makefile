modules   := $(wildcard molecule/module_*)
roles     := $(wildcard molecule/role_*)
scenarios := $(modules) $(roles)

# Make sure ansible can find our collection without having to install it.
export ANSIBLE_COLLECTIONS_PATHS ?= $(realpath $(CURDIR)/../../../../..)


.PHONY: all
all: $(scenarios)

.PHONY: modules
modules: $(modules)

.PHONY: roles
roles: $(roles)

.PHONY: $(scenarios)
$(scenarios):
	molecule -c base.yml test -s $(notdir $@)
