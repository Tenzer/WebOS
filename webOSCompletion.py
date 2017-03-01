import sublime
import sublime_plugin
import json

settings = sublime.load_settings("Preferences.sublime-settings")
current = settings.get("auto_complete_triggers", [])
# FIXME: Line below gives: TypeError: argument of type 'NoneType' is not iterable
# if not {"characters":":/.","selector":"source.js"} in current:
#   current.append(
#       {"characters":":/.","selector":"source.js"}
#   )
settings.set("auto_complete_triggers", current)


class webOSAutoComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        luna_service_data, enyo_completion_data = self.get_completion_data()
        luna_flag = self.check_luna_protocol(view)
        if luna_flag:
            self.remove_dot_from_separators(view)
            return ([(x["data"] + " ", x["data"]) for x in luna_service_data])
        else:
            self.add_dot_to_separators(view)
            prefix_word, trigger = self.get_prefix_word(view, view.sel()[0].end())
            if trigger == "." and (prefix_word == "enyo" or prefix_word == "moon" or prefix_word == "onyx"):
                return ([(x + " \t" + prefix_word + "-component", x) for x in enyo_completion_data[prefix_word]])
            elif trigger == ":" and prefix_word == "method":
                luna_api = self.find_luna_api(view)
                if luna_api is not None:
                    for data in luna_service_data:
                        if data['data'] == luna_api and prefix_word in data:
                            return ([(x + " ", "\"" + x + "\"") for x in data[prefix_word]])
                return []
            else:
                if self.check_method_protocols(view):
                    luna_api = self.find_luna_api(view)
                    if luna_api is not None:
                        for data in luna_service_data:
                            if data['data'] == luna_api and prefix_word in data:
                                return ([(x + " \tLS2", x) for x in data[prefix_word]])
                return []

    def check_method_protocols(self, view):
        current_position = view.sel()[0].end() - 1
        while current_position != 0 and view.substr(current_position - 1) != '(' and view.substr(current_position - 1) != '{' and view.substr(current_position - 1) != '\n':
            if view.substr(current_position) == ":" and view.substr(view.word(current_position - 1)) == 'method':
                return True
            current_position -= 1
        return False

    def find_luna_api(self, view):
        current_position = view.sel()[0].end() - 1
        while current_position != 0 and view.substr(current_position - 1) != '(':
            prefix_word, trigger = self.get_prefix_word(view, current_position)
            if prefix_word == "luna" and trigger == "://":
                self.remove_dot_from_separators(view)
                luna_api = view.substr(view.word(sublime.Region(current_position, current_position + 1)))
                self.return_separators(view)
                return luna_api
            current_position -= 1
        return None

    def check_luna_protocol(self, view):
        current_position = view.sel()[0].end() - 1
        while True:
            character = view.substr(current_position)
            if character == '.' or character == '/' or character == ':' or character.isalpha():
                current_position -= 1
            else:
                break
        trigger = view.substr(sublime.Region(current_position + 1, view.sel()[0].end()))
        return trigger.find("luna://") != -1

    def get_completion_data(self):
        enyo_completion_url = sublime.packages_path() + '/webOS/lib/enyoAPI.json'
        settings = sublime.load_settings("webOS.sublime-settings")
        luna_service_url = sublime.packages_path() + '/webOS/lib/LS2.' + settings.get('sdkType') + '.json'
        if luna_service_url is not None:
            with open(luna_service_url, 'rt') as file_object:
                luna_service_data = json.load(file_object)
        else:
            luna_service_data = []
        if enyo_completion_url is not None:
            with open(enyo_completion_url, 'rt') as file_object:
                enyo_completion_data = json.load(file_object)
        else:
            enyo_completion_data = {}
        return luna_service_data, enyo_completion_data

    def get_prefix_word(self, view, current_position):
        index = 1
        while True:
            character_region = sublime.Region(current_position - index - 1, current_position - index)
            character = view.substr(character_region)
            if character.isalpha() or current_position == 1:
                break
            index += 1
        prefix_word = view.substr(view.word(sublime.Region(current_position - index - 1, current_position - index)))
        trigger = view.substr(sublime.Region(current_position - index, current_position))
        return prefix_word, trigger

    def remove_dot_from_separators(self, view):
        word_separators = view.settings().get('word_separators')
        if not view.settings().get('word_separators_backup'):
            view.settings().set('word_separators_backup', word_separators)
        view.settings().set('word_separators', word_separators.replace(".", ""))

    def add_dot_to_separators(self, view):
        word_separators = view.settings().get('word_separators')
        if not view.settings().get('word_separators_backup'):
            view.settings().set('word_separators_backup', word_separators)
        if word_separators.find(".") == -1:
            view.settings().set('word_separators', word_separators + ".")

    def return_separators(self, view):
        if view.settings().get('word_separators_backup'):
            view.settings().set('word_separators', view.settings().get('word_separators_backup'))
