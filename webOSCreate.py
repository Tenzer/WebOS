import os
import sublime
import sublime_plugin

from webOS.webOS import WebosCommand


class WebosCreateApplicationCommand(sublime_plugin.WindowCommand, WebosCommand):
    template_list = []
    selected_index = -1
    create_path = None

    def run(self, paths=None):
        self.template_list = []
        if not paths:
            paths = os.path.join(os.getenv('USERHOME', os.path.expanduser('~')))
        elif not os.path.isdir(paths[0]):
            paths = os.path.dirname(paths[0])
        self.create_path = paths
        ares_command = 'ares-generate'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-generate', '-l']
        command = [ares_command, '-l', 'webapp']
        self.run_command(command, callback=self.set_application_template_list, status_message='getting the template list...')

    def set_application_template_list(self, result):
        bootplates = result.split('\n')
        for bootplate in bootplates:
            if bootplate:
                bootplate = bootplate.split(' ')
                self.template_list.append(bootplate[0])
        sublime.active_window().show_quick_panel(self.template_list, self.set_application_name)

    def set_application_name(self, selected_index):
        if selected_index != -1:
            self.selected_index = selected_index
            sublime.active_window().show_input_panel('Input your application name', '', self.create_application, None, None)

    def create_application(self, name):
        settings = sublime.load_settings("webOS.sublime-settings")
        if isinstance(self.create_path, list):
            self.create_path = os.path.join(self.create_path[0], name)
        else:
            self.create_path = os.path.join(self.create_path, name)
        ares_command = 'ares-generate'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-generate', '-t', self.template_list[self.selected_index][0], self.create_path]
        default_id = 'id=com.yourdomain.app'
        if settings.get('sdkType') == 'Signage':
            default_id = 'id=com.lg.app.signage'
        command = [ares_command, '-t', self.template_list[self.selected_index], '-p', default_id, self.create_path]
        self.run_command(command, callback=self.add_new_application, status_message='Generating the new application from template -' + name)

    def add_new_application(self, result):
        if result.find('Success'):
            self.add_folder_project(['-a', self.create_path])
        self.view_output(result)


class WebosCreateServiceCommand(sublime_plugin.WindowCommand, WebosCommand):
    service_list = []
    selected_index = -1
    create_path = None

    def run(self, paths=None):
        self.service_list = []
        self.onSidebar = True

        if not paths:
            paths = os.path.join(os.getenv('USERHOME', os.path.expanduser('~')))
        elif not os.path.isdir(paths[0]):
            paths = os.path.dirname(paths[0])
        self.create_path = paths

        ares_command = 'ares-generate'
        if self.get_cli_path():
            ares_command = os.path.join(self.get_cli_path(), ares_command)
        # command = ['ares-generate', '-l', 'webosService']
        command = [ares_command, '-l', 'jsservice']
        self.run_command(command, callback=self.set_services_list, status_message='getting the service template list...')

    def set_services_list(self, result):
        bootplates = result.split('\n')
        for bootplate in bootplates:
            if bootplate:
                bootplate = bootplate.split(' ')
                self.service_list.append(bootplate[0])
        sublime.active_window().show_quick_panel(self.service_list, self.set_service_name)

    def set_service_name(self, selected_index):
        if selected_index != -1:
            self.selected_index = selected_index
            sublime.active_window().show_input_panel('Input your service name', '', self.create_service, None, None)

    def create_service(self, name):
        if self.selected_index != -1:
            # self.selected_index = selected_index
            settings = sublime.load_settings("webOS.sublime-settings")
            ares_command = 'ares-generate'
            if self.get_cli_path():
                ares_command = os.path.join(self.get_cli_path(), ares_command)
            # command = ['ares-generate', '-t', self.service_list[self.selected_index][0], self.create_path]
            if settings.get('sdkType') == 'Signage':
                default_id = 'com.lg.app.signage.' + name
                self.create_path = os.path.join(self.create_path, name)
                command = [ares_command, '-t', self.service_list[self.selected_index], '-s', default_id, self.create_path, '-f']
            else:
                self.create_path = os.path.join(self.create_path, name)
                command = [ares_command, '-t', self.service_list[self.selected_index], '-s', name, self.create_path, '-f']

            self.run_command(command, callback=self.add_new_service, status_message='Generating the new application from template')

    def add_new_service(self, result):
        if result.find('Success') and self.onSidebar:
            self.add_folder_project(['-a', self.create_path])
        self.view_output(result)


class WebosCreateAppinfoCommand(sublime_plugin.WindowCommand, WebosCommand):
    def run(self, paths=None):
        if not paths:
            currentfile = sublime.active_window().active_view().file_name()
            dirname = os.path.basename(os.path.dirname(currentfile))
        elif not os.path.isdir(paths[0]):
            dirname = os.path.basename(os.path.dirname(paths[0]))
        else:
            dirname = os.path.basename(paths[0])

        view = sublime.active_window().new_file()
        sublime.active_window().active_view().set_name('appinfo.json')
        template = """{
    "id": "com.yourdomain.""" + dirname + """,
    "version": "0.0.1",
    "vendor": "My Company",
    "type": "web",
    "main": "index.html",
    "title": "singlepane",
    "icon": "icon.png",
    "uiRevision":2,
    "enyoVersion": "2.3.0"
  }
  """
        view.run_command("insert_snippet", {"contents": template})

    def is_enabled(self, paths=None):
        if not paths:
            appinfo_path = self.get_appinfo_path()
        elif not os.path.isdir(paths[0]):
            appinfo_path = self.get_appinfo_path(currentfile=paths[0])
        else:
            appinfo_path = paths[0]

        if self.get_appinfo_data(appinfo_path=appinfo_path):
            return False
        return True
