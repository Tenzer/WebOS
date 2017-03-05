import copy
import json
import os

import sublime
import sublime_plugin

from .webOS import WebosCommand

CLIPATH = {
    'TV': 'WEBOS_CLI_TV',
    'Watch': 'WEBOS_CLI_WD',
    'Signage': 'WEBOS_CLI_SIGNAGE',
    'PartnerTV': 'PARTNER_CLI_TV',
}

deviceData = []
tvDatas = []
watchDatas = []
signageDatas = []
selectedTarget = -1
settings = sublime.load_settings('webOS.sublime-settings')

if not settings.get('CLIPATH'):
    if os.getenv('WEBOS_CLI_WD'):
        settings.set('CLIPATH', 'WEBOS_CLI_WD')
        settings.set('sdkType', 'Watch')
    elif os.getenv('WEBOS_CLI_SIGNAGE'):
        settings.set('CLIPATH', 'WEBOS_CLI_SIGNAGE')
        settings.set('sdkType', 'Signage')
    elif os.getenv('PARTNER_CLI_TV'):
        settings.set('CLIPATH', 'PARTNER_CLI_TV')
        settings.set('sdkType', 'PartnerTV')
    else:
        settings.set('CLIPATH', 'WEBOS_CLI_TV')
        settings.set('sdkType', 'TV')


class WebosSetTargetCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self, index):
        global deviceData
        settings = sublime.load_settings('webOS.sublime-settings')
        settings.set('target', deviceData[index]['name'])
        settings.set('CLIPATH', CLIPATH[deviceData[index]['sdkType']])
        settings.set('sdkType', deviceData[index]['sdkType'])
        sublime.save_settings('webOS.sublime-settings')

    def is_checked(self, index):
        global selectedTarget
        return index == selectedTarget

    def is_visible(self, index):
        global deviceData
        if not WebosCommand.is_visible(self):
            return False
        if index < len(deviceData):
            return True
        return False

    def description(self, index):
        global deviceData, selectedTarget
        if index == 0:
            self.get_novacom_device_data()
            selectedTarget = -1
            self.set_selected_target_no()

        if index < len(deviceData):
            if any([os.getenv(i) for i in ['WEBOS_CLI_TV', 'WEBOS_CLI_WD', 'WEBOS_CLI_SIGNAGE', 'PARTNER_CLI_TV']]):
                return '{} ({})'.format(deviceData[index]['name'], deviceData[index]['sdkType'])
            return deviceData[index]['name']

    def set_selected_target_no(self):
        global deviceData, tvDatas, selectedTarget
        settings = sublime.load_settings('webOS.sublime-settings')
        index = 0
        while index < len(deviceData):
            if deviceData[index]['sdkType'] == settings.get('sdkType') and deviceData[index]['name'] == settings.get('target'):
                selectedTarget = index
                break
            index += 1
        if index == len(deviceData):
            selectedTarget = 0
            if settings.get('sdkType') == 'Watch':
                selectedTarget = len(tvDatas)
            settings.set('target', deviceData[selectedTarget]['name'])
            sublime.save_settings('webOS.sublime-settings')

    def get_novacom_device_data(self):
        no_target = [{'name': 'No Targets'}]
        global deviceData, watchDatas, tvDatas, signageDatas
        deviceData = []
        tvDatas = []
        watchDatas = []
        signageDatas = []
        if os.getenv('WEBOS_CLI_TV'):
            datas = self.get_target_list(cli_path='WEBOS_CLI_TV')
            try:
                tvDatas = json.loads(datas) or copy.copy(no_target)
                for data in tvDatas:
                    data['sdkType'] = 'TV'
                    deviceData.append(data)
            except ValueError:
                print('TV CLI ERROR')

        if os.getenv('PARTNER_CLI_TV'):
            datas = self.get_target_list(cli_path='PARTNER_CLI_TV')
            try:
                partner_tv_datas = json.loads(datas) or copy.copy(no_target)
                for data in partner_tv_datas:
                    data['sdkType'] = 'PartnerTV'
                    deviceData.append(data)
            except ValueError:
                print('Partner TV CLI ERROR')

        if os.getenv('WEBOS_CLI_WD'):
            datas = self.get_target_list(cli_path='WEBOS_CLI_WD')
            try:
                watchDatas = json.loads(datas) or copy.copy(no_target)
                for data in watchDatas:
                    data['sdkType'] = 'Watch'
                    deviceData.append(data)
            except ValueError:
                print('Watch CLI ERROR')

        if os.getenv('WEBOS_CLI_SIGNAGE'):
            datas = self.get_target_list(cli_path='WEBOS_CLI_SIGNAGE')
            try:
                signageDatas = json.loads(datas) or copy.copy(no_target)
                for data in signageDatas:
                    data['sdkType'] = 'Signage'
                    deviceData.append(data)
            except ValueError:
                print('Signage CLI ERROR')
