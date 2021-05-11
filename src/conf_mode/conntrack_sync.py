#!/usr/bin/env python3
#
# Copyright (C) 2021 VyOS maintainers and contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 or later as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from sys import exit
from vyos.config import Config
from vyos.configdict import dict_merge
from vyos.configverify import verify_interface_exists
from vyos.util import call
from vyos.util import read_file
from vyos.template import render
from vyos.template import get_ipv4
from vyos.validate import is_addr_assigned
from vyos.xml import defaults
from vyos import ConfigError
from vyos import airbag
airbag.enable()

config_file = '/run/conntrackd/conntrackd.conf'

def get_config(config=None):
    if config:
        conf = config
    else:
        conf = Config()
    base = ['service', 'conntrack-sync']
    if not conf.exists(base):
        return None

    conntrack = conf.get_config_dict(base, key_mangling=('-', '_'),
                                     get_first_key=True)
    # We have gathered the dict representation of the CLI, but there are default
    # options which we need to update into the dictionary retrived.
    default_values = defaults(base)
    conntrack = dict_merge(default_values, conntrack)

    conntrack['hash_size'] = read_file('/sys/module/nf_conntrack/parameters/hashsize')
    conntrack['table_size'] = read_file('/proc/sys/net/netfilter/nf_conntrack_max')

    return conntrack

def verify(conntrack):
    if not conntrack:
        return None

    if 'interface' not in conntrack:
        raise ConfigError('Interface not defined!')

    for interface in conntrack['interface']:
        verify_interface_exists(interface)
        # Interface must not only exist, it must also carry an IP address
        if len(get_ipv4(interface)) < 1:
            raise ConfigError(f'Interface {interface} requires an IP address!')

    if 'expect_sync' in conntrack:
        if len(conntrack['expect_sync']) > 1 and 'all' in conntrack['expect_sync']:
            raise ConfigError('Cannot configure all with other protocol')

    if 'listen_address' in conntrack:
        address = conntrack['listen_address']
        if not is_addr_assigned(address):
            raise ConfigError(f'Specified listen-address {address} not assigned to any interface!')

    return None

def generate(conntrack):
    if not conntrack:
        if os.path.isfile(config_file):
            os.unlink(config_file)
        return None

    render(config_file, 'conntrackd/conntrackd.conf.tmpl', conntrack)

    return None

def apply(conntrack):
    if not conntrack:
        call('systemctl stop conntrackd.service')
        return None

    call('systemctl restart conntrackd.service')
    return None

if __name__ == '__main__':
    try:
        c = get_config()
        verify(c)
        generate(c)
        apply(c)
    except ConfigError as e:
        print(e)
        exit(1)
