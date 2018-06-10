import yaml


class Profile:
    def __init__(self):
        self.bundles = dict()

        self.valid_link_options = dict(
            required={
                'src': {'types': [str], 'default': ''},
                'dst': {'types': [str], 'default': ''},
            },
            optional={
                'copy': {'types': [bool], 'default': False},
                'before': {'types': [str, list], 'default': ''},
                'after': {'types': [str, list], 'default': ''},
            }
        )

        self.valid_bundle_options = dict(
            required={
                'name': {'types': [str], 'default': ''},
                'links': {'types': [list], 'default': []},
            },
            optional={
                'generic': {'types': [bool], 'default': False},
                'desc': {'types': [str], 'default': ''},
            }
        )

        self.default = self._get_default()

    def _get_default(self):
        default = dict()
        for key, value in self.valid_link_options['optional'].items():
            default[key] = value['default']
        return default

    def _get_default_link_options(self):
        default_options = dict()
        for key, value in self.valid_link_options['required'].items():
            default_options[key] = value['default']
        for key, value in self.default.items():
            default_options[key] = value
        return default_options

    def _get_default_bundle_options(self):
        default_options = dict()
        for key, value in dict(self.valid_bundle_options['required'], **self.valid_bundle_options['optional']).items():
            default_options[key] = value['default']
        return default_options

    @staticmethod
    def _check_option(value, option: dict):
        if type(value) in option['types']:
            return True

    def check_options(self, options: dict, valid_options: dict, strict=False):
        if not isinstance(options, dict):
            return False
        # Check required options
        for key, value in valid_options['required'].items():
            if not (key in options and self._check_option(options[key], value)):
                return False

        # Check optional options
        for key, value in options.items():
            if (value is not None) and key in valid_options['optional']:
                if not self._check_option(value, valid_options['optional'][key]):
                    return False
            elif strict:
                return False

        return True

    @staticmethod
    def merge_options(old: dict, new: dict):
        for key, value in new.items():
            old[key] = value
        return old

    def create_link(self, options: dict):
        assert self.check_options(options, self.valid_link_options, strict=False)
        default = self._get_default_link_options()
        options = self.merge_options(default, options)
        return options

    def create_bundle(self, options: dict):
        assert self.check_options(options, self.valid_bundle_options, strict=False)
        default = self._get_default_bundle_options()
        options = self.merge_options(default, options)
        return options

    def save_to_yaml(self, fname: str):
        profile = dict(
            bundles=self.bundles,
            default=self.default,
        )
        try:
            with open(fname, 'w') as f:
                yaml.dump(f, profile)
        except IOError as e:
            print(e.args)

    def read_from_yaml(self, fname: str):
        try:
            with open(fname, 'r') as f:
                profile = yaml.load(f)
        except IOError as e:
            print(e.args)
            return False

        if isinstance(profile, dict):
            default_section = profile.get('default')
            if isinstance(default_section, dict):
                self.default = self.merge_options(self.default, default_section)

            bundle_section = profile.get('bundles')
            if isinstance(bundle_section, dict):
                for key, value in bundle_section.items():
                    value['name'] = key
                    bundle = self.create_bundle(value)
                    links = []
                    for ln in bundle['links']:
                        link = self.create_link(ln)
                        links.append(link)
                    bundle['links'] = links
                    self.bundles[key] = bundle
        else:
            return False
        return True


if __name__ == '__main__':
    p = Profile()
    status = p.read_from_yaml('/Users/xinhangliu/workspace/dotme/dotme.yml')
    print(status)
    print(p.default)
    for i in p.bundles.items():
        print(i['name'], i['desc'], i['generic'])
        for ln in i['links']:
            print(ln)
