#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Plugin to monitor the amount shares to and from the specified nextcloud instance
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


class NextcloudShares:
    def __init__(self):
        instance = self.get_instance()
        self.config = [
            # shares
            ''.join(['graph_title Nextcloud Shares', instance['title']]),
            'graph_args --base 1000 -l 0',
            'graph_printf %.0lf',
            'graph_vlabel number of shares',
            'graph_info graph showing the number of shares',
            'graph_category nextcloud',
            instance['suffix'].join(['num_shares', '.label total number of shares']),
            instance['suffix'].join(['num_shares', '.info current over all total of shares']),
            instance['suffix'].join(['num_shares', '.min 0']),
            instance['suffix'].join(['num_shares_user', '.label user shares']),
            instance['suffix'].join(['num_shares_user', '.info current total of user shares']),
            instance['suffix'].join(['num_shares_user', '.min 0']),
            instance['suffix'].join(['num_shares_groups', '.label group shares']),
            instance['suffix'].join(['num_shares_groups', '.info current total of group shares']),
            instance['suffix'].join(['num_shares_groups', '.min 0']),
            instance['suffix'].join(['num_shares_link', '.label link shares']),
            instance['suffix'].join(['num_shares_link', '.info current total of shares through a link']),
            instance['suffix'].join(['num_shares_link', '.min 0']),
            instance['suffix'].join(['num_shares_mail', '.label mail shares']),
            instance['suffix'].join(['num_shares_mail', '.info current total of mail shares']),
            instance['suffix'].join(['num_shares_mail', '.min 0']),
            instance['suffix'].join(['num_shares_room', '.label room shares']),
            instance['suffix'].join(['num_shares_room', '.info current total of room shares']),
            instance['suffix'].join(['num_shares_room', '.min 0']),
            instance['suffix'].join(['num_shares_link_no_password', '.label link shares without a password']),
            instance['suffix'].join(['num_shares_link_no_password', '.info current total of shares through a link without a password protection']),
            instance['suffix'].join(['num_shares_link_no_password', '.min 0']),
            instance['suffix'].join(['num_fed_shares_sent', '.label federated shares sent']),
            instance['suffix'].join(['num_fed_shares_sent', '.info current total of federated shares sent']),
            instance['suffix'].join(['num_fed_shares_sent', '.min 0']),
            instance['suffix'].join(['num_fed_shares_received', '.label federated shares recieved']),
            instance['suffix'].join(['num_fed_shares_received', '.info current total of federated shares recieved']),
            instance['suffix'].join(['num_fed_shares_received', '.min 0'])
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
        shares = api_response['ocs']['data']['nextcloud']['shares']

        # append for every key in shares the key and the value if the key starts with "num"
        for key, value in shares.items():
            if key.startswith('num'):
                self.result.append(instance['suffix'].join(['{k}','.value {v}']).format(k=key, v=value))

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
    NextcloudShares().main()
