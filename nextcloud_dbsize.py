#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Plugin to monitor the nextcloud database size
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
import re


class NextcloudDB:
    def __init__(self):
        instance = self.get_instance()
        self.config = [
            # dbsize
            ''.join(['graph_title Nextcloud Database Size', instance['title']]),
            'graph_args --base 1024 -l 0',
            'graph_vlabel size in byte',
            'graph_info graph showing the database size in byte',
            'graph_category nextcloud',
            instance['suffix'].join(['db_size', '.label database size in byte']),
            instance['suffix'].join(['db_size', '.info users connected in the last 5 minutes']),
            instance['suffix'].join(['db_size', '.draw AREA']),
            instance['suffix'].join(['db_size', '.min 0'])
        ]
        self.result = list()

    def get_instance(self):
        self.instance = { 'title': '', 'suffix': '' }
        instance_filename = os.path.basename(__file__)
        instance_tuple = instance_filename.rpartition('_')

        if 'nextcloud' != instance_tuple[0]:
            self.instance['title'] = ' on ' + instance_tuple[2]
            self.instance['suffix'] = '_' + re.sub(r'\W+', '', instance_tuple[2])

        return self.instance

    def parse_data(self, api_response):
        instance = self.get_instance()
        dbsize = api_response['ocs']['data']['server']['database']['size']
        self.result.append(instance['suffix'].join(['db_size','.value %s']) % dbsize)

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
    NextcloudDB().main()
