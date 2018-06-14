import creaturecast_rigging.nodes.depend_node as dep


class Shader(dep.DependNode):

    default_data = dict(
        icon='shader',
        node_type='phong',
        color=[0.0, 0.0, 0.0],
        specular_color=[0.0, 0.0, 0.0],
        transparency=[0.9, 0.9, 0.9],
        ambient_color=[0.5, 0.5, 0.5],
        incandescence=[0.0, 0.0, 0.0],
        suffix='shd'
    )

    def __init__(self, *args, **kwargs):
        super(Shader, self).__init__(*args, **kwargs)

    def create(self):
        self.plugs['color'].value = self.data['color']
        self.plugs['transparency'].value = self.data['transparency']
        self.plugs['ambientColor'].value = self.data['ambient_color']
        self.plugs['incandescence'].value = self.data['incandescence']
        self.plugs['specularColor'].value = self.data['specular_color']
        return self
