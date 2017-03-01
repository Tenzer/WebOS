import os
import subprocess
import sublime
import sublime_plugin
import json

from webOS import WebosCommand

CLIPATH = {
  "TV" : "WEBOS_CLI_TV",
  "Watch" : "WEBOS_CLI_WD",
  "Signage" : "WEBOS_CLI_SIGNAGE",
  "PartnerTV" : "PARTNER_CLI_TV"
}

deviceData = []
tvDatas = []
watchDatas = []
signageDatas = []
selectedTarget = -1
s = sublime.load_settings("webOS.sublime-settings")

if not s.get('CLIPATH'):
  if os.getenv('WEBOS_CLI_WD'):
    s.set('CLIPATH', 'WEBOS_CLI_WD')
    s.set('sdkType', 'Watch')
  elif os.getenv('WEBOS_CLI_SIGNAGE'):
    s.set('CLIPATH', 'WEBOS_CLI_SIGNAGE')
    s.set('sdkType', 'Signage')
  elif os.getenv('PARTNER_CLI_TV'):
    s.set('CLIPATH', 'PARTNER_CLI_TV')
    s.set('sdkType', 'PartnerTV')
  else :
    s.set('CLIPATH', 'WEBOS_CLI_TV')
    s.set('sdkType', 'TV')

class WebosSetTargetCommand(sublime_plugin.WindowCommand, WebosCommand):
  def run(self, index):
    global deviceData
    s = sublime.load_settings("webOS.sublime-settings")
    s.set('target', deviceData[index]['name'])
    s.set('CLIPATH', CLIPATH[deviceData[index]['sdkType']])
    s.set('sdkType', deviceData[index]['sdkType'])
    sublime.save_settings("webOS.sublime-settings")

  def is_checked(self, index):
    global selectedTarget
    if index == selectedTarget:
      return True

  def is_visible(self, index):
    global deviceData
    if not WebosCommand.is_visible(self):
      return False
    if index < len(deviceData):
      return True
    return False
  
  def description(self, index):
    global deviceData, watchDatas, tvDatas, signageDatas, selectedTarget
    if index == 0:
      self.get_novacom_device_data()
      selectedTarget = -1
      self.set_selected_target_no()      

    if index < len(deviceData):
      cnt = 0
      if os.getenv('WEBOS_CLI_TV'):
        cnt += 1
      if os.getenv('WEBOS_CLI_WD'):
        cnt += 1
      if os.getenv('WEBOS_CLI_SIGNAGE'):
        cnt += 1
      if os.getenv('PARTNER_CLI_TV'):
        cnt += 1

      if cnt > 1:
        return deviceData[index]['name'] + " (" +deviceData[index]['sdkType'] +")"
      return deviceData[index]['name']

  def set_selected_target_no(self):
    global deviceData, watchDatas, tvDatas, selectedTarget
    s = sublime.load_settings("webOS.sublime-settings")
    index = 0
    while (index < len(deviceData)):
      if deviceData[index]['sdkType'] == s.get('sdkType') and deviceData[index]['name'] == s.get('target'):
        selectedTarget = index
        break
      index += 1
    if index == len(deviceData):
      selectedTarget = 0
      if s.get('sdkType') == "Watch":
        selectedTarget = len(tvDatas)
      s.set('target', deviceData[selectedTarget]['name'])
      sublime.save_settings("webOS.sublime-settings")

  def get_novacom_device_data(self):
    noTarget = [{"name":"No Targets"}]    
    global deviceData, watchDatas, tvDatas, signageDatas
    deviceData = []
    tvDatas = []
    watchDatas = []
    signageDatas = []
    if os.getenv('WEBOS_CLI_TV'):
      datas = self.get_target_list(CLIPATH='WEBOS_CLI_TV')
      try:
        tvDatas = json.loads(datas)
        if len(tvDatas) == 0:
          tvDatas = json.loads(json.dumps(noTarget))
        for data in tvDatas:
          data['sdkType'] = 'TV'
          deviceData.append(data)
      except ValueError:
        print "TV CLI ERROR"
    
    if os.getenv('PARTNER_CLI_TV'):
      datas = self.get_target_list(CLIPATH='PARTNER_CLI_TV')
      try:
        partnerTvDatas = json.loads(datas)
        if len(partnerTvDatas) == 0:
          partnerTvDatas = json.loads(json.dumps(noTarget))
        for data in partnerTvDatas:
          data['sdkType'] = 'PartnerTV'
          deviceData.append(data)
      except ValueError:
        print "Partner TV CLI ERROR"
        
    if os.getenv('WEBOS_CLI_WD'):
      datas = self.get_target_list(CLIPATH='WEBOS_CLI_WD')
      try:
        watchDatas = json.loads(datas)
        if len(watchDatas) == 0:
          watchDatas = json.loads(json.dumps(noTarget))
        for data in watchDatas:
          data['sdkType'] = 'Watch'
          deviceData.append(data)
      except ValueError:
        print "Watch CLI ERROR"
    
    if os.getenv('WEBOS_CLI_SIGNAGE'):
      datas = self.get_target_list(CLIPATH='WEBOS_CLI_SIGNAGE')
      try:
        signageDatas = json.loads(datas)
        if len(signageDatas) == 0:
          signageDatas = json.loads(json.dumps(noTarget))
        for data in signageDatas:
          data['sdkType'] = 'Signage'
          deviceData.append(data)
      except ValueError:
        print "Signage CLI ERROR"

class WebosSetupAppinfoCommand(sublime_plugin.WindowCommand, WebosCommand):
  def run(self, paths=None):
    if not paths:
      appinfo_path = self.get_appinfo_path()
    elif not os.path.isdir(paths[0]):
      appinfo_path = self.get_appinfo_path(currentfile=paths[0])
    else:
      appinfo_path = paths[0]
    
    appinfo = os.path.join(appinfo_path,'appinfo.json')
    sublime.active_window().open_file(appinfo)
    
  def is_enabled(self, paths=None):
    if not paths:
      appinfo_path = self.get_appinfo_path()
    elif not os.path.isdir(paths[0]):
      appinfo_path = self.get_appinfo_path(currentfile=paths[0])
    else:
      appinfo_path = paths[0]

    if self.get_appinfo_data(appinfo_path=appinfo_path):
      return True
    return False
