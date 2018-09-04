# Nextcloud Munin Plugin
Some basic Munin Plugins gathering information from the NextCloud external API.

## install
To use these plugins properly some configuration parameters need to be added to the plugin-config `/etc/munin/plugin-config.d/munin-node`. 
```
[nextcloud_*]
url = https://URL.TO.YOUR.NEXTCLOUD.tld/ocs/v2.php/apps/serverinfo/api/v1/info
username = username
password = password or logintoken
```
After that the script needs to be placed in the munin plugin directory eg. `/etc/munin/plugins/`

The munin-node needs to be restarted to facilitate the new plugins.
`systemctl restart munin-node`

### everything working?
To check if everything is working as expected check if the plugins actually gather data.
```
telnet localhost 4949 # localhost or IP the munin-node
list
fetch nextcloud_shares
fetch nextcloud_users
```

If everything works as it should, list will return `nextcloud_shares` and `nextcloud_users` within the list of other active plugins. The `fetch` commands will run the script and return the gathered values. As long as none of them are NaN everything works as expected.

### uninstall
To remove the plugins from munin remove both plugins from the directory and restart the node.
