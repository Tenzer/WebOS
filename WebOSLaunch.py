import os

import sublime
import sublime_plugin

from .WebOS import WebosCommand


class WebosLaunchCommand(sublime_plugin.WindowCommand, WebosCommand):
    appinfo_path = None
    appinfo_data = None

    def run(self):
        settings = sublime.load_settings('WebOS.sublime-settings')

        ares_command = os.path.join(self.get_cli_path(), 'ares-install')
        # command = ['ares-install', '-d', settings.get('target'), '-l']
        command = [ares_command, '-d', settings.get('target'), '-l']
        self.run_command(command, callback=self.installedlist, status_message='checking the installed applications...')

    def installedlist(self, result):
        settings = sublime.load_settings('WebOS.sublime-settings')

        # sometime installed list does not return
        if not result:
            ares_command = os.path.join(self.get_cli_path(), 'ares-install')
            # command = ['ares-install', '-d', settings.get('target'), '-l']
            command = [ares_command, '-d', settings.get('target'), '-l']
            self.run_command(command, callback=self.installedlist, status_message='checking the installed applications...')
            return

        self.appinfo_path = self.get_appinfo_path(self.appinfo_path)
        if not self.appinfo_path:
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR: "appinfo.json" could not be found.'})
            return

        self.appinfo_data = self.get_appinfo_data(appinfo_path=self.appinfo_path)

        if result.find('Error') != -1:
            sublime.active_window().run_command('webos_view_output', {'output': result})
            return

        if result.find(self.appinfo_data['id']) == -1:
            ipk = '{id}_{version}_all.ipk'.format(**self.appinfo_data)
            if not os.path.exists(os.path.join(self.appinfo_path, ipk)):
                self.package_action(callback=self.package_done)
            else:
                self.install_action(ipk, callback=self.install_done, appinfo_path=self.appinfo_path)

        else:
            self.launch_action(self.appinfo_data['id'])

    def package_done(self, result):
        ipk = '{id}_{version}_all.ipk'.format(**self.appinfo_data)
        self.install_action(ipk, callback=self.install_done, appinfo_path=self.appinfo_path)

    def install_done(self, result):
        self.launch_action(self.appinfo_data['id'])


class WebosPreviewCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self):
        appinfo_path = self.get_appinfo_path()
        if not appinfo_path:
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR: "appinfo.json" could not be found.'})
            return

        ares_command = os.path.join(self.get_cli_path(), 'ares-server')
        command = [ares_command, '-o', os.path.join(appinfo_path, 'dist')]
        self.run_command(command, show_status=False)


class WebosInstallLaunchCommand(sublime_plugin.WindowCommand, WebosCommand):
    appinfo_data = None

    def run(self):
        appinfo_path = self.get_appinfo_path()
        if not appinfo_path:
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR: "appinfo.json" could not be found.'})
            return

        self.appinfo_data = self.get_appinfo_data(appinfo_path=appinfo_path)
        ipk = '{id}_{version}_all.ipk'.format(**self.appinfo_data)

        if not os.path.exists(os.path.join(appinfo_path, ipk)):
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR : "{}" does not exist.'.format(ipk)})
        else:
            self.install_action(self.ipk, callback=self.install_done, appinfo_path=appinfo_path)

    def install_done(self, result):
        if result.find('Error') != -1:
            sublime.active_window().run_command('webos_view_output', {'output': result})
            return
        else:
            self.launch_action(self.appinfo_data['id'])


class WebosPackageInstallLaunchCommand(sublime_plugin.WindowCommand, WebosCommand):
    appinfo_path = None
    appinfo_data = None

    def run(self):
        self.appinfo_path = self.get_appinfo_path(self.appinfo_path)
        if not self.appinfo_path:
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR: "appinfo.json" could not be found.'})
            return

        self.appinfo_data = self.get_appinfo_data(appinfo_path=self.appinfo_path)
        self.package_action(callback=self.package_done, appinfo_path=self.appinfo_path)

    def package_done(self, result):
        if result.find('Error') != -1:
            sublime.active_window().run_command('webos_view_output', {'output': result})
            return

        ipk = '{id}_{version}_all.ipk'.format(**self.appinfo_data)
        self.install_action(ipk, callback=self.install_done, appinfo_path=self.appinfo_path)

    def install_done(self, result):
        if result.find('Error') != -1:
            sublime.active_window().run_command('webos_view_output', {'output': result})
            return

        self.launch_action(self.appinfo_data['id'])
