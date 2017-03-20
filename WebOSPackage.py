import sublime
import sublime_plugin

from .WebOS import WebosCommand


class WebosPackageCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self, mode):
        appinfo_path = self.get_appinfo_path()
        if not appinfo_path:
            sublime.error_message('ERROR: "appinfo.json" could not be found.')
            return

        self.package_action(mode, appinfo_path=appinfo_path)
