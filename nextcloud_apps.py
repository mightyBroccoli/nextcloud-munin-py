#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Plugin to monitor the number of available nextcloud app updates
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


class NextcloudApps:
    def __init__(self):
        title = os.path.basename(__file__)
        title = title.split("nextcloud_apps.py_",1)[1]
        if title:
            title = ' on ' + title
        else
            title = ''

        self.config = [
            # available_updates
            'graph_title Nextcloud available App updates' + title,
            'graph_args --base 1000 -l 0',
            'graph_printf %.0lf',
            'graph_vlabel updates available',
            'graph_info graph showing the number of available app updates',
            'graph_category nextcloud',
            'num_updates_available.label available app updates',
            'num_updates_available.info number of available app updates',
            'num_updates_available.min 0',
            'num_updates_available.warning 1'
        ]
        self.result = list()

    def parse_data(self, api_response):
        # precaution for Nextcloud versions prior to version 14
        version = api_response['ocs']['data']['nextcloud']['system']['version'].split(sep=".")

        if int(version[0]) >= 14:
            num_updates_available = api_response['ocs']['data']['nextcloud']['system']['apps']['num_updates_available']
            self.result.append('num_updates_available.value %s' % num_updates_available)

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
    NextcloudApps().main()
