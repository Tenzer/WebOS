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
        return sdktype != 'Signage'


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
        return sdktype != 'Signage'


class WebosSdkHelpCommand(sublime_plugin.WindowCommand):
    def run(self):
        webbrowser.open_new('http://webostv.developer.lge.com/sdk/sublime-text-plugin/')


class WebosSdkVersionCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        version_info = 'Sublime Text webOS Plugin version: {}\nCopyright(C) 2014 LG Electronics'.format(settings.get('version'))
        sublime.message_dialog(version_info)
