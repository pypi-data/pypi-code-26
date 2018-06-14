import copy
import creaturecast_rigging.nodes.shader as shd
import creaturecast_node.node as nod

rig_settings = nod.rig_settings


class AltShader(shd.Shader):

    default_data = copy.copy(shd.Shader.default_data)

    default_data.update(dict(
    ))

    def __init__(self, *args, **kwargs):
        kwargs['specularColor'] = [0.0, 0.0, 0.0]
        kwargs['transparency'] = [0.9, 0.9, 0.9]
        kwargs['ambientColor'] = rig_settings['alternate_rgb']
        kwargs['color'] = rig_settings['alternate_rgb']
        super(AltShader, self).__init__(*args, **kwargs)


class SideShader(shd.Shader):

    default_data = copy.copy(shd.Shader.default_data)

    default_data.update(dict(
    ))

    def __init__(self, *args, **kwargs):
        kwargs['specularColor'] = [0.0, 0.0, 0.0]
        kwargs['transparency'] = [0.9, 0.9, 0.9]
        kwargs['ambientColor'] = [0.5, 0.5, 0.5]
        kwargs['color'] = rig_settings['side_rgb'][kwargs.get('side', 0)]
        super(SideShader, self).__init__(*args, **kwargs)
