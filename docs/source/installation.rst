Installation
============

We can install Unit Ansible Collection using the ``ansible-galaxy`` tool
that comes bundled with Ansible. This tool can install Ansible collections
from different sources.


Installing from Ansible Galaxy
------------------------------

`Ansible Galaxy`_ is the default source of Ansible collections for the
``ansible-galaxy`` tool. We can install the Unit Ansible Collection by
running::

   $ ansible-galaxy collection install steampunk.unit

.. _Ansible Galaxy: https://galaxy.ansible.com

After the command finishes, we will have the latest version of the Unit
Ansible Collection installed and ready to be (ab)used ;)

We can also install a specific version of the collection by appending a
version after the name::

   $ ansible-galaxy collection install steampunk.unit:0.7.0

.. note::

   ``ansible-galaxy`` command will not overwrite the existing collection if it
   is already installed. We can change this default behavior by adding a
   ``--force`` command line switch::

      $ ansible-galaxy collection install --force steampunk.unit:0.7.0

The official Ansible documentation contains more information about the
installation options in the `Using collections`_ document.

.. _Using collections:
   https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#installing-collections


Installing from a local file
----------------------------

This last method of installation might come in handy in situations where our
Ansible control node cannot access Ansible Galaxy or Automation Hub.

First, we need to download the Sensu Go Ansible collection archive from the
GitHub `releases page`_ and then transfer that archive to the Ansible control
node. Once we have that archive on our control node, we can install the Sensu
Go collection by running::

   $ ansible-galaxy collection install path/to/steampunk-unit-0.7.0.tar.gz

.. _releases page:
   https://github.com/xlab-steampunk/steampunk.unit/releases
