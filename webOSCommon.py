import os
import webbrowser

import sublime
import sublime_plugin

from .webOS import WebosCommand


class WebosInstalledappCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        ares_command = 'ares-install'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-install', '-l', settings.get('target')]
        command = [ares_command, '-l', settings.get('target')]
        self.run_command(command, status_message='Getting the installed apps list from ' + settings.get('target'))

    def is_visible(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        sdktype = settings.get('sdkType')
        if sdktype == 'Signage':
            return False
        return True


class WebosRunningappCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        ares_command = 'ares-launch'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-launch', '-r', settings.get('target')]
        command = [ares_command, '-r', settings.get('target')]

        self.run_command(command, status_message='Getting the running apps list from ' + settings.get('target'))

    def is_visible(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        sdktype = settings.get('sdkType')
        if sdktype == 'Signage':
            return False
        return True


class WebosSdkHelpCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        sdktype = settings.get('sdkType')
        if sdktype == 'TV' or sdktype == 'PartnerTV':
            url = 'http://developer.lge.com/webOSTV/develop/web-app/developer-tools/webos-tv-plugin-sublime/'
        elif sdktype == 'Signage':
            url = 'http://developer.lge.com/webOSSignage/sdk/sdk-tools/'
        else:
            url = 'http://developer.lge.com/temp01/sdk/tools/sublime/guide/'
        webbrowser.open_new(url)


class WebosSdkVersionCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        version_info = '''
  Sublime Text webOS Plugin version : ''' + settings.get('version') + '''
  Copyright(C) 2014 LG Electronics
'''
        sublime.message_dialog(version_info)
