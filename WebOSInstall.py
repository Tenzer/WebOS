import os

import sublime
import sublime_plugin

from .WebOS import WebosCommand


class WebosInstallCommand(sublime_plugin.WindowCommand, WebosCommand):
    appinfo_data = None

    def run(self):
        appinfo_path = self.get_appinfo_path()
        if not appinfo_path:
            sublime.error_message('ERROR: "appinfo.json" could not be found.')
            return

        self.appinfo_data = self.get_appinfo_data(appinfo_path=appinfo_path)
        ipk = '{id}_{version}_all.ipk'.format(**self.appinfo_data)

        if not os.path.exists(os.path.join(appinfo_path, ipk)):
            self.package_action(callback=self.package_done, appinfo_path=appinfo_path)
        else:
            self.install_action(ipk, appinfo_path=appinfo_path)

    def package_done(self, result):
        ipk = '{id}_{version}_all.ipk'.format(**self.appinfo_data)
        self.install_action(ipk)
