
import creaturecast_rigging.nodes.depend_node as dep
import creaturecast_rigging.rigging.oscillator as osc
import creaturecast_rigging.rigging.transform_array as tay


class OscillatorArray(tay.TransformArray):

    default_data = dict(
        icon='wave',
        suffix='osy'
        )

    node_constructor = osc.Oscillator

    def __init__(self, *args, **kwargs):
        super(OscillatorArray, self).__init__(*args, **kwargs)

    def create(self):
        super(OscillatorArray, self).create()

        oscillators = self.nodes['items']
        position_plug = self.create_plug('position', type='double', k=True)
        amplitude_plug = self.create_plug('amplitude', dv=1.0, type='double', k=True)
        frequency_plug = self.create_plug('frequency', dv=1.0, type='double', k=True)
        offset_plug = self.create_plug('offset', dv=1.0, type='double', k=True)

        main_offset_remap_value = dep.DependNode(
            node_type='remapValue',
            parent=self,
        )

        main_offset_remap_value.plugs['value[0].value_Position'].set_value(0)
        main_offset_remap_value.plugs['value[0].value_FloatValue'].set_value(0)
        main_offset_remap_value.plugs['value[1].value_Position'].set_value(1)
        main_offset_remap_value.plugs['value[1].value_FloatValue'].set_value(1)

        for i, oscillator in enumerate(oscillators):

            offset_remap_value = dep.DependNode(
                node_type='remapValue',
                parent=oscillator,
                index=i
            )

            offset_multiply = dep.DependNode(
                node_type='multiplyDivide',
                parent=oscillator,
                index=i
            )

            offset_plug.connect_to(offset_multiply.plugs['input1X'])
            offset_multiply.plugs['input2X'].set_value(1.0 / len(oscillators) * (i-1))

            offset_multiply.plugs['outputX'].connect_to(offset_remap_value.plugs['inputValue'])

            main_offset_remap_value.plugs['value[0].value_Position'].connect_to(
                offset_remap_value.plugs['value[0].value_Position']
            )
            main_offset_remap_value.plugs['value[0].value_FloatValue'].connect_to(
                offset_remap_value.plugs['value[0].value_FloatValue']
            )
            main_offset_remap_value.plugs['value[1].value_Position'].connect_to(
                offset_remap_value.plugs['value[1].value_Position']
            )
            main_offset_remap_value.plugs['value[1].value_FloatValue'].connect_to(
                offset_remap_value.plugs['value[1].value_FloatValue']
            )

            offset_remap_value.plugs['outValue'].connect_to(oscillator.plugs['position'])
            amplitude_plug.connect_to(oscillator.plugs['amplitude'])
            frequency_plug.connect_to(oscillator.plugs['frequency'])
            position_plug.connect_to(oscillator.plugs['position'])
