import copy
import json
import os

import sublime
import sublime_plugin

from .webOS import WebosCommand


class WebosSetTargetCommand(sublime_plugin.WindowCommand, WebosCommand):
    def __init__(self, window):
        sublime_plugin.WindowCommand.__init__(self, window)
        self.device_data = []
        self.tv_data = []
        self.watch_data = []
        self.signage_data = []
        self.selected_target = -1
        self.settings = sublime.load_settings('webOS.sublime-settings')

        if not self.settings.get('CLIPATH'):
            if os.getenv('WEBOS_CLI_WD'):
                self.settings.set('CLIPATH', 'WEBOS_CLI_WD')
                self.settings.set('sdkType', 'Watch')
            elif os.getenv('WEBOS_CLI_SIGNAGE'):
                self.settings.set('CLIPATH', 'WEBOS_CLI_SIGNAGE')
                self.settings.set('sdkType', 'Signage')
            elif os.getenv('PARTNER_CLI_TV'):
                self.settings.set('CLIPATH', 'PARTNER_CLI_TV')
                self.settings.set('sdkType', 'PartnerTV')
            else:
                self.settings.set('CLIPATH', 'WEBOS_CLI_TV')
                self.settings.set('sdkType', 'TV')

    def run(self, index):
        self.settings.set('target', self.device_data[index]['name'])
        self.settings.set(
            'CLIPATH',
            {
                'TV': 'WEBOS_CLI_TV',
                'Watch': 'WEBOS_CLI_WD',
                'Signage': 'WEBOS_CLI_SIGNAGE',
                'PartnerTV': 'PARTNER_CLI_TV',
            }.get(self.device_data[index]['sdkType']),
        )
        self.settings.set('sdkType', self.device_data[index]['sdkType'])
        sublime.save_settings('webOS.sublime-settings')

    def is_checked(self, index):
        return index == self.selected_target

    def is_visible(self, index):
        return WebosCommand.is_visible(self) and index < len(self.device_data)

    def description(self, index):
        if index == 0:
            self.get_novacom_device_data()
            self.selected_target = -1
            self.set_selected_target_no()

        if index < len(self.device_data):
            if any([os.getenv(i) for i in ['WEBOS_CLI_TV', 'WEBOS_CLI_WD', 'WEBOS_CLI_SIGNAGE', 'PARTNER_CLI_TV']]):
                return '{name} ({sdkType})'.format(**self.device_data[index])
            return self.device_data[index]['name']

        # Make sure we always return a string
        return ''

    def set_selected_target_no(self):
        index = 0
        while index < len(self.device_data):
            if self.device_data[index]['sdkType'] == self.settings.get('sdkType') and self.device_data[index]['name'] == self.settings.get('target'):
                self.selected_target = index
                break
            index += 1
        if index == len(self.device_data):
            self.selected_target = 0
            if self.settings.get('sdkType') == 'Watch':
                self.selected_target = len(self.tv_data)
            self.settings.set('target', self.device_data[self.selected_target]['name'])
            sublime.save_settings('webOS.sublime-settings')

    def get_novacom_device_data(self):
        no_target = [{'name': 'No Targets'}]
        self.device_data = []
        self.tv_data = []
        self.watch_data = []
        self.signage_data = []
        if os.getenv('WEBOS_CLI_TV'):
            try:
                self.tv_data = json.loads(self.get_target_list(cli_path='WEBOS_CLI_TV')) or copy.copy(no_target)
                for data in self.tv_data:
                    data['sdkType'] = 'TV'
                    self.device_data.append(data)
            except ValueError:
                print('TV CLI ERROR')

        if os.getenv('PARTNER_CLI_TV'):
            try:
                partner_tv_data = json.loads(self.get_target_list(cli_path='PARTNER_CLI_TV')) or copy.copy(no_target)
                for data in partner_tv_data:
                    data['sdkType'] = 'PartnerTV'
                    self.device_data.append(data)
            except ValueError:
                print('Partner TV CLI ERROR')

        if os.getenv('WEBOS_CLI_WD'):
            try:
                self.watch_data = json.loads(self.get_target_list(cli_path='WEBOS_CLI_WD')) or copy.copy(no_target)
                for data in self.watch_data:
                    data['sdkType'] = 'Watch'
                    self.device_data.append(data)
            except ValueError:
                print('Watch CLI ERROR')

        if os.getenv('WEBOS_CLI_SIGNAGE'):
            try:
                self.signage_data = json.loads(self.get_target_list(cli_path='WEBOS_CLI_SIGNAGE')) or copy.copy(no_target)
                for data in self.signage_data:
                    data['sdkType'] = 'Signage'
                    self.device_data.append(data)
            except ValueError:
                print('Signage CLI ERROR')
