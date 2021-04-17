class SettingsObject:
    def __str__(self):
        strings = []
        for key, val in self.__dict__.items():
            if isinstance(val, SettingsObject):
                strings.append(f'{repr(key)}: {str(val)}')
            else:
                strings.append(f'{repr(key)}: {repr(val)}')
        return f's{{{", ".join(strings)}}}'

    def __repr__(self):
        return f'<Settings object { str(self) } >'
