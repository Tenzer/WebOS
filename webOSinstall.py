import os

import sublime_plugin

from .webOS import WebosCommand


class WebosInstallCommand(sublime_plugin.WindowCommand, WebosCommand):
    appinfo_path = None

    def run(self, paths=None):
        if not paths:
            appinfo_path = self.get_appinfo_path()
        elif not os.path.isdir(paths[0]):
            appinfo_path = self.get_appinfo_path(currentfile=paths[0])
        else:
            appinfo_path = paths[0]
        appinfo_data = self.get_appinfo_data(appinfo_path=appinfo_path)

        if not appinfo_data:
            self.view_output('ERROR : "appinfo.json" is not exist.')
            return
        ipk = appinfo_data['id'] + '_' + appinfo_data['version'] + '_all.ipk'

        if not os.path.exists(os.path.join(appinfo_path, ipk)):
            self.package_action(callback=self.package_done, appinfo_path=appinfo_path)
        else:
            self.install_action(ipk, appinfo_path=appinfo_path)

    def package_done(self, result):
        global appinfo_path
        appinfo_data = self.get_appinfo_data(appinfo_path=appinfo_path)
        ipk = '{}_{}_all.ipk'.format(appinfo_data['id'], appinfo_data['version'])
        self.install_action(ipk)
