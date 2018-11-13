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
	def config(self):
		config = {
			'storage': [
				'graph_title Nextcloud Storage',
				'graph_args --base 1000 -l 0',
				'graph_vlabel number of storage',
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
		}

		return config

	def get_data(self, api_response):
		data = {
			'nextcloud_storage': [],
		}

		# storage
		storage = api_response['ocs']['data']['nextcloud']['storage']

		# append for every key in storage the key and the value if the key starts with "num"
		[data['nextcloud_storage'].append(str(key) + ".value " + str(storage[key]))
			for key in storage if key.startswith('num_storages')]

		return data

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
			result = self.get_data(r.json())

			# for key in results print every entry in dict
			[print('\n'.join(result[key])) for key in result.keys()]

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
				# for key in config().keys() print every entry in dict
				[print('\n'.join(self.config()[key])) for key in self.config().keys()]
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
	