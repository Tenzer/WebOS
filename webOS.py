import os
import sys
import subprocess
import sublime
import sublime_plugin
import json
import threading
import functools


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
      output = proc.communicate()[0]
      if not output:
        output = ''
      main_thread(self.command_done, output)
    except subprocess.CalledProcessError as e:   
      main_thread(self.command_done, e.returncode)
      
class ThreadProgress():
    """
    Animates an indicator, [=   ], in the status area while a thread runs

    :param thread:
        The thread to track for activity

    :param message:
        The message to display next to the activity indicator

    :param success_message:
        The message to display once the thread is complete
    """

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
        after = (self.size - 1) - before

        sublime.status_message('%s [%s=%s]' % \
            (self.message, ' ' * before, ' ' * after))

        if not after:
            self.addend = -1
        if not before:
            self.addend = 1
        i += self.addend

        sublime.set_timeout(lambda: self.run(i), 100)

class WebosCommand(sublime_plugin.TextCommand):
  def run_command(self, command, callback=None, show_status=True, status_message=None, **kwargs):
    command = [arg for arg in command if arg]   
    if not callback:
      callback = self.command_done
    s = sublime.load_settings("webOS.sublime-settings")        
    thread = CliThread(command, callback, **kwargs)
    thread.start()

    if show_status:
      message = status_message or ' '.join(command)
      ThreadProgress(thread, message, '')

  def command_done(self, result):
    if not result.strip():
      return
    self.view_output(result)

  def view_output(self, output, **kwargs):
    if not hasattr(self, 'output_view'):
      self.output_view = sublime.active_window().get_output_panel("cli")
    self.output_view.set_read_only(False)
    self.output_view.erase(self.output_view.begin_edit(),sublime.Region(0,self.output_view.size()))
    self.output_view.insert(self.output_view.begin_edit(),0,output)
    self.output_view.end_edit(self.output_view.begin_edit())
    self.output_view.set_read_only(True)
    sublime.active_window().run_command("show_panel", {"panel": "output.cli"})

  def get_appinfo_path(self, currentfile=None):
    if not currentfile:
      currentfile = sublime.active_window().active_view().file_name()
    dir_path = os.path.dirname(currentfile)

    while True:
      parent_dir_path = os.path.dirname(dir_path)
      #root directory
      if parent_dir_path == dir_path:
        break;
      if os.path.exists(os.path.join(dir_path,'appinfo.json')):
        return dir_path
      else:
        dir_path = parent_dir_path
    return os.path.dirname(currentfile)

  def get_appinfo_data(self, appinfo_path=None):
    
    if not appinfo_path:
      appinfo_path = self.get_appinfo_path()
    if appinfo_path and os.path.exists(os.path.join(appinfo_path,'appinfo.json')):
      with open(os.path.join(appinfo_path,'appinfo.json'), 'rt') as f:
        return json.load(f)
    else:
      return False

  def package_action(self, mode='minify', callback=None, appinfo_path=None):
    print("Package Action")
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
    
    self.run_command(command, callback=callback, status_message='Packaging the application - '+ appinfo_path)

  def install_action(self, ipk, callback=None, appinfo_path=None):
    print("Install Action")
    s = sublime.load_settings("webOS.sublime-settings")
    if not appinfo_path:
      appinfo_path = self.get_appinfo_path()
    ares_command = 'ares-install'
    if self.get_cli_path():
      ares_command = os.path.join(self.get_cli_path(), ares_command)
    # command = ['ares-install', '-d', s.get('target'), os.path.join(appinfo_path,ipk)]
    command = [ares_command, '-d', s.get('target'), os.path.join(appinfo_path,ipk)]
    self.run_command(command, callback=callback, status_message='Installing the \''+ ipk + '\' into '+s.get('target'))

  def launch_action(self, id, callback=None):
    print("Launch Action")
    s = sublime.load_settings("webOS.sublime-settings")
    ares_command = 'ares-launch'
    if self.get_cli_path():
      ares_command = os.path.join(self.get_cli_path(), ares_command)
    # command = ['ares-launch', '-d', s.get('target'), id]
    command = [ares_command, '-d', s.get('target'), id]
    self.run_command(command, callback=callback, status_message='Launching the appliction('+id+') to '+s.get('target'))

  def get_sublime_path(self):
    if sublime.platform() == 'osx':
      return '/Applications/Sublime Text 2.app/Contents/SharedSupport/bin/subl'
    if sublime.platform() == 'linux':
      return open('/proc/self/cmdline').read().split(chr(0))[0]
    return sys.executable

  def add_folder_project(self, args):
    args.insert(0,self.get_sublime_path())
    return subprocess.Popen(args)

  def get_target_list(self, CLIPATH=None):
    shell = os.name == 'nt'
    ares_command = 'ares-setup-device'    
    if CLIPATH != None:
      ares_command = os.path.join(os.getenv(CLIPATH), ares_command)
    command = [ares_command, '-F']
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, universal_newlines=True)
    output = proc.communicate()[0]
    if not output:
      output = ''
    return output

  def get_cli_path(self):
    s = sublime.load_settings("webOS.sublime-settings")
    return os.getenv(s.get('CLIPATH'))
      
  def is_visible(self):
    s = sublime.load_settings("webOS.sublime-settings")
    # FIXME: Line below gives: TypeError: str expected, not NoneType
    # if not os.getenv(s.get('CLIPATH')):
    #   s.erase('CLIPATH')

    if not s.get('CLIPATH'):
      if os.getenv('WEBOS_CLI_WD'):
        s.set('CLIPATH', 'WEBOS_CLI_WD')
        s.set('sdkType', 'Watch')
      elif os.getenv('WEBOS_CLI_TV'):
        s.set('CLIPATH', 'WEBOS_CLI_TV')
        s.set('sdkType', 'TV')
      elif os.getenv('WEBOS_CLI_SIGNAGE'):
        s.set('CLIPATH', 'WEBOS_CLI_SIGNAGE')
        s.set('sdkType', 'Signage')
      elif os.getenv('PARTNER_CLI_TV'):
        s.set('CLIPATH', 'PARTNER_CLI_TV')
        s.set('sdkType', 'PartnerTV')
      else:
        return False

    if os.getenv('WEBOS_CLI_WD') or os.getenv('WEBOS_CLI_TV') or os.getenv('WEBOS_CLI_SIGNAGE') or os.getenv('PARTNER_CLI_TV'):
      return True
    return False


