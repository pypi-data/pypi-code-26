try:
    from collections import OrderedDict
    import pretty_output
    import grammalecte
    import grammalecte.text as txt
    from grammalecte.graphspell.echo import echo
    from termcolor import colored

    import mistune, json

    def check_grammar(data):
        pretty_output.title_3('grammar')

        if isinstance(data, OrderedDict):
            result = ''
            for key, content in OrderedDict(data).items():
                pretty_output.info(key)
                markdown_check_grammar(content)


    def markdown_check_grammar(content):
        renderer = GrammarRenderer()
        markdown = mistune.Markdown(renderer=renderer)
        return markdown(content)


    class GrammarRenderer(mistune.Renderer):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.grammar_checker = grammalecte.GrammarChecker("fr")
            opt_on = []
            opt_off = ['apos', 'esp', 'typo', 'unit', 'num', 'nbsp']

            self.grammar_checker.gce.setOptions({'html': True, 'latex': True})
            self.grammar_checker.gce.setOptions({ opt: True for opt in opt_on if opt in self.grammar_checker.gce.getOptions() })
            self.grammar_checker.gce.setOptions({ opt: False for opt in opt_off if opt in self.grammar_checker.gce.getOptions() })

        def correct(self, text):
            grammer_check_result = json.loads(self.grammar_checker.generateParagraphAsJSON(0, text))
            for error in grammer_check_result['lGrammarErrors']:
                self.grammar_correction(text, error)
            for error in grammer_check_result['lSpellingErrors']:
                self.spelling_correction(text, error)

        def grammar_correction(self, text, error):
            start = error['nStart']
            end = error['nEnd']
            error_message = error['sMessage']
            suggestions = error['aSuggestions']

            message = '\n'
            before_error = text[0:start]
            error_text = text[start:end]
            after_error = text[end:]

            message += colored(before_error, 'green')
            message += colored(error_text, 'white', 'on_red')
            message += colored(after_error, 'green')

            message += colored('\n{}\n'.format(error_message), 'cyan')
            message += colored('suggestions: ', 'cyan')
            message += colored('{}'.format(', '.join(suggestions)), 'white', 'on_green')
            print(message)

        def spelling_correction(self, text, error):
            start = error['nStart']
            end = error['nEnd']
            error_message = error['sValue']

            message = '\n'
            before_error = text[0:start]
            error_text = text[start:end]
            after_error = text[end:]

            message += colored(before_error, 'green')
            message += colored(error_text, 'white', 'on_red')
            message += colored(after_error, 'green')

            message += colored('\n{}\n'.format(error_message), 'cyan')
            print(message)


        def header(self, text, level, raw):
            self.correct(text)
            return text

        def list_item(self, text):
            self.correct(text)
            return text

        def paragraph(self, text):
            self.correct(text)
            return text

        def text(self, text):
            return text

        def inline_html(self, text):
            return text

except ImportError:

    def check_grammar(data):
        pretty_output.title_3('grammalecte not installed')
