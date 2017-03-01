import os
import sublime
import sublime_plugin

from webOS import WebosCommand

class WebosLaunchCommand(sublime_plugin.WindowCommand, WebosCommand):
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
    ares_command = 'ares-install'
    if self.get_cli_path():
      ares_command = os.path.join(self.get_cli_path(), ares_command)
    # command = ['ares-install', '-d', s.get('target'), '-l']
    command = [ares_command, '-d', s.get('target'), '-l']
    self.run_command(command, callback=self.installedlist, status_message='checking the installed applications...')

  def installedlist(self, result):
    global appinfo_data
    global appinfo_path
    s = sublime.load_settings("webOS.sublime-settings")

    # sometime installed list is not return
    if not result:
      ares_command = 'ares-install'
      if self.get_cli_path():
        ares_command = os.path.join(self.get_cli_path(), ares_command)
      # command = ['ares-install', '-d', s.get('target'), '-l']
      command = [ares_command, '-d', s.get('target'), '-l']
      self.run_command(command, callback=self.installedlist, stauts_message='checking the installed applications...')
      return 

    if not appinfo_data:
      self.view_output("ERROR : \"appinfo.json\" is not exist.")
      return 
    id = appinfo_data['id']

    if result.find('Error') != -1:
      self.view_output(result)
      return 

    if result.find(id) == -1:
      ipk = appinfo_data['id'] + '_' + appinfo_data['version'] + '_all.ipk'
      if not os.path.exists(os.path.join(appinfo_path,ipk)):
        self.package_action(callback=self.package_done)
      else:
        self.install_action(ipk, callback=self.install_done, appinfo_path=appinfo_path)

    else:
      self.launch_action(id)

  def package_done(self, result):
    global appinfo_path
    global appinfo_data

    s = sublime.load_settings("webOS.sublime-settings")
    ipk = appinfo_data['id'] + '_' + appinfo_data['version'] + '_all.ipk'      
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
      self.view_output("ERROR : \"appinfo.json\" is not exist.")
      return 

    self.id = appinfo_data['id']
    self.ipk = self.id + '_' + appinfo_data['version'] + '_all.ipk'

    if not os.path.exists(os.path.join(appinfo_path, self.ipk)):
      self.view_output("ERROR : \""+self.ipk+"\" is not exist.")
    else:
      self.install_action(self.ipk, callback=self.install_done, appinfo_path=appinfo_path)

  def install_done(self, result):
    if result.find('Error') != -1:
      self.view_output(result)
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
      self.view_output("ERROR : \"appinfo.json\" is not exist.")
      return 

    self.id = appinfo_data['id']
    self.ipk = self.id + '_' + appinfo_data['version'] + '_all.ipk'

    self.package_action(callback=self.package_done)

  def package_done(self, result):
    if result.find('Error') != -1:
      self.view_output(result)
      return
    else:
      self.install_action(self.ipk, callback=self.install_done, appinfo_path=self.appinfo_path)

  def install_done(self, result):
    if result.find('Error') != -1:
      self.view_output(result)
      return
    else:
      self.launch_action(self.id)

