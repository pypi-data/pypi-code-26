import creaturecast_rigging.nodes.depend_node as dep
import creaturecast_rigging.nodes.transform as trn
import creaturecast_rigging.nodes.locator as loc


class Oscillator(trn.Transform):

    default_data = dict(
        suffix='osc',
        icon='single_wave',
    )

    def __init__(self, *args, **kwargs):
        super(Oscillator, self).__init__(*args, **kwargs)

    def create(self):
        super(Oscillator, self).create()
        root_name = self.data['root_name']
        sampler_transform = trn.Transform(
            root_name='%s_sampler' % root_name,
            parent=self
        )
        sampler_locator = loc.Locator(
            parent=sampler_transform
        )

        frequency_multiply = dep.DependNode(
            node_type='multiplyDivide',
            parent=sampler_transform,
        )

        degrees_divide = dep.DependNode(
            node_type='multiplyDivide',
            parent=sampler_transform,
        )


        self.plugs['inheritsTransform'].set_value(False)
        sampler_locator.plugs['visibility'].set_value(False)
        position_plug = self.create_plug('position', at='double', k=True)
        output_plug = self.create_plug('output', at='double', k=True)
        amplitude_plug = self.create_plug('amplitude', dv=1.0, at='double', k=True)
        frequency_plug = self.create_plug('frequency', dv=1.0, at='double', k=True)
        position_plug.connect_to(frequency_multiply.plugs['input1X'])
        frequency_plug.connect_to(frequency_multiply.plugs['input2X'])
        amplitude_plug.connect_to(sampler_transform.plugs['translateX'])

        frequency_multiply.plugs['outputX'].connect_to(degrees_divide.plugs['input1X'])
        degrees_divide.plugs['input2X'].set_value(360)

        degrees_divide.plugs['outputX'].connect_to(self.plugs['rotateZ'])
        sampler_locator.plugs['worldPosition[0].worldPositionY'].connect_to(output_plug)
        return self


