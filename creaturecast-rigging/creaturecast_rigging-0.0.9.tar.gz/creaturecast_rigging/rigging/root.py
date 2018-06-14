import json
import creaturecast_rigging.nodes.depend_node as dep


import creaturecast_rigging.rigging.part_array as pry


class AbstractRoot(object):

    metadata_name = 'rigging_metadata'

    def __init__(self, *args, **kwargs):
        super(AbstractRoot, self).__init__()

    def save_to_metadata(self):
        self.plugs[self.metadata_name].set_value(self.serialize())


class RootTemplate(AbstractRoot, pry.PartArrayTemplate):

    default_data = dict(
        icon='ball_metal_silver_small',
        root_name='root_template',
        suffix='root'
    )

    def __init__(self, *args, **kwargs):

        super(RootTemplate, self).__init__(*args, **kwargs)
        self.constructor = Root

    def create(self):
        super(RootTemplate, self).create()
        self.create_plug(self.metadata_name, dt='string')
        self.create_geometry_group()
        return self

    def set_parent(self, parent):
        super(RootTemplate, self).set_parent(parent)

    def create_rig(self, parent=None):
        self.data['hierarchy_map'] = self.get_hierarchy_map()
        rig = super(RootTemplate, self).create_rig(parent=parent)
        return rig


    def create_tool(self):
        data = super(RootTemplate, self).create_tool()
        data['hierarchy_map'] = [x for x in self.get_hierarchy_map()]
        data['handle_translations'] = dict((x[0], x[1].values) for x in self.get_handle_translations())
        return data


class Root(pry.PartArray, AbstractRoot):

    default_data = dict(
        icon='ball_metal_silver_small',
        root_name='root',
        suffix='root'
    )

    def __init__(self, *args, **kwargs):
        super(Root, self).__init__(*args, **kwargs)
        self.constructor = RootTemplate

    def create(self):
        super(Root, self).create()
        self.create_plug(self.metadata_name, type='string')
        self.create_geometry_group()
        return self

    def set_parent(self, parent):
        if isinstance(parent, dep.DependNode):
            raise Exception('Failed to parent %s, %s\'s cannot be parented to other nodes' % (self, self.__class__.__name__))
        super(Root, self).set_parent(parent)

    def get_handle_spaces(self):
        for handle in self.get_nodes('handles', recursive=True):
            space = handle.get_node('space')
            if space:
                #Handle orient Spaces
                yield (handle.data['name'], [x.data['name'] for x in space.get_nodes('targets')])
            else:
                yield (handle.data['name'], [])

    def export_handle_spaces(self, path):
        space_data = dict()
        for data in self.get_handle_spaces():
            space_data[data[0]] = data[1]
            yield data
        cut.dataToDisk(space_data, path)

    def set_handle_spaces(self, data):
        all_handles = dict((x.data['name'], x) for x in self.get_nodes('handles', recursive=True))
        for handle_name in all_handles:
            if handle_name in data:
                handle = all_handles[handle_name]
                #Handle orient Spaces\
                targets = [all_handles[x] for x in data[handle_name] if x in all_handles]
                if targets:
                    handle.set_parent_spaces(targets)
            yield handle

    def import_handle_spaces(self, path):
        with open(path, mode='r') as f:
            data = json.loads(f.read())
            for handle in self.set_handle_spaces(data):
                yield handle

    def finalize(self):
        if 'handle_spaces' in self.data:
            [x for x in self.set_handle_spaces(self.data['handle_spaces'])]
        if 'hierarchy_map' in self.data:
            self.set_hierarchy_map(self.data['hierarchy_map'])
        if self.data.get('bind_skeleton', False) and not self.get_node('bind_skeleton'):
            self.create_bind_skeleton()
        super(Root, self).finalize()
        return self


    def _create_template(self, parent=None):
        if 'template_data' in self.data:
            template = mya.compile_blueprint(self.data['template_data'])
            pry.create_parts(template)
            [x for x in template.set_handle_translations(template.data['handle_translations'])]
            template.set_hierarchy_map(template.data['hierarchy_map'])
            return template
        else:
            raise Exception('Template data not found for %s. ' % self)

'''
import_namespace = 'TEMP_IMPORT_GEO_NAMESPACE'
path = '%s/scenes/%s_Model.mb' % (project, project.split('/')[-1])
cmds.file(
    path,
    i=True,
    namespace=import_namespace,
    mergeNamespacesOnClash=True,
    ra=True,
    ignoreVersion=True,
    options="v=0;"
)
assemblies = cmds.ls('%s:*' % import_namespace, assemblies=True)
if assemblies:
    cmds.parent(assemblies, self.parent.get_node('geometry_group').get_long_name())
    cmds.namespace(mv=(import_namespace, ':'), f=True)

#cmds.colorManagementPrefs(edit=True, cmEnabled=False)













path = '%s/data/%s_PositionComponents.json' % (project, self.parent)
[x for x in self.parent.import_position_components(path)]








path = '%s/data/%s_Hierarchy.json' % (project, self.parent)
[x for x in self.parent.import_hierarchy(path)]







'''