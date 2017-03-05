import functools
import json
import os
import subprocess
import sys
import threading

import sublime
import sublime_plugin


def main_thread(callback, *args, **kwargs):
    sublime.set_timeout(functools.partial(callback, *args, **kwargs), 0)


class CliThread(threading.Thread):
    def __init__(self, command, command_done):
        threading.Thread.__init__(self)
        self.command = command
        self.command_done = command_done

    def run(self):
        try:
            shell = os.name == 'nt'
            proc = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, universal_newlines=True)
            output = proc.communicate()[0] or ''
            main_thread(self.command_done, output)
        except subprocess.CalledProcessError as error:
            main_thread(self.command_done, error.returncode)


class ThreadProgress(object):
    '''
    Animates an indicator, [=   ], in the status area while a thread runs

    :param thread:
        The thread to track for activity

    :param message:
        The message to display next to the activity indicator

    :param success_message:
        The message to display once the thread is complete
    '''

    def __init__(self, thread, message, success_message):
        self.thread = thread
        self.message = message
        self.success_message = success_message
        self.addend = 1
        self.size = 8
        sublime.set_timeout(lambda: self.run(0), 100)

    def run(self, i):
        if not self.thread.is_alive():
            if hasattr(self.thread, 'result') and not self.thread.result:
                sublime.status_message('')
                return
            sublime.status_message(self.success_message)
            return

        before = i % self.size
        after = self.size - 1 - before

        sublime.status_message('{} [{}={}]'.format(self.message, ' ' * before, ' ' * after))

        if not after:
            self.addend = -1
        if not before:
            self.addend = 1
        i += self.addend

        sublime.set_timeout(lambda: self.run(i), 100)


class WebosViewOutputCommand(sublime_plugin.TextCommand):
    def run(self, edit, output=''):
        view = sublime.active_window().get_output_panel('cli')
        view.set_read_only(False)
        view.erase(edit, sublime.Region(0, view.size()))
        view.insert(edit, 0, output)
        view.set_read_only(True)
        sublime.active_window().run_command('show_panel', {'panel': 'output.cli'})


class WebosCommand(sublime_plugin.TextCommand):
    def run_command(self, command, callback=None, show_status=True, status_message=None, **kwargs):
        command = [arg for arg in command if arg]
        if not callback:
            callback = self.command_done
        thread = CliThread(command, callback, **kwargs)
        thread.start()

        if show_status:
            message = status_message or ' '.join(command)
            ThreadProgress(thread, message, '')

    def command_done(self, result):
        if not result.strip():
            return
        sublime.active_window().run_command('webos_view_output', {'output': result})

    def get_appinfo_path(self, currentfile=None):
        paths = [currentfile]

        project_data = sublime.active_window().project_data()
        if project_data:
            for folder in project_data.get('folders', {}):
                paths.append(folder.get('path'))

        paths.append(sublime.active_window().active_view().file_name())

        for path in paths:
            if not path:
                continue

            if os.path.isfile(path):
                path = os.path.dirname(path)

            while True:
                if os.path.exists(os.path.join(path, 'appinfo.json')):
                    return path

                if os.path.dirname(path) == path:
                    break

                path = os.path.dirname(path)

        return False

    def get_appinfo_data(self, appinfo_path=None):
        appinfo_path = appinfo_path or self.get_appinfo_path()

        if appinfo_path and os.path.exists(os.path.join(appinfo_path, 'appinfo.json')):
            with open(os.path.join(appinfo_path, 'appinfo.json'), 'rt') as appinfo_file:
                return json.load(appinfo_file)

        return False

    def package_action(self, mode='minify', callback=None, appinfo_path=None):
        print('Package Action')
        if not appinfo_path:
            appinfo_path = self.get_appinfo_path()

        ares_command = 'ares-package'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)

        if mode == 'nominify':
            command = [ares_command, appinfo_path, '-o', appinfo_path, '--no-minify']
        elif mode == 'rom':
            command = [ares_command, appinfo_path, '-o', appinfo_path, '--rom']
        else:
            command = [ares_command, appinfo_path, '-o', appinfo_path]

        self.run_command(command, callback=callback, status_message='Packaging the application - ' + appinfo_path)

    def install_action(self, ipk, callback=None, appinfo_path=None):
        print('Install Action')
        settings = sublime.load_settings('webOS.sublime-settings')
        if not appinfo_path:
            appinfo_path = self.get_appinfo_path()
        ares_command = 'ares-install'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-install', '-d', settings.get('target'), os.path.join(appinfo_path,ipk)]
        command = [ares_command, '-d', settings.get('target'), os.path.join(appinfo_path, ipk)]
        self.run_command(command, callback=callback, status_message='Installing the "{}" into {}'.format(ipk, settings.get('target')))

    def launch_action(self, id, callback=None):
        print('Launch Action')
        settings = sublime.load_settings('webOS.sublime-settings')
        ares_command = 'ares-launch'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-launch', '-d', settings.get('target'), id]
        command = [ares_command, '-d', settings.get('target'), id]
        self.run_command(command, callback=callback, status_message='Launching the application({}) to {}'.format(id, settings.get('target')))

    def get_sublime_path(self):
        if sublime.platform() == 'osx':
            return '/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl'
        if sublime.platform() == 'linux':
            return open('/proc/self/cmdline').read().split(chr(0))[0]
        return sys.executable

    def add_folder_project(self, args):
        args.insert(0, self.get_sublime_path())
        return subprocess.Popen(args)

    def get_target_list(self, cli_path=None):
        shell = os.name == 'nt'
        ares_command = 'ares-setup-device'
        if cli_path is not None:
            ares_command = os.path.join(os.getenv(cli_path), ares_command)
        command = [ares_command, '-F']
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, universal_newlines=True)
        return proc.communicate()[0] or ''

    def get_cli_path(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        return os.getenv(settings.get('CLIPATH'))

    def is_visible(self):
        settings = sublime.load_settings('webOS.sublime-settings')
        if not os.getenv(settings.get('CLIPATH', '')):
            settings.erase('CLIPATH')

        if os.getenv(settings.get('CLIPATH', '')):
            return True

        if not settings.get('CLIPATH'):
            if os.getenv('WEBOS_CLI_WD'):
                settings.set('CLIPATH', 'WEBOS_CLI_WD')
                settings.set('sdkType', 'Watch')
                return True
            elif os.getenv('WEBOS_CLI_TV'):
                settings.set('CLIPATH', 'WEBOS_CLI_TV')
                settings.set('sdkType', 'TV')
                return True
            elif os.getenv('WEBOS_CLI_SIGNAGE'):
                settings.set('CLIPATH', 'WEBOS_CLI_SIGNAGE')
                settings.set('sdkType', 'Signage')
                return True
            elif os.getenv('PARTNER_CLI_TV'):
                settings.set('CLIPATH', 'PARTNER_CLI_TV')
                settings.set('sdkType', 'PartnerTV')
                return True

        return False
