"""
Brython MDCComponent: Core
==========================


"""

from browser import window, html

########################################################################
class MDCObject():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, view, mdc, element):
        """Constructor"""
        self.__mdc__ = mdc
        self.__view__ = view
        self.__element__ = element


    #----------------------------------------------------------------------
    def __getattr__(self, attr):
        """"""
        # print('__getattr__', attr)
        if hasattr(self.__view__, attr):  #check first for existence in view model, the method in view model can use MDC call
            #print('VIEW', self.__view__, attr)
            # return getattr(self.__view__, attr)

            # print(self.__view__)

            def inset(*args, **kwargs):
                return getattr(self.__view__, attr)(self.__element__, *args, **kwargs)
            return inset




        elif hasattr(self.__mdc__, attr):  #or look up in MDC
            #print('MDC')
            return getattr(self.__mdc__, attr)
        #print('NO ATTR')


    #----------------------------------------------------------------------
    def __getitem__(self, item):
        """"""
        # print('__getitem__', item)
        # print('HHHAg')
        return self.__view__[item]







########################################################################
class MDCCore:
    """"""


    #----------------------------------------------------------------------
    @classmethod
    def elevation(cls, element, Z):
        """"""
        cls.add_class(element, ['mdc-elevation--z{}'.format(Z), 'mdc-elevation-transition'])
        #cls.element.class_name += ' mdc-elevation--z{} mdc-elevation-transition'.format(Z)



    #----------------------------------------------------------------------
    @classmethod
    def add_class(cls, element, classes):
        """"""
        # if not isinstance(classes, (list, tuple, set)):
            # classes = [classes]

        # print(cls.element.class_name)

        # print(cls)

        for class_ in classes:
            if class_ in cls.CSS_classes:
                class_ = cls.CSS_classes[class_]

            element.class_name += ' {}'.format(class_)



    #----------------------------------------------------------------------
    @classmethod
    def remove_class(cls, element, classes):
        """"""
        # if not isinstance(classes, (list, tuple, set)):
            # classes = [classes]

        for class_ in classes:
            if class_ in cls.CSS_classes:
                class_ = cls.CSS_classes[class_]

            element.class_name = element.class_name.replace(class_, '')


    #----------------------------------------------------------------------
    @classmethod
    def toggle_class(cls, element, class_):
        """"""
        if class_ in cls.CSS_classes:
            class_ = cls.CSS_classes[class_]

        if class_ in cls.element.class_name:
            cls.remove_class(element, cls.mdc, [class_])
        else:
            cls.add_class(element, cls.mdc, [class_])


    #----------------------------------------------------------------------
    @classmethod
    def ripple(cls, element, theme=None, unbounded=False):
        """"""

        cls.add_class(element, ['mdc-ripple-surface'])
        if theme in ['primary', 'accent']:
            cls.add_class(element, ['mdc-ripple-surface--{}'.format(theme)])

        if unbounded:
            cls.element.setAttribute('data-mdc-ripple-is-unbounded', '')



    #----------------------------------------------------------------------
    @classmethod
    def theme(cls, element, theme, on=None):
        """"""
        if theme in ['primary', 'secondary', 'background', 'on-primary', 'on-secondary', 'secondary-bg', 'primary-bg']:
            cls.add_class(element, ['mdc-theme--{}'.format(theme)])

        elif theme in ['text-primary', 'text-secondary', 'text-hint', 'text-disabled', 'text-icon']:
            if on in ['light', 'dark']:
                cls.add_class(element, ['mdc-theme--{}-on-{}'.format(theme, on)])


    #----------------------------------------------------------------------
    @classmethod
    def typography(cls, element, typo='typography'):
        """"""

        if typo == 'typography':
            cls.add_class(element, ['mdc-typography'])

        elif typo in ['headline1', 'headline2', 'headline3', 'headline4', 'headline5', 'headline6']:
            cls.add_class(element, ['mdc-typography--{}'.format(typo)])

        elif typo in ['subtitle1', 'subtitle2']:
            cls.add_class(element, ['mdc-typography--{}'.format(typo)])

        elif typo in ['body1', 'body2']:
            cls.add_class(element, ['mdc-typography--{}'.format(typo)])

        elif typo in ['caption', 'button', 'overline']:
            cls.add_class(element, ['mdc-typography--{}'.format(typo)])




########################################################################
class MDCTemplate(MDCCore):
    """"""

    NAME = None, None
    CSS_classes = {}
    MDC_optionals = {}


    #----------------------------------------------------------------------
    def __new__(self, **kwargs):
        """"""
        self.element = self.render({}, kwargs)
        return self.element

    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <div></div>
        """
        return cls.render_html(code, context)


    #----------------------------------------------------------------------
    @classmethod
    def render(cls, locals_, kwargs, attach_now=True):
        """"""
        context = locals_.copy()
        context.pop('self')
        context.pop('kwargs')
        context.update(**kwargs)

        cls.html_element = cls.__html__(**context)

        if attach_now:
            cls.attach()


        if 'Class' in kwargs:
            cls.html_element.class_name += ' {Class}'.format(**kwargs)

        if 'id' in kwargs:
            cls.html_element.setAttribute('id', kwargs['id'])

        if 'style' in kwargs:
            cls.html_element.style = kwargs['style']

        if 'attr' in kwargs:
            for attr in kwargs['attr']:
                cls.html_element.setAttribute(attr, kwargs['attr'][attr])

        return cls.html_element


    #----------------------------------------------------------------------
    @classmethod
    def attach(cls):
        """"""

        html_element = cls.html_element

        name, mdcname = cls.NAME
        try:
            cls.mdc = getattr(getattr(window.mdc, name), mdcname).attachTo(html_element)
            html_element.mdc = MDCObject(cls, cls.mdc, html_element)
            # print('ATTACHED', mdcname)
        except:
            html_element.mdc = MDCObject(cls, None, html_element)
            cls.mdc = html_element.mdc
            #print(mdcname, ' is None')

        #try:
            #getattr(getattr(window.mdc, name), mdcname).new(html_element)
            ##print('ATTACHED', mdcname)
        #except:
            #pass
            ##print('no_attach', mdcname)

            # Riplleame
        # window.mdc.ripple.MDCRipple.attachTo(html_element)
        # try:
        # except:
            # pass


        #print('ATTACHED', mdcname)


    #----------------------------------------------------------------------
    @classmethod
    def render_html(cls, code, context):
        """"""

        classes = []
        for key in cls.CSS_classes.keys():
            if context.get(key, False):
                classes.append(cls.CSS_classes[key])
        context['CSS_classes'] = ' '.join(classes)



        for key in cls.MDC_optionals.keys():
            if context.get(key, False):
                #optionals[key] = cls.MDC_optionals[key]
                #classes.append(cls.CSS_classes[key])

                #vals = defaultdict(lambda: '', context)
                #context[key] = cls.MDC_optionals[key].format_map(**vals)

                try:
                    context[key] = cls.MDC_optionals[key].format(**context)
                except:

                    context[key] = cls.MDC_optionals[key]

            else:
                context[key] = ''


        code = code.format(**context)
        #return html.DIV(code).children[0]
        return cls.render_str(code)




    #----------------------------------------------------------------------
    @classmethod
    def render_str(cls, code):
        """"""
        return html.DIV(code).children[0]



    #----------------------------------------------------------------------
    @classmethod
    def new_id(cls):
        """"""
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        import random
        return ''.join([random.choice(ascii_lowercase) for l in range(2**5)])




    #----------------------------------------------------------------------
    @classmethod
    def get_id(cls, element=None):
        """"""
        return cls.ID


