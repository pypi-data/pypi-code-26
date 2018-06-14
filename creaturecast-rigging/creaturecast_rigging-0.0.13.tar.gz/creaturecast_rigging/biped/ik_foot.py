import copy

import creaturecast_rigging.rigging.connect_curve as ccv
import creaturecast_rigging.rigging.template as tmp
import creaturecast_rigging.rigging.constraint as cnt
import creaturecast_rigging.rigging.handle as hdl
import creaturecast_rigging.rigging.joint_array as jry
import creaturecast_rigging.rigging.part as prt


class IkFootTemplate(prt.PartTemplate):

    default_data = copy.copy(prt.PartTemplate.default_data)
    default_data.update(dict(
        icon='joint_array',
        root_name='foot',
        suffix='fot',
    ))

    def __init__(self, *args, **kwargs):
        kwargs['count'] = 5
        super(IkFootTemplate, self).__init__(*args, **kwargs)
        self.constructor = IkFoot


    def create(self):
        super(IkFootTemplate, self).create()

        root_name = self.data['root_name']
        index_name = self.get_index_name()
        size = self.data['size']
        side = self.data['side']
        count = self.data['count']

        cones = []
        handles = []

        pivot_names = ['front', 'back', 'in', 'out']
        for i in range(4):
            handle = hdl.Handle(
                node_type='joint',
                parent=self,
                root_name='%s_%s' % (root_name, pivot_names[i]),
            )
            cone = tmp.Cone(
                root_name='%s_%s' % (root_name, pivot_names[i]),
                parent=handle,
                size=size*0.5,
                aim_vector=[1, 0, 0]
            ).create()
            cone.plugs['drawStyle'].set_value(2)
            cone.get_node('mesh').set_node('shader', alt_shader)
            handle.plugs['overrideEnabled'].set_value(True)
            handle.plugs['overrideRGBColors'].set_value(1)
            handle.plugs['overrideColorRGB'].set_value(nod.rig_settings['alternate_rgb'])
            cones.append(cone)
            handles.append(handle)
            cone.plugs['displayLocalAxis'].set_value(True)

        up_vector = nod.rig_settings['up_vector']
        reverse_aim_vector = [x*-1 for x in nod.rig_settings['aim_vector']]
        reverse_up_vector = [x*-1 for x in nod.rig_settings['up_vector']]

        cnt.AimConstraint(
            parent=self,
            build_kwargs={
                'mo': False,
                'aimVector': [-1, 0, 0],
                'upVector': [0, 1, 0],
                'worldUpType': 'scene'
            }).create(
            cones[0],
            cones[1],
        )
        cnt.AimConstraint(
            parent=self,
            build_kwargs={
                'mo': False,
                'aimVector': [-1, 0, 0],
                'upVector': [0, -1, 0],
                'worldUpType': 'scene'

            }).create(
            cones[1],
            cones[0],
        )
        cnt.AimConstraint(
            parent=self,
            build_kwargs={
                'mo': False,
                'aimVector': [-1, 0, 0],
                'upVector': [0, 1, 0],
                'worldUpType': 'scene'
            }).create(
            cones[2],
            cones[3],
        )
        cnt.AimConstraint(
            parent=self,
            build_kwargs={
                'mo': False,
                'aimVector': [-1, 0, 0],
                'upVector': [0, -1, 0],
                'worldUpType': 'scene'
            }).create(
            cones[3],
            cones[2],
        )

        ccv.ConnectCurve(
            parent=self,
            index=1,
        ).create(handles[0], handles[1])

        ccv.ConnectCurve(
            parent=self,
            index=1,
        ).create(handles[2], handles[3])

        self.set_nodes('handles', handles)
        self.set_nodes('joints', cones)

        return self


class IkFoot(prt.PartTemplate):

    default_data = copy.copy(prt.PartTemplate.default_data)
    default_data.update(dict(
        icon='joint_array',
        root_name='foot',
        suffix='fot',
    ))

    def __init__(self, *args, **kwargs):
        kwargs['count'] = 5
        super(IkFoot, self).__init__(*args, **kwargs)
        self.constructor = IkFootTemplate
        root_name = self.data['root_name']
        matrices = self.matrices
        size = self.data['size']

        joint_array = jry.JointArray(
            root_name=root_name,
            parent=self,
            matrices=matrices,
            parent_as_chain=True,
            size=size * 0.25
        ).create()

        joints = joint_array.get_nodes('items')
        front_pivot, back_pivot, in_pivot, out_pivot = joints

        roll_plug = self.create_plug('roll', at='double', k=True)
        toe_plug = self.create_plug('toe', at='double', k=True)
        tip_plug = self.create_plug('tip', at='double', k=True, min=0)
        tilt_plug = self.create_plug('tilt', at='double', k=True)
        ball_tilt_plug = self.create_plug('ballTilt', at='double', k=True)
        tip_tilt_plug = self.create_plug('tipTilt', at='double', k=True)

        #ball_tilt_plug.connectTo(toePivot.plugs['rotateY'])
        tip_tilt_plug.connect_to(front_pivot.plugs['rotateZ'])

        '''
        toePlug.connectTo(toeHandle.groups[0].plugs['rotateZ'])
        tipPlug.connectTo(frontPivot.plugs['rotateZ'])

        tipTiltPlug.connectTo(frontPivot.plugs['rotateY'])
        ballTiltPlug.connectTo(toePivot.plugs['rotateY'])

        toeRollCon = mya.createNode('condition', name='%s_toeroll_con' % RIG.indexName)
        toeRollCon.plugs['operation'].value = 2
        rollPlug.connectTo(toeRollCon.plugs['firstTerm'])
        rollPlug.connectTo(toeRollCon.plugs['colorIfTrueR'])
        toeRollCon.plugs['outColorR'].connectTo(toePivot.plugs['rotateZ'])

        heelRollCon = mya.createNode('condition', name='%s_heelroll_con' % RIG.indexName)
        heelRollCon.plugs['operation'].value = 4
        rollPlug.connectTo(heelRollCon.plugs['firstTerm'])
        rollPlug.connectTo(heelRollCon.plugs['colorIfTrueR'])
        heelRollCon.plugs['outColorR'].connectTo(backPivot.plugs['rotateZ'])

        inCon = mya.createNode('condition', name='%s_out_con' % RIG.indexName)
        inCon.plugs['operation'].value = 2
        tiltPlug.connectTo(inCon.plugs['firstTerm'])
        tiltPlug.connectTo(inCon.plugs['colorIfTrueR'])
        inCon.plugs['outColorR'].connectTo(outPivot.plugs['rotateZ'])

        outCon = mya.createNode('condition', name='%s_in_con' % RIG.indexName)
        outCon.plugs['operation'].value = 4
        tiltPlug.connectTo(outCon.plugs['firstTerm'])
        tiltPlug.connectTo(outCon.plugs['colorIfTrueR'])
        outCon.plugs['outColorR'].connectTo(inPivot.plugs['rotateZ'])
        '''
        self.set_nodes('joints', joints)
