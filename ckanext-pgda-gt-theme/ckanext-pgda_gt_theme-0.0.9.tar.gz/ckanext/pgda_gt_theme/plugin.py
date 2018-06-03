import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h


class Pgda_Gt_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'pgda_gt_theme')

    def get_helpers(self):
        return {'pgda_list_groups': list_groups}


def list_groups():
    groups = toolkit.get_action('group_list')(data_dict={'all_fields': True})
    groups = map(lambda group: group_with_url(group), groups)
    return groups


def group_with_url(group):
    group['url'] = h.group_link(group)
    return group
