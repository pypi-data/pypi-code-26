"""
An full-blown application demoing a domain-specific usecase with Mayavi:
interactive design of coils.

This is example of electromagnetic coils design, an application is built to
enable a user to interactively position current loops while visualizing the
resulting magnetic field. For this purpose, it is best to use object-oriented
programming. Each current loop is written as an object (the `Loop` class), with
position, radius and direction attributes, and that knows how to calculate the
magnetic field it generates: its `Bnorm` is a property, that is recomputed when
the loop characteristic changes. These loop objects are available to the main
application class as a list. The total magnetic field created is the sum of
each individual magnetic field. It can be visualized via a Mayavi scene
embedded in the application class. As we use Traited objects for the current
loops, a dialog enabling modification of their attributes can be generated by
Traits and embedded in our application.

The full power of Mayavi is available to the application. Via the pipeline tree
view, the user can modify the visualization. Familiar interaction and movements
are possible in the figure. So is saving the visualization, or loading data. In
addition, as the visualization model, described by the pipeline, is separated
from the data that is visualized, contained in the data source, any
visualization module added by the user will update when coils are added or
changed.

Simpler examples of magnetic field visualization can be found on
:ref:`example_magnetic_field_lines` and :ref:`example_magnetic_field`.
The material required to understand this example is covered in section
:ref:`builing_applications`.

"""
# Author: Gael Varoquaux <gael.varoquaux@normalesup.org>
# Copyright (c) 2009, Enthought, Inc.
# License: BSD Style.

# Major scientific library imports
import numpy as np
from scipy import linalg, special

# Enthought library imports:
from traits.api import HasTraits, Array, CFloat, List, \
   Instance, on_trait_change, Property
from traitsui.api import Item, View, ListEditor, \
        HSplit, VSplit
from mayavi.core.ui.api import EngineView, MlabSceneModel, \
        SceneEditor

##############################################################################
# Module-level variables

# The grid of points on which we want to evaluate the field
X, Y, Z = np.mgrid[-0.15:0.15:20j, -0.15:0.15:20j, -0.15:0.15:20j]
# Avoid rounding issues :
f = 1e4  # this gives the precision we are interested by :
X = np.round(X * f) / f
Y = np.round(Y * f) / f
Z = np.round(Z * f) / f

##############################################################################
# A current loop class
class Loop(HasTraits):
    """ A current loop class.
    """

    #-------------------------------------------------------------------------
    # Public traits
    #-------------------------------------------------------------------------
    direction = Array(float, value=(0, 0, 1), cols=3,
                    shape=(3,), desc='directing vector of the loop',
                    enter_set=True, auto_set=False)

    radius    = CFloat(0.1, desc='radius of the loop',
                    enter_set=True, auto_set=False)

    position  = Array(float, value=(0, 0, 0), cols=3,
                    shape=(3,), desc='position of the center of the loop',
                    enter_set=True, auto_set=False)

    _plot      = None

    Bnorm   = Property(depends_on='direction,position,radius')

    view = View('position', 'direction', 'radius', '_')


    #-------------------------------------------------------------------------
    # Loop interface
    #-------------------------------------------------------------------------
    def base_vectors(self):
        """ Returns 3 orthognal base vectors, the first one colinear to
            the axis of the loop.
        """
        # normalize n
        n = self.direction / (self.direction**2).sum(axis=-1)

        # choose two vectors perpendicular to n
        # choice is arbitrary since the coil is symetric about n
        if  np.abs(n[0])==1 :
            l = np.r_[n[2], 0, -n[0]]
        else:
            l = np.r_[0, n[2], -n[1]]

        l /= (l**2).sum(axis=-1)
        m = np.cross(n, l)
        return n, l, m


    @on_trait_change('Bnorm')
    def redraw(self):
        if hasattr(self, 'app') and self.app.scene._renderer is not None:
            self.display()
            self.app.visualize_field()


    def display(self):
        """
        Display the coil in the 3D view.
        """
        n, l, m = self.base_vectors()
        theta = np.linspace(0, 2*np.pi, 30)[..., np.newaxis]
        coil = self.radius*(np.sin(theta)*l + np.cos(theta)*m)
        coil += self.position
        coil_x, coil_y, coil_z = coil.T
        if self._plot is None:
            self._plot = self.app.scene.mlab.plot3d(coil_x, coil_y, coil_z,
                                    tube_radius=0.007, color=(0, 0, 1),
                                    name='Coil')
        else:
            self._plot.mlab_source.trait_set(x=coil_x, y=coil_y, z=coil_z)


    def _get_Bnorm(self):
        """
        returns the magnetic field for the current loop calculated
        from eqns (1) and (2) in Phys Rev A Vol. 35, N 4, pp. 1535-1546; 1987.
        """
        ### Translate the coordinates in the coil's frame
        n, l, m = self.base_vectors()
        R       = self.radius
        r0      = self.position
        r       = np.c_[np.ravel(X), np.ravel(Y), np.ravel(Z)]

        # transformation matrix coil frame to lab frame
        trans = np.vstack((l, m, n))

        r -= r0   #point location from center of coil
        r = np.dot(r, linalg.inv(trans) )           #transform vector to coil frame

        #### calculate field

        # express the coordinates in polar form
        x = r[:, 0]
        y = r[:, 1]
        z = r[:, 2]
        rho = np.sqrt(x**2 + y**2)
        theta = np.arctan2(x, y)

        E = special.ellipe((4 * R * rho)/( (R + rho)**2 + z**2))
        K = special.ellipk((4 * R * rho)/( (R + rho)**2 + z**2))
        Bz =  1/np.sqrt((R + rho)**2 + z**2) * (
                    K
                  + E * (R**2 - rho**2 - z**2)/((R - rho)**2 + z**2)
                )
        Brho = z/(rho*np.sqrt((R + rho)**2 + z**2)) * (
                -K
                + E * (R**2 + rho**2 + z**2)/((R - rho)**2 + z**2)
                )
        # On the axis of the coil we get a divided by zero here. This returns a
        # NaN, where the field is actually zero :
        Brho[np.isnan(Brho)] = 0

        B = np.c_[np.cos(theta)*Brho, np.sin(theta)*Brho, Bz ]

        # Rotate the field back in the lab's frame
        B = np.dot(B, trans)

        Bx, By, Bz = B.T
        Bx = np.reshape(Bx, X.shape)
        By = np.reshape(By, X.shape)
        Bz = np.reshape(Bz, X.shape)

        Bnorm = np.sqrt(Bx**2 + By**2 + Bz**2)

        # We need to threshold ourselves, rather than with VTK, to be able
        # to use an ImageData
        Bmax = 10 * np.median(Bnorm)

        Bx[Bnorm > Bmax] = np.NAN
        By[Bnorm > Bmax] = np.NAN
        Bz[Bnorm > Bmax] = np.NAN
        Bnorm[Bnorm > Bmax] = np.NAN

        self.Bx = Bx
        self.By = By
        self.Bz = Bz
        return Bnorm


