# Nextcloud Munin Plugin [![CodeFactor](https://www.codefactor.io/repository/github/mightybroccoli/nextcloud-munin-py/badge/master)](https://www.codefactor.io/repository/github/mightybroccoli/nextcloud-munin-py/overview/master)
This repository contains some basic Munin Plugins for gathering information from the NextCloud external API. To further simplify the monitory process I choose to also include a multigraph plugin `nextcloud_multi.py` which does everything the other plugins do in a single plugin.

There are requirements for using a multigraph plugin which can be read up here : [Munin-Monitoring.org/multigraphing](http://guide.munin-monitoring.org/en/latest/plugin/multigraphing.html)

## install
### requirements
The Python environment need to have access to the [requests](https://github.com/psf/requests) module. It is possible to run the plugins in a virtual environment, with the virtual environment tool of your choice.
The `requirements.txt` file contains all necessary libraries pip will install.
```
virtualenv -p python3 /path/to/your/venv
pip install -r requirements.txt
```

#### Tip
Unfortunately you need to invoke the plugin with the virtual environment runtime. Thus you have to change the shebang from '#!/usr/bin/env python3' to the python3 path, or you could simply add a wrapper script.
That way you only modify untracked files which helps with git updates.
```bash
#!/bin/bash
# path to my virtual env python runtime                            # the unchanged nextcloud_multi.py file
/usr/share/munin/custom-plugins/nextcloud-munin-py/venv/bin/python /usr/share/munin/custom-plugins/nextcloud-munin-py/nextcloud_multi.py $@
```

### configuration
To use these plugins properly some configuration parameters need to be added to the plugin-config `/etc/munin/plugin-config.d/z-custom-config`. 
```
[nextcloud_*]
env.username username
env.password password or logintoken
env.url https://URL.TO.YOUR.NEXTCLOUD.tld/ocs/v2.php/apps/serverinfo/api/v1/info
```

### activating the plugin
Finally you need to symlink the plugins you would like to activate into the munin plugin directory eg. `/etc/munin/plugins/`. 
Or if you want to use the multigraph plugin only symlink that one the the munin plugin directory.

After this has been done the munin-node needs to be restarted to facilitate the new plugins.
`systemctl restart munin-node`

### everything working?
To check if everything is working as expected check if the plugins are listed and actually gather data.
```
telnet localhost 4949 # localhost or IP the munin-node
list
fetch nextcloud_shares.py
num_fed_shares_received.value 1
num_shares_link_no_password.value 5
num_shares_user.value 13
num_shares.value 21
num_shares_link.value 5
num_shares_groups.value 0
num_fed_shares_sent.value 0
```
If everything works as it should, list will return the symlinked plugins within the list of active plugins. 

##### multipgrah plugin
To check if the multigraph plugin is working correctly, it is necessary to first instruct the multigraph capability, before the `list` instruction will list the plugin.
```
telnet localhost 4949 # localhost or IP the munin-node
cap multigraph
list
fetch nextcloud_multi.py
multigraph nextcloud_shares
num_fed_shares_received.value 1
num_shares_link_no_password.value 5
num_shares_user.value 13
num_shares.value 21
num_shares_link.value 5
num_shares_groups.value 0
num_fed_shares_sent.value 0
...
```

The `fetch` commands will run the script and return the gathered values. As long as none of them are NaN everything works as expected.

### uninstall
To remove the plugins from munin remove all symlinked plugins from the directory and restart the node.
