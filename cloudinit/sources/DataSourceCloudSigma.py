# vi: ts=4 expandtab
#
#    Copyright (C) 2013 CloudSigma
#
#    Author: Kiril Vladimiroff <kiril.vladimiroff@cloudsigma.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3, as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from slugify import slugify
import yaml

from cloudinit import log as logging
from cloudinit import sources
from cloudinit import cs_utils
from cloudinit import util

LOG = logging.getLogger(__name__)


class DataSourceCloudSigma(sources.DataSource):
    def __init__(self, sys_cfg, distro, paths):
        self.cepko = cs_utils.Cepko()
        sources.DataSource.__init__(self, sys_cfg, distro, paths)

    def _to_cloud_config(self, input):
        if isinstance(input, basestring):
            input = yaml.load(input)

        return "#cloud-config\n{}".format(yaml.safe_dump(input))

    def get_data(self):
        try:
            server_context = self.cepko.all().result
            server_meta = server_context['meta']
            self.userdata_raw = self._to_cloud_config(server_meta.get("cloud-config", {}))
            self.metadata = server_context
            self.ssh_public_key = server_meta["ssh_public_key"]
        except:
            util.logexc(LOG, "Failed reading from the serial port")
            return False
        return True

    def get_hostname(self, fqdn=False):
        return slugify(self.metadata['name'])[:61]

    def get_public_ssh_keys(self):
        return [self.ssh_public_key]


# Used to match classes to dependencies
datasources = [
    (DataSourceCloudSigma, (sources.DEP_FILESYSTEM)),
]


def get_datasource_list(depends):
    """
    Return a list of data sources that match this set of dependencies
    """
    return sources.list_from_depends(depends, datasources)
