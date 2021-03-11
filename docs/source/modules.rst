Modules
=======

While different modules perform different tasks, their interfaces all follow
the same pattern as much as possible.

The API of each module is composed of two parts. Information iside the
*provider* parameter influences how moddules connect to the Unit service. All
other parameters hold the information related to the resource that we are
operating on.


Provider parameters
-------------------

Each module has a *provider* parameter that holds the following information
about the Unit process we would like to manage:

1. The **endpoint** key holds the address of the Unit's control socket. If
   this key is not present in the task's definition, modules will consult the
   *UNIT_ENDPOINT* environment variable and, if the variable is not set, try
   to use the common unix socket paths. We can leave this variable unset in
   most cases.
2. **username** and **password** keys contain the credentials that modules
   will use when connecting to the Unit via the IP-based socket. It not
   present, Ansible will try to look up the *UNIT_USERNAME* and
   *UNIT_PASSWORD* environment variables. Again, we can leave these two
   variables unset in vast majority of use cases.

.. code-block:: yaml

   - name: 
     steampunk.unit.listener:
       provider:
         endpoint: https://unit.control.endpoint
         username: user
         password: pass
       # Other listener parameters here


Managing NGINX Unit configuration
---------------------------------

There are two things modules from the NGINX Unit Ansible Collection can do:

1. Enforce certain state of the configuration (either making sure configuration
   options are present or absent).
2. List all currently available resources on the backend.

Reference material for each module contains documentation on what parameters
certain modules accept and what values they expect those parameters to be.


Module reference
----------------

.. toctree::
   :glob:
   :maxdepth: 1

   modules/*
