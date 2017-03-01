import os
import subprocess
import sublime
import sublime_plugin
import json

from webOS.webOS import WebosCommand


class WebosDebugCommand(sublime_plugin.WindowCommand, WebosCommand):
    appinfo_path = None
    appinfo_data = None

    def run(self, paths=None):
        s = sublime.load_settings("webOS.sublime-settings")
        global appinfo_path
        global appinfo_data

        if not paths:
            appinfo_path = self.get_appinfo_path()
        elif not os.path.isdir(paths[0]):
            appinfo_path = self.get_appinfo_path(currentfile=paths[0])
        else:
            appinfo_path = paths[0]
        appinfo_data = self.get_appinfo_data(appinfo_path=appinfo_path)

        if not appinfo_data:
            self.view_output("ERROR : \"appinfo.json\" is not exist.")
            return
        id = appinfo_data['id']
        ares_command = 'ares-launch'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-launch', '-d', s.get('target'), '-i', id]
        command = [ares_command, '-d', s.get('target'), '-i', '-o', id]
        self.run_command(command, show_status=False)
