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


class NextcloudShares:
    def __init__(self):
        title = os.path.basename(__file__)
        title = title.split("nextcloud_apps.py_",1)[1]
        if title:
            title = ' on ' + title
        else
            title = ''

        self.config = [
            # shares
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
            'num_fed_shares_received.min 0'
        ]
        self.result = list()

    def parse_data(self, api_response):
        shares = api_response['ocs']['data']['nextcloud']['shares']

        # append for every key in shares the key and the value if the key starts with "num"
        for key, value in shares.items():
            if key.startswith('num'):
                self.result.append('{k}.value {v}'.format(k=key, v=value))

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
