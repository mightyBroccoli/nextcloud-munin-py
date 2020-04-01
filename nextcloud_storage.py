#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Plugin to monitor the amount storage to and from the specified nextcloud instance
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


class NextcloudStorage:
    def __init__(self):
        self.config = [
            # storages
            'graph_title Nextcloud Storages',
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
            'num_storages_other.min 0'
        ]
        self.result = list()

    def parse_data(self, api_response):
        storage = api_response['ocs']['data']['nextcloud']['storage']

        # append for every key in storage the key and the value if the key starts with "num"
        for key, value in storage.items():
            if key.startswith('num_storages'):
                self.result.append('{k}.value {v}'.format(k=key, v=value))

    def run(self):
        # init request session with specific header and credentials
        with requests.Session() as s:
            # read credentials from env
            s.auth = (os.environ.get('username'), os.environ.get('password'))

            # update header for json
            s.headers.update({'Accept': 'application/json'})

            # request the data
            url = ''.join([os.environ.get('url'), '/ocs/v2.php/apps/serverinfo/api/v1/info'])
            r = s.get(url)

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
    NextcloudStorage().main()