##############################################################################
# The application object
class Application(HasTraits):

    scene = Instance(MlabSceneModel, (), editor=SceneEditor())

    # The mayavi engine view.
    engine_view = Instance(EngineView)

    coils = List(Instance(Loop, (), allow_none=False),
                        editor=ListEditor(style='custom'),
                        value=[ Loop(position=(0, 0, -0.05), ),
                                 Loop(position=(0, 0,  0.05), ), ])


    Bx    = Array(value=np.zeros_like(X))
    By    = Array(value=np.zeros_like(X))
    Bz    = Array(value=np.zeros_like(X))
    Bnorm = Array(value=np.zeros_like(X))

    vector_field = None

    def __init__(self, **traits):
        HasTraits.__init__(self, **traits)
        self.engine_view = EngineView(engine=self.scene.engine)


    @on_trait_change('scene.activated,coils')
    def init_view(self):
        if self.scene._renderer is not None:
            self.scene.scene_editor.background = (0, 0, 0)
            for coil in self.coils:
                coil.app = self
                coil.display()

            self.visualize_field()

    def visualize_field(self):
        self.Bx    = np.zeros_like(X)
        self.By    = np.zeros_like(X)
        self.Bz    = np.zeros_like(X)
        self.Bnorm = np.zeros_like(X)
        self.scene.scene.disable_render = True
        for coil in self.coils:
            self.Bx += coil.Bx
            self.By += coil.By
            self.Bz += coil.Bz

        self.Bnorm = np.sqrt(self.Bx**2 + self.By**2 + self.Bz**2)

        if self.vector_field is None:
            self.vector_field = self.scene.mlab.pipeline.vector_field(
                                    X, Y, Z, self.Bx, self.By, self.Bz,
                                    scalars=self.Bnorm,
                                    name='B field')
            vectors = self.scene.mlab.pipeline.vectors(self.vector_field,
                                    mode='arrow', resolution=10,
                                    mask_points=6, colormap='YlOrRd',
                                    scale_factor=2*np.abs(X[0,0,0]
                                                          -X[1,1,1]) )
            vectors.module_manager.vector_lut_manager.reverse_lut = True
            vectors.glyph.mask_points.random_mode = False
            self.scene.mlab.axes()
            self.scp = self.scene.mlab.pipeline.scalar_cut_plane(
                                                      self.vector_field,
                                                      colormap='hot')
        else:
            # Modify in place the data source. The visualization will
            # update automaticaly
            self.vector_field.mlab_source.trait_set(
                u=self.Bx, v=self.By, w=self.Bz, scalars=self.Bnorm)
        self.scene.scene.disable_render = False


    view = View(HSplit(
                    VSplit(Item(name='engine_view',
                                   style='custom',
                                   resizable=True),
                            Item('coils', springy=True),
                        show_labels=False),
                        'scene',
                        show_labels=False),
                    resizable=True,
                    title='Coils...',
                    height=0.8,
                    width=0.8,
                )


##############################################################################
if __name__ == '__main__':
    app = Application()
    app.configure_traits()

