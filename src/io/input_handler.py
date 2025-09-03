import os

class InputHandler:
    def __init__(self, regex_file='input/regex.txt', string_file='input/w_string.txt'):
        self.regex = self._read_file(regex_file)
        self.input_string = self._read_file(string_file)

    def _read_file(self, path):
        with open(path, 'r') as f:
            return f.read().strip()