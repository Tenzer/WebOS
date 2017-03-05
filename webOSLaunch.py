import os

import sublime
import sublime_plugin

from .webOS import WebosCommand


class WebosLaunchCommand(sublime_plugin.WindowCommand, WebosCommand):
    appinfo_path = None
    appinfo_data = None

    def run(self, paths=None):
        settings = sublime.load_settings('webOS.sublime-settings')
        global appinfo_path, appinfo_data

        if not paths:
            appinfo_path = self.get_appinfo_path()
        elif not os.path.isdir(paths[0]):
            appinfo_path = self.get_appinfo_path(currentfile=paths[0])
        else:
            appinfo_path = paths[0]
        appinfo_data = self.get_appinfo_data(appinfo_path=appinfo_path)

        if not appinfo_data:
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR : "appinfo.json" does not exist.'})
            return
        id = appinfo_data['id']
        ares_command = 'ares-install'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-install', '-d', settings.get('target'), '-l']
        command = [ares_command, '-d', settings.get('target'), '-l']
        self.run_command(command, callback=self.installedlist, status_message='checking the installed applications...')

    def installedlist(self, result):
        global appinfo_data, appinfo_path
        settings = sublime.load_settings('webOS.sublime-settings')

        # sometime installed list does not return
        if not result:
            ares_command = 'ares-install'
            if self.get_cli_path():
                ares_command = os.path.join(self.get_cli_path(), ares_command)
            # command = ['ares-install', '-d', settings.get('target'), '-l']
            command = [ares_command, '-d', settings.get('target'), '-l']
            self.run_command(command, callback=self.installedlist, status_message='checking the installed applications...')
            return

        if not appinfo_data:
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR : "appinfo.json" does not exist.'})
            return
        id = appinfo_data['id']

        if result.find('Error') != -1:
            sublime.active_window().run_command('webos_view_output', {'output': result})
            return

        if result.find(id) == -1:
            ipk = '{}_{}_all.ipk'.format(appinfo_data['id'], appinfo_data['version'])
            if not os.path.exists(os.path.join(appinfo_path, ipk)):
                self.package_action(callback=self.package_done)
            else:
                self.install_action(ipk, callback=self.install_done, appinfo_path=appinfo_path)

        else:
            self.launch_action(id)

    def package_done(self, result):
        global appinfo_path, appinfo_data

        ipk = '{}_{}_all.ipk'.format(appinfo_data['id'], appinfo_data['version'])
        self.install_action(ipk, callback=self.install_done, appinfo_path=appinfo_path)

    def install_done(self, result):
        global appinfo_data

        id = appinfo_data['id']
        self.launch_action(id)


class WebosPreviewCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self, paths=None):
        if not paths:
            appinfo_path = self.get_appinfo_path()
        elif not os.path.isdir(paths[0]):
            appinfo_path = self.get_appinfo_path(currentfile=paths[0])
        else:
            appinfo_path = paths[0]
        ares_command = 'ares-server'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        command = [ares_command, '-o', appinfo_path]
        self.run_command(command, show_status=False)


class WebosInstallLaunchCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self, paths=None):
        if not paths:
            appinfo_path = self.get_appinfo_path()
        elif not os.path.isdir(paths[0]):
            appinfo_path = self.get_appinfo_path(currentfile=paths[0])
        else:
            appinfo_path = paths[0]
        appinfo_data = self.get_appinfo_data(appinfo_path=appinfo_path)

        if not appinfo_data:
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR : "appinfo.json" does not exist.'})
            return

        self.id = appinfo_data['id']
        self.ipk = '{}_{}_all.ipk'.format(self.id, appinfo_data['version'])

        if not os.path.exists(os.path.join(appinfo_path, self.ipk)):
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR : "{}" does not exist.'.format(self.ipk)})
        else:
            self.install_action(self.ipk, callback=self.install_done, appinfo_path=appinfo_path)

    def install_done(self, result):
        if result.find('Error') != -1:
            sublime.active_window().run_command('webos_view_output', {'output': result})
            return
        else:
            self.launch_action(self.id)


class WebosPackageInstallLaunchCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self, paths=None):
        if not paths:
            self.appinfo_path = self.get_appinfo_path()
        elif not os.path.isdir(paths[0]):
            self.appinfo_path = self.get_appinfo_path(currentfile=paths[0])
        else:
            self.appinfo_path = paths[0]
        appinfo_data = self.get_appinfo_data(appinfo_path=self.appinfo_path)

        if not appinfo_data:
            sublime.active_window().run_command('webos_view_output', {'output': 'ERROR : "appinfo.json" does not exist.'})
            return

        self.id = appinfo_data['id']
        self.ipk = '{}_{}_all.ipk'.format(self.id, appinfo_data['version'])

        self.package_action(callback=self.package_done)

    def package_done(self, result):
        if result.find('Error') != -1:
            sublime.active_window().run_command('webos_view_output', {'output': result})
            return
        else:
            self.install_action(self.ipk, callback=self.install_done, appinfo_path=self.appinfo_path)

    def install_done(self, result):
        if result.find('Error') != -1:
            sublime.active_window().run_command('webos_view_output', {'output': result})
            return
        else:
            self.launch_action(self.id)
