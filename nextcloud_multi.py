#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Plugin to monitor nextcloud external api statistics
#   * user activity
#   * db size
#   * share count
#   * available app updates
#
# Parameters understood:
#     config   (required)
#     autoconf (optional - used by munin-config)

# Magic markers - optional - used by installation scripts and
# munin-config:
#
#  #%# family=manual
#  #%# capabilities=autoconf
import requests
import sys
import os


class NextcloudMultiGraph:
    def __init__(self):
        title = os.path.basename(__file__)
        title = title.split("nextcloud_apps.py_",1)[1]
        if title:
            title = ' on ' + title
        else
            title = ''

        self.config = [
            # users
            'multigraph nextcloud_users',
            'graph_title Nextcloud User Activity' + title,
            'graph_args --base 1000 -l 0',
            'graph_printf %.0lf',
            'graph_vlabel connected users',
            'graph_info graph showing the number of connected user',
            'graph_category nextcloud',
            'last5minutes.label last 5 minutes',
            'last5minutes.info users connected in the last 5 minutes',
            'last5minutes.min 0',
            'last1hour.label last hour',
            'last1hour.info users connected in the last hour',
            'last1hour.min 0',
            'last24hours.label last 24 hours',
            'last24hours.info users connected in the last 24 hours',
            'last24hours.min 0',
            'num_users.label number of users',
            'num_users.info total number of users',
            'num_users.min 0',

            # shares
            'multigraph nextcloud_shares',
            'graph_title Nextcloud Shares' + title,
            'graph_args --base 1000 -l 0',
            'graph_printf %.0lf',
            'graph_vlabel number of shares',
            'graph_info graph showing the number of shares',
            'graph_category nextcloud',
            'num_shares.label total number of shares',
            'num_shares.info current over all total of shares',
            'num_shares.min 0',
            'num_shares_user.label user shares',
            'num_shares_user.info current total of user shares',
            'num_shares_user.min 0',
            'num_shares_groups.label group shares',
            'num_shares_groups.info current total of group shares',
            'num_shares_groups.min 0',
            'num_shares_link.label link shares',
            'num_shares_link.info current total of shares through a link',
            'num_shares_link.min 0',
            'num_shares_mail.label mail shares',
            'num_shares_mail.info current total of mail shares',
            'num_shares_mail.min 0',
            'num_shares_room.label room shares',
            'num_shares_room.info current total of room shares',
            'num_shares_room.min 0',
            'num_shares_link_no_password.label link shares without a password',
            'num_shares_link_no_password.info current total of shares through a link without a password protection',
            'num_shares_link_no_password.min 0',
            'num_fed_shares_sent.label federated shares sent',
            'num_fed_shares_sent.info current total of federated shares sent',
            'num_fed_shares_sent.min 0',
            'num_fed_shares_received.label federated shares recieved',
            'num_fed_shares_received.info current total of federated shares recieved',
            'num_fed_shares_received.min 0',

            # dbsize
            'multigraph nextcloud_dbsize',
            'graph_title Nextcloud Database Size' + title,
            'graph_args --base 1024 -l 0',
            'graph_vlabel size in byte',
            'graph_info graph showing the database size in byte',
            'graph_category nextcloud',
            'db_size.label database size in byte',
            'db_size.info users connected in the last 5 minutes',
            'db_size.draw AREA',
            'db_size.min 0',

            # available_updates
            'multigraph nextcloud_available_updates',
            'graph_title Nextcloud available App updates' + title,
            'graph_args --base 1000 -l 0',
            'graph_printf %.0lf',
            'graph_vlabel updates available',
            'graph_info graph showing the number of available app updates',
            'graph_category nextcloud',
            'num_updates_available.label available app updates',
            'num_updates_available.info number of available app updates',
            'num_updates_available.min 0',
            'num_updates_available.warning 1',

            # storages
            'multigraph nextcloud_storages',
            'graph_title Nextcloud Storages' + title,
            'graph_args --base 1000 -l 0',
            'graph_printf %.0lf',
            'graph_vlabel number',
            'graph_info graph showing the number of storages',
            'graph_category nextcloud',
            'num_storages.label total number of storages',
            'num_storages.info current over all total of storages',
            'num_storages.min 0',
            'num_storages_local.label number of local storages',
            'num_storages_local.info current over all total of storage',
            'num_storages_local.min 0',
            'num_storages_home.label number of home storages',
            'num_storages_home.info current over all total of storage',
            'num_storages_home.min 0',
            'num_storages_other.label number of other storages',
            'num_storages_other.info current over all total of storage',
            'num_storages_other.min 0',

            # filecount
            'multigraph nextcloud_filecount',
            'graph_title Nextcloud Files' + title,
            'graph_args --base 1000 -l 0',
            'graph_printf %.0lf',
            'graph_vlabel number of files',
            'graph_info graph showing the number of files',
            'graph_category nextcloud',
            'num_files.label number of files',
            'num_files.info current number of files in the repository',
            'num_files.min 0'
        ]
        self.result = list()

    def parse_data(self, api_response):
        # users
        users = api_response['ocs']['data']['activeUsers']
        num_users = api_response['ocs']['data']['nextcloud']['storage']['num_users']
        self.result.append('multigraph nextcloud_users')

        # append for every key in users the key and the value to the results
        for key, value in users.items():
            self.result.append('{k}.value {v}'.format(k=key, v=value))

        # append total number of users
        self.result.append('num_users.value %s' % num_users)

        # shares
        shares = api_response['ocs']['data']['nextcloud']['shares']
        self.result.append('multigraph nextcloud_shares')

        # append for every key in shares the key and the value if the key starts with "num"
        for key, value in shares.items():
            if key.startswith('num'):
                self.result.append('{k}.value {v}'.format(k=key, v=value))

        # dbsize
        dbsize = api_response['ocs']['data']['server']['database']['size']
        self.result.append('multigraph nextcloud_dbsize')
        self.result.append('db_size.value %s' % dbsize)

        # app updates
        # precaution for Nextcloud versions prior to version 14
        version = api_response['ocs']['data']['nextcloud']['system']['version'].split(sep=".")

        if int(version[0]) >= 14:
            num_updates_available = api_response['ocs']['data']['nextcloud']['system']['apps']['num_updates_available']
            self.result.append('multigraph nextcloud_available_updates')
            self.result.append('num_updates_available.value %s' % num_updates_available)

        # storage
        storage = api_response['ocs']['data']['nextcloud']['storage']
        self.result.append('multigraph nextcloud_storages')

        # append for every key in storage the key and the value if the key starts with "num"
        for key, value in storage.items():
            if key.startswith('num_storages'):
                self.result.append('{k}.value {v}'.format(k=key, v=value))

        # filecount
        num_files = api_response['ocs']['data']['nextcloud']['storage']['num_files']
        self.result.append('multigraph nextcloud_filecount')
        self.result.append('num_files.value %s' % num_files)

    def run(self):
        # init request session with specific header and credentials
        with requests.Session() as s:
            # read credentials from env
            s.auth = (os.environ.get('username'), os.environ.get('password'))

            # update header for json
            s.headers.update({'Accept': 'application/json'})

            # request the data
            r = s.get(os.environ.get('url'))

        # if status code is successful continue
        if r.status_code == 200:
            self.parse_data(r.json())

            # output results to stdout
            for el in self.result:
                print(el, file=sys.stdout)

        elif r.status_code == 996:
            print('server error')
        elif r.status_code == 997:
            print('not authorized')
        elif r.status_code == 998:
            print('not found')
        else:
            print('unknown error')

    def main(self):
        # check if any argument is given
        if sys.argv.__len__() >= 2:
            # check if first argument is config or autoconf if not fetch data
            if sys.argv[1] == "config":
                # output config list to stdout
                for el in self.config:
                    print(el, file=sys.stdout)

                # if DIRTYCONFIG true also return the corresponding values
                if os.environ.get('MUNIN_CAP_DIRTYCONFIG') == '1':
                    self.run()

            elif sys.argv[1] == 'autoconf':
                if None in [os.environ.get('username'), os.environ.get('password')]:
                    print('env variables are missing')
                else:
                    print('yes')
        else:
            self.run()


if __name__ == "__main__":
    NextcloudMultiGraph().main()
