import os
import re

import sublime
import sublime_plugin

from .WebOS import WebosCommand


class WebosCreateProjectCommand(sublime_plugin.WindowCommand, WebosCommand):
    variant = ""
    templates = []
    template = ""
    project_name = ""
    project_path = ""

    def run(self, variant):
        self.variant = variant

        ares_command = os.path.join(self.get_cli_path(), "ares-generate")
        command = [ares_command, "--list", self.variant]
        self.run_command(
            command,
            callback=self.set_template_list,
            status_message="Getting list of templates",
        )

    def set_template_list(self, result):
        self.templates.clear()

        for line in result.split("\n"):
            if line:
                split_line = re.split(r"  +", line)
                self.templates.append("{}: {}".format(split_line[0], split_line[3].replace("(default)", "")))

        sublime.active_window().show_quick_panel(self.templates, self.set_name)

    def set_name(self, template_index):
        if template_index == -1:
            return

        self.template, _ = self.templates[template_index].split(":", 1)

        sublime.active_window().show_input_panel("Input name", "", self.set_path, None, None)

    def set_path(self, project_name):
        self.project_name = project_name

        sublime.active_window().show_input_panel("Input path", self.get_default_path(), self.create_project, None, None)

    def create_project(self, project_path):
        self.project_path = project_path

        settings = sublime.load_settings("WebOS.sublime-settings")
        application_id = "id=com.example.app"
        if settings.get("sdkType") == "Signage":
            application_id = "id=com.lg.app.signage"

        ares_command = os.path.join(self.get_cli_path(), "ares-generate")
        if self.variant == "webapp":
            command = [
                ares_command,
                "--template",
                self.template,
                "--property",
                application_id,
                self.project_path,
            ]
        else:
            command = [
                ares_command,
                "--template",
                self.template,
                "--servicename",
                self.project_name,
                self.project_path,
            ]

        self.run_command(
            command,
            callback=self.add_project,
            status_message='Generating new project "{}" ({})'.format(self.project_name, self.project_path),
        )

    def add_project(self, result):
        if "Success" in result:
            self.add_folder_project(["-a", self.project_path])

        sublime.active_window().run_command("webos_view_output", {"output": result})
