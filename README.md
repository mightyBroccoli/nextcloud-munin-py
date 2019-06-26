# Nextcloud Munin Plugin [![CodeFactor](https://www.codefactor.io/repository/github/mightybroccoli/nextcloud-munin-py/badge/master)](https://www.codefactor.io/repository/github/mightybroccoli/nextcloud-munin-py/overview/master)
Within this repository there are some basic Munin Plugins gathering information from the NextCloud external API. I choose to also include a multigraph plugin `nextcloud_multi.py` which does everything the other plugins dynamically.

There are requirements for using a multigraph plugin which can be read up here : [Munin-Monitoring.org/multigraphing](http://guide.munin-monitoring.org/en/latest/plugin/multigraphing.html)

## install
To use these plugins properly some configuration parameters need to be added to the plugin-config `/etc/munin/plugin-config.d/custom-config`. 
```
[nextcloud_*]
url = https://URL.TO.YOUR.NEXTCLOUD.tld/ocs/v2.php/apps/serverinfo/api/v1/info
username = username
password = password or logintoken
```
To install these plugins, you just have to symlink those plugins you would like to activate to the munin plugin directory eg. `/etc/munin/plugins/`. Or if you want to use the multigraph plugin only symlink that one the the munin plugin directory.

After this has been done the munin-node needs to be restarted to facilitate the new plugins.
`systemctl restart munin-node`

It is possible to run the plugins in a virtual environment, for that the environment needs to be initialized and the required packages to be installed.
```
virtualenv -p python3 /path/to/your/venv

pip install -r requirements.txt
```

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
