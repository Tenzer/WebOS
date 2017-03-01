import os
import sublime_plugin

from webOS.webOS import WebosCommand


class WebosPackageCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self, mode, paths=None):
        if not paths:
            appinfo_path = None
        elif not os.path.isdir(paths[0]):
            appinfo_path = self.get_appinfo_path(currentfile=paths[0])
        else:
            appinfo_path = paths[0]
        self.package_action(mode, appinfo_path=appinfo_path)
