
import logging, os, re, sys, time, json
from configparser import ConfigParser, BasicInterpolation, ExtendedInterpolation
from bl.dict import Dict         # needed for dot-attribute notation
from bl.rglob import rglob
from collections import OrderedDict

LIST_PATTERN = "^\[\s*([^,]*)\s*(,\s*[^,]*)*,?\s*\]$"
DICT_ELEM = """(\s*['"].+['"]\s*:\s*[^,]+)"""
DICT_PATTERN = """^\{\s*(%s,\s*%s*)?,?\s*\}$""" % (DICT_ELEM, DICT_ELEM)
log = logging.getLogger(os.path.basename(__file__))

class Config(Dict):
    """class for holding application configuration in an Ini file. 

    Sample Usage:
    
    >>> cf_filename = os.path.join(os.path.dirname(__file__), "config_test.ini")
    >>> cf = Config(cf_filename)
    >>> cf.filename
    >>> cf.__dict__['__filename__'] == os.path.join(os.path.dirname(__file__), "config_test.ini")
    True
    >>> cf.Archive.path             # basic string conversion
    '/data/files'
    >>> cf.Test.debug               # boolean 
    True
    >>> cf.Test.list                # list with several types
    [1, 2, 'three', True, 4.0]
    >>> cf.Test.dict                # dict => Dict
    {'a': 1, 'b': 'two', 'c': False}
    >>> cf.Test.dict.a              # Dict uses dot-notation
    1
    """

    Interpolation = ExtendedInterpolation()

    def __init__(self, fn=None, interpolation=None, 
                split_list=None, join_list=None, **params):
        config = ConfigParser(interpolation=interpolation or self.Interpolation)
        config.optionxform = lambda option: option      # don't lowercase key names
        self.__dict__['__filename__'] = fn
        self.__dict__['__join_list__'] = join_list
        if fn is not None and os.path.exists(fn):
            if config.read(fn):
                self.parse_config(config, split_list=split_list)
            else:
                raise KeyError("Config file not found at %s" % fn)
        self.update(**params)

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__filename__)

    def parse_config(self, config, split_list=None):
        self.__dict__['ordered_keys'] = []
        for s in config.sections():
            self.__dict__['ordered_keys'].append(s)
            self[s] = Dict()
            for k, v in config.items(s):
                # resolve common data types
                if v.lower() in ['true', 'false', 'yes', 'no']:     # boolean
                    self[s][k] = config.getboolean(s, k)
                elif re.match("^\-?\d+$", v):                       # integer
                    self[s][k] = int(v)
                elif re.match("^\-?\d+\.\d*$", v):                  # float
                    self[s][k] = float(v)
                elif re.match(LIST_PATTERN, v):                     # list
                    self[s][k] = eval(v)
                elif re.match(DICT_PATTERN, v):                     # dict
                    self[s][k] = Dict(**eval(v))
                elif split_list is not None \
                and re.search(split_list, v) is not None:
                    self[s][k] = re.split(split_list, v)
                else:                                               # default: string
                    self[s][k] = v.strip()

    def write(self, fn=None, sorted=False, wait=0):
        """write the contents of this config to fn or its __filename__.
        """
        config = ConfigParser(interpolation=None)
        if sorted==True: keys.sort()
        for key in self.__dict__.get('ordered_keys') or self.keys():
            config[key] = {}
            ks = self[key].keys()
            if sorted==True: ks.sort()
            for k in ks:
                if type(self[key][k])==list and self.__join_list__ is not None:
                    config[key][k] = self.__join_list__.join([v for v in self[key][k] if v!=''])
                else:
                    config[key][k] = str(self[key][k])
        fn = fn or self.__dict__.get('__filename__')
        # use advisory locking on this file
        i = 0
        while os.path.exists(fn+'.LOCK') and i < wait:
            i += 1
            time.sleep(1)
        if os.path.exists(fn+'.LOCK'):
            raise FileExistsError(fn + ' is locked for writing')
        else:
            with open(fn+'.LOCK', 'w') as lf:
                lf.write(time.strftime("%Y-%m-%d %H:%M:%S %Z"))
            with open(fn, 'w') as f:
                config.write(f)
            os.remove(fn+'.LOCK')

class ConfigTemplate(Config):
    """load the config with interpolation=None, so as to provide a template"""
    Interpolation = None

    def expected_param_keys(self):
        """returns a list of params that this ConfigTemplate expects to receive"""
        expected_keys = []
        r = re.compile('%\(([^\)]+)\)s')
        for block in self.keys():
            for key in self[block].keys():
                s = self[block][key]
                if type(s)!=str: continue
                md = re.search(r, s)
                while md is not None:
                    k = md.group(1)
                    if k not in expected_keys:
                        expected_keys.append(k)
                    s = s[md.span()[1]:]
                    md = re.search(r, s)
        return expected_keys

    def render(self, fn=None, prompt=False, **params):
        """return a Config with the given params formatted via ``str.format(**params)``.
        fn=None         : If given, will assign this filename to the rendered Config.
        prompt=False    : If True, will prompt for any param that is None.
        """
        from getpass import getpass
        expected_keys = self.expected_param_keys()
        compiled_params = Dict(**params)
        for key in expected_keys:
            if key not in compiled_params.keys():
                if prompt==True:
                    if key=='password':
                        compiled_params[key] = getpass("%s: " % key)
                    else:
                        compiled_params[key] = input("%s: " % key)
                        if 'path' in key:
                            compiled_params[key] = compiled_params[key].replace('\\','')
                else:
                    compiled_params[key] = "%%(%s)s" % key

        config = ConfigTemplate(fn=fn, **self)
        config.__dict__['ordered_keys'] = self.__dict__.get('ordered_keys')
        for block in config.keys():
            for key in config[block].keys():
                if type(config[block][key])==str:
                    config[block][key] = config[block][key] % compiled_params
        return config

def package_config(path, template='__config__.ini.TEMPLATE', config_name='__config__.ini', **params):
    """configure the module at the given path with a config template and file.
        path        = the filesystem path to the given module
        template    = the config template filename within that path
        config_name = the config filename within that path
        params      = a dict containing config params, which are found in the template using %(key)s.
    """
    config_fns = []
    template_fns = rglob(path, template)
    for template_fn in template_fns:
        config_template = ConfigTemplate(fn=template_fn)
        config = config_template.render(
            fn=os.path.join(os.path.dirname(template_fn), config_name), 
            prompt=True, path=path, **params)
        config.write()
        config_fns.append(config.fn)
        log.info('wrote %r' % config)
    return config_fns

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1]=='test':
        import doctest
        doctest.testmod()
    elif sys.argv[1]=='package':
        path = sys.argv[2]
        params = {}
        for arg in sys.argv[3:]:
            params.update(**json.loads(arg))
        package_config(path, **params)
