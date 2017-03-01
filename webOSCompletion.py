import sublime
import sublime_plugin
import json
import os

from webOS.webOS import WebosCommand

s = sublime.load_settings("Preferences.sublime-settings")
current = s.get("auto_complete_triggers", [])
# FIXME: Line below gives: TypeError: argument of type 'NoneType' is not iterable
# if not {"characters":":/.","selector":"source.js"} in current:
#   current.append(
#       {"characters":":/.","selector":"source.js"}
#   )
s.set("auto_complete_triggers", current)


class webOSAutoComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        lunaServiceData, enyoCompletionData = self.get_completion_data()
        lunaFlag = self.check_luna_protocol(view)
        if lunaFlag:
            self.remove_dot_from_separators(view)
            return ([(x["data"] + " ", x["data"]) for x in lunaServiceData])
        else:
            self.add_dot_to_separators(view)
            prefixWord, trigger = self.get_prefix_word(view, view.sel()[0].end())
            if trigger == "." and (prefixWord == "enyo" or prefixWord == "moon" or prefixWord == "onyx"):
                return ([(x + " \t" + prefixWord + "-component", x) for x in enyoCompletionData[prefixWord]])
            elif trigger == ":" and prefixWord == "method":
                lunaAPI = self.find_lunaAPI(view)
                if lunaAPI is not None:
                    for Data in lunaServiceData:
                        if Data['data'] == lunaAPI and prefixWord in Data:
                            return ([(x + " ", "\"" + x + "\"") for x in Data[prefixWord]])
                return ([])
            else:
                if self.check_method_protocols(view):
                    lunaAPI = self.find_lunaAPI(view)
                    if lunaAPI is not None:
                        for Data in lunaServiceData:
                            if Data['data'] == lunaAPI and prefixWord in Data:
                                return ([(x + " \tLS2", x) for x in Data[prefixWord]])
                return ([])

    def check_method_protocols(self, view):
        currentPosition = view.sel()[0].end() - 1
        while currentPosition != 0 and view.substr(currentPosition - 1) != '(' and view.substr(currentPosition - 1) != '{' and view.substr(currentPosition - 1) != '\n':
            if view.substr(currentPosition) == ":" and view.substr(view.word(currentPosition - 1)) == 'method':
                return True
            currentPosition -= 1
        return False

    def find_lunaAPI(self, view):
        currentPosition = view.sel()[0].end() - 1
        while currentPosition != 0 and view.substr(currentPosition - 1) != '(':
            prefixWord, trigger = self.get_prefix_word(view, currentPosition)
            if prefixWord == "luna" and trigger == "://":
                self.remove_dot_from_separators(view)
                lunaAPI = view.substr(view.word(sublime.Region(currentPosition, currentPosition + 1)))
                self.return_separators(view)
                return lunaAPI
            currentPosition -= 1
        return None

    def check_luna_protocol(self, view):
        currentPosition = view.sel()[0].end() - 1
        while True:
            ch = view.substr(currentPosition)
            if ch == '.' or ch == '/' or ch == ':' or ch.isalpha():
                currentPosition -= 1
            else:
                break
        trigger = view.substr(sublime.Region(currentPosition + 1, view.sel()[0].end()))
        if trigger.find("luna://") != -1:
            return True
        else:
            return False

    def get_completion_data(self):
        enyo_completion_url = sublime.packages_path() + '/webOS/lib/enyoAPI.json'
        s = sublime.load_settings("webOS.sublime-settings")
        luna_service_url = sublime.packages_path() + '/webOS/lib/LS2.' + s.get('sdkType') + '.json'
        if luna_service_url is not None:
            with open(luna_service_url, 'rt') as f:
                lunaServiceData = json.load(f)
        else:
            lunaServiceData = []
        if enyo_completion_url is not None:
            with open(enyo_completion_url, 'rt') as f:
                enyoCompletionData = json.load(f)
        else:
            enyoCompletionData = {}
        return lunaServiceData, enyoCompletionData

    def get_prefix_word(self, view, currentPosition):
        index = 1
        while True:
            chRegion = sublime.Region(currentPosition - index - 1, currentPosition - index)
            ch = view.substr(chRegion)
            if ch.isalpha() or currentPosition == 1:
                break
            index += 1
        prefixWord = view.substr(view.word(sublime.Region(currentPosition - index - 1, currentPosition - index)))
        trigger = view.substr(sublime.Region(currentPosition - index, currentPosition))
        return prefixWord, trigger

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
