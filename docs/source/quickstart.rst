Quickstart
==========

If we have Ansible 2.9 or newer installed, we can download and install the
NGINX Unit Ansible Collection with just one command::

   $ ansible-galaxy collection install steampunk.unit

With the collection in place, we are just one Ansible
:download:`playbook <../examples/quickstart/playbook.yaml>` away from
deploying a minimalistic python application:

.. literalinclude:: ../examples/quickstart/playbook.yaml
   :language: yaml

When we run it, Ansible will:

1. install and run the Unit server,
2. copy our
   :download:`python application <../examples/quickstart/wsgi.py>` to the
   remote host, and
3. instruct Unit to start passing the requests on port 3000 to our
   application.

Now, before we can run this playbook, we need to prepare an inventory file.
The inventory should contain an *unit_hosts* group becuse our playbook expects
to find target hosts there. A
:download:`minimal inventory <../examples/quickstart/inventory.yaml>` with
a singlehosts will look somewhat like this:

.. literalinclude:: ../examples/quickstart/inventory.yaml
   :language: yaml

Replace the IP addresses with your own and make sure you can ssh into the
host. If you need help with building your inventory file, consult `official
documentation on inventory`_.

.. _official documentation on inventory:
   https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html

All that we need to do now is to
run the playbook::

   $ ansible-playbook -i inventory.yaml playbook.yaml

And in a minute or so, things should be ready to go. And if we now visit
http://192.168.50.4:3000 (replace that IP address with the address of your
backend), we should be greeted by our application. If no firewall is in a way,
of cource ;)
