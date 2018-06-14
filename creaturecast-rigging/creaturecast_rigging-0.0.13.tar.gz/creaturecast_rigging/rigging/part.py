import copy
import creaturecast_node.node as nod
import creaturecast_rigging.nodes.transform as trn
import creaturecast_rigging.math.matrix as mtx


class AbstractPart(trn.Transform):

    default_data = dict(
        base_type='abstract_part'
    )

    def __init__(self, *args, **kwargs):
        self.matrices = []
        if 'matrices' in kwargs:
            matrices = kwargs.pop('matrices', [])
            self.matrices = [mtx.Matrix(*x) for x in matrices]
            kwargs['count'] = len(self.matrices)
        elif 'count' in kwargs:
            for i in range(kwargs['count']):
                self.matrices.append(mtx.Matrix())
        else:
            raise Exception('Must specify matrices or count to create %s' % self.__class__.__name__)
        super(AbstractPart, self).__init__(*args, **kwargs)

    def create(self):

        super(AbstractPart, self).create()

        self.create_plug('size', dv=1.0)
        self.plugs['overrideVisibility'].value = True
        self.plugs['overrideRGBColors'].value = True
        self.plugs['overrideColorRGB'].value = nod.rig_settings['side_rgb'][self.data['side']]


        return self



class Part(AbstractPart):

    default_data = dict(
        base_type='part'
    )

    def __init__(self, *args, **kwargs):
        super(Part, self).__init__(*args, **kwargs)
        self.data['base_class'] = '%s.%s' % (Part.__module__, Part.__name__)
        self.constructor = PartTemplate
        self.template_mode = False


    def create_template(self, parent=None):
        template_data = self.data['template_data']
        template_data.update(
            parent=parent,
            created=False
        )
        template = self.constructor(**template_data)
        template.create()
        return template


class PartTemplate(AbstractPart):

    default_data = dict(
        base_type='part_template'
    )

    def __init__(self, *args, **kwargs):
        super(PartTemplate, self).__init__(*args, **kwargs)
        self.constructor = Part

    def create_rig(self, parent=None):
        data = dict(self.data)
        template_data = copy.copy(data)
        template_data.update(
            matrices=[x.matrix.values for x in self.nodes.get('handles', [])]
        )
        data.update(
            parent=parent,
            created=False,
            matrices=[x.matrix.values for x in self.nodes.get('joints', [])],
            template_data=template_data
        )
        rig = self.constructor(**data)
        rig.create()
        return rig
