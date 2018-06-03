from IPython.terminal.prompts import Prompts, Token
from time import time, strftime, localtime
from colorama import Fore, Style

class CustomPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [
            (Token.Prompt, strftime("[%H:%M:%S] ", localtime())),
            (Token.Prompt, 'In ['),
            (Token.PromptNum, str(self.shell.execution_count)),
            (Token.Prompt, ']: '),
        ]

    def out_prompt_tokens(self):
        return [
            (Token.OutPrompt, strftime("[%H:%M:%S] ", localtime())),
            (Token.OutPrompt, 'Out['),
            (Token.OutPromptNum, str(self.shell.execution_count)),
            (Token.OutPrompt, ']: '),
        ]

class VarWatcher(object):
    def __init__(self, ip):
        self.shell = ip
        self.t_pre = time()
        self.texc = 0
        self.prev_texc = 0

    def pre_execute(self):
        self.t_pre = time()

    def post_execute(self):
        self.prev_texc = self.texc
        self.texc = time() - self.t_pre

        print(Fore.CYAN + '[{}s]'.format('{}'.format(self.texc)[:7]) + Style.RESET_ALL)
        # Only add or update user namespace var if it is safe to do so
        if 'texc' not in self.shell.user_ns or \
                self.shell.user_ns['texc'] == self.prev_texc:
            self.shell.push({'texc': self.texc})
        else:
            pass

def load_ipython_extension(ip):
    """Load the extension in IPython."""
    vw = VarWatcher(ip)
    ip.events.register('pre_execute', vw.pre_execute)
    ip.events.register('post_execute', vw.post_execute)
    ip.prompts = CustomPrompt(ip)
