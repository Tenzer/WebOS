import os
import webbrowser

import sublime
import sublime_plugin

from .WebOS import WebosCommand


class WebosInstalledappCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self):
        settings = sublime.load_settings('WebOS.sublime-settings')

        ares_command = os.path.join(self.get_cli_path(), 'ares-install')
        # command = ['ares-install', '-l', settings.get('target')]
        command = [ares_command, '-l', settings.get('target')]
        self.run_command(command, status_message='Getting the installed apps list from ' + settings.get('target'))

    def is_visible(self):
        settings = sublime.load_settings('WebOS.sublime-settings')
        sdktype = settings.get('sdkType')
        return sdktype != 'Signage'


class WebosRunningappCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self):
        settings = sublime.load_settings('WebOS.sublime-settings')

        ares_command = os.path.join(self.get_cli_path(), 'ares-launch')
        # command = ['ares-launch', '-r', settings.get('target')]
        command = [ares_command, '-r', settings.get('target')]

        self.run_command(command, status_message='Getting the running apps list from ' + settings.get('target'))

    def is_visible(self):
        settings = sublime.load_settings('WebOS.sublime-settings')
        sdktype = settings.get('sdkType')
        return sdktype != 'Signage'


class WebosSdkHelpCommand(sublime_plugin.WindowCommand):
    def run(self):
        webbrowser.open_new('https://github.com/Tenzer/WebOS')


class WebosSdkVersionCommand(sublime_plugin.WindowCommand):
    def run(self):
        sublime.message_dialog('Sublime Text WebOS Plugin\nCopyright(C) 2017 LG Electronics and Jeppe Toustrup')
