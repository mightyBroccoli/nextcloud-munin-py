# Nextcloud Munin Plugin
Within this repository there are some basic Munin Plugins gathering information from the NextCloud external API. I choose to also include a multigraph plugin `nextcloud_multi` which does everything the other plugins do but in one single request.

There are drawbacks to using a multigraph plugin which can be read up here : [Munin-Monitoring.org](http://guide.munin-monitoring.org/en/latest/plugin/multigraphing.html)

## install
To use these plugins properly some configuration parameters need to be added to the plugin-config `/etc/munin/plugin-config.d/munin-node`. 
```
[nextcloud_*]
url = https://URL.TO.YOUR.NEXTCLOUD.tld/ocs/v2.php/apps/serverinfo/api/v1/info
username = username
password = password or logintoken
```
To install these plugins, you just have to symlink those plugins you would like to activate to the munin plugin directory eg. `/etc/munin/plugins/`. Or if you want to use the multigraph plugin only symlink that one the the munin plugin directory.

After this has been done the munin-node needs to be restarted to facilitate the new plugins.
`systemctl restart munin-node`

### everything working?
To check if everything is working as expected check if the plugins are listed and actually gather data.
```
telnet localhost 4949 # localhost or IP the munin-node
list
fetch nextcloud_shares
fetch nextcloud_users
fetch nextcloud_db
fetch nextcloud_apps
```
If everything works as it should, list will return the symlinked plugins within the list of active plugins. 

##### multipgrah plugin
To check if the multigraph plugin is working correctly it is necessary to first instruct the capability multigraph before the `list` instruction.
```
telnet localhost 4949 # localhost or IP the munin-node
cap multigraph
list
fetch nextcloud_multi
```

The `fetch` commands will run the script and return the gathered values. As long as none of them are NaN everything works as expected.

### uninstall
To remove the plugins from munin remove all symlinked plugins from the directory and restart the node.
