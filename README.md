# NGINX Unit Ansible Collection

This repo contains the `steampunk.unit` Ansible Collection. The collection
includes modules and roles for setting up and managing NGINX Unit server.


## Using this collection

Before using the `steampunk.unit` Ansible Collection, you need to install the
collection with the `ansible-galaxy` CLI:

    $ ansible-galaxy collection install steampunk.unit

You can also include it in a `requirements.yml` file and install it via
`ansible-galaxy collection install -r requirements.yml` using the format:

    ---
    collections:
      - name: steampunk.unit

See [Ansible Using collections][usage] for more details.

   [usage]:
      https://docs.ansible.com/ansible/latest/user_guide/collections_using.html
      (Guides on using Ansible collections)


## Licensing

GNU General Public License v3.0 or later. See the LICENSE file to see the full
text.
