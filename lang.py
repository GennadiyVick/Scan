import locale
import json
import os


class Lang:
    def sys_lang(self):
        l,_ = locale.getdefaultlocale()
        return l.lower()[0:2]

    def __init__(self):
        l = self.sys_lang()
        #l = 'en'
        self.lang = 'default'
        fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lang.json')
        if os.path.isfile(fn):
            with open(fn, encoding='utf-8') as f:
                self.dic = json.load(f)
            values = list(self.dic.values())
            if l in values[0]:
                self.lang = l
        else:
            self.dic = {}

    def tr(self,s):
        if s in self.dic:
            return self.dic[s][self.lang]
        else:
            return s



