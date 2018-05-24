# -*- coding: utf-8 -*-
from setuptools import setup

# import importLongDescription
# long_description = importLongDescription.output()
long_description = u"""
Package xrt (XRayTracer) is a python software library for ray tracing and wave
propagation in x-ray regime. It is primarily meant for modeling synchrotron
sources, beamlines and beamline elements. Includes a GUI for creating a
beamline and interactively viewing it in 3D.

Features of xrt
---------------

* *Rays and waves*. Classical ray tracing and wave propagation via Kirchhoff
  integrals, also freely intermixed. No further approximations, such as thin
  lens or paraxial. The optical surfaces may have figure errors, analytical or
  measured. In wave propagation, partially coherent radiation is treated by
  incoherent addition of coherently diffracted fields generated per electron.

* *Publication quality graphics*. 1D and 2D position histograms are
  *simultaneously* coded by hue and brightness. Typically, colors represent
  energy and brightness represents beam intensity. The user may select other
  quantities to be encoded by colors: angular and positional distributions,
  various polarization properties, beam categories, number of reflections,
  incidence angle etc. Brightness can also encode partial flux for a selected
  polarization and incident or absorbed power. Publication quality plots are
  provided by matplotlib with image formats PNG, PostScript, PDF and SVG.

* *Unlimited number of rays*. The colored histograms are *cumulative*. The
  accumulation can be stopped and resumed.

* *Parallel execution*. xrt can be run in parallel in several threads or
  processes (can be opted), which accelerates the execution on multi-core
  computers. Alternatively, xrt can use the power of GPUs via OpenCL for
  running special tasks such as the calculation of an undulator source or
  performing wave propagation.

* *Scripting in Python*. xrt can be run within Python scripts to generate a
  series of images under changing geometrical or physical parameters. The image
  brightness and 1D histograms can be normalized to the global maximum
  throughout the series.

* *Synchrotron sources*. Bending magnet, wiggler, undulator and elliptic
  undulator are calculated internally within xrt. There is also a legacy
  approach to sampling synchrotron sources using the codes `ws` and `urgent`
  which are parts of XOP package. Please look the section "Comparison of
  synchrotron source codes" for the comparison between the implementations. If
  the photon source is one of the synchrotron sources, the total flux in the
  beam is reported not just in number of rays but in physical units of ph/s.
  The total power or absorbed power can be opted instead of flux and is
  reported in W. The power density can be visualized by isolines. The magnetic
  gap of undulators can be tapered. Undulators can be calculated in near field.
  Custom magnetic field is also possible. Undulators can be calculated on GPU,
  with a high gain in computation speed, which is important for tapering and
  near field calculations.

* *Shapes*. There are several predefined shapes of optical elements implemented
  as python classes. The inheritance mechanism simplifies creation of other
  shapes. The user specifies methods for the surface height and the surface
  normal. For asymmetric crystals, the normal to the atomic planes can be
  additionally given. The surface and the normals are defined either in local
  (x, y) coordinates or in user-defined parametric coordinates. Parametric
  representation enables closed shapes such as capillaries or wave guides. It
  also enables exact solutions for complex shapes (e.g. a logarithmic spiral)
  without any expansion. The methods of finding the intersections of rays with
  the surface are very robust and can cope with pathological cases as sharp
  surface kinks. Notice that the search for intersection points does not
  involve any approximation and has only numerical inaccuracy which is set by
  default as 1 fm. Any surface can be combined with a (differently and variably
  oriented) crystal structure and/or (variable) grating vector. Surfaces can be
  faceted.

* *Energy dispersive elements*. Implemented are crystals in dynamical
  diffraction, gratings (also with efficiency calculations), Fresnel zone
  plates, Bragg-Fresnel optics and multilayers in dynamical diffraction.
  Crystals can work in Bragg or Laue cases, in reflection or in transmission.
  The two-field polarization phenomena are fully preserved, also within the
  Darwin diffraction plateau, thus enabling the ray tracing of crystal-based
  phase retarders.

* *Materials*. The material properties are incorporated using three different
  tabulations of the scattering factors, with differently wide and differently
  dense energy meshes. Refractive index and absorption coefficient are
  calculated from the scattering factors. Two-surface bodies, such as plates or
  refractive lenses, are treated with both refraction and absorption.

* *Multiple reflections*. xrt can trace multiple reflections in a single
  optical element. This is useful, for example in 'whispering gallery' optics
  or in Montel or Wolter mirrors.

* *Non-sequential optics*. xrt can trace non-sequential optics where different
  parts of the incoming beam meet different surfaces. Examples of such optics
  are poly-capillaries and Wolter mirrors.

* *Singular optics*. xrt correctly propagates vortex beams, which can be used
  for studying the creation of vortex beams by transmissive or reflective
  optics.

* *Global coordinate system*. The optical elements are positioned in a global
  coordinate system. This is convenient for modeling a real synchrotron
  beamline. The coordinates in this system can be directly taken from a CAD
  library. The optical surfaces are defined in their local systems for the
  user's convenience.

* *Beam categories*. xrt discriminates rays by several categories: `good`,
  `out`, `over` and `dead`. This distinction simplifies the adjustment of
  entrance and exit slits. An alarm is triggered if the fraction of dead rays
  exceeds a specified level.

* *Portability*. xrt runs on Windows and Unix-like platforms, wherever you can
  run python.

* *Examples*. xrt comes with many examples; see the galleries, the links are at
  the top bar.

xrtQook -- a GUI for creating scripts
-------------------------------------

The main interface to xrt is through a python script. Many examples of such
scripts can be found in the supplied folder 'examples'. The script imports the
modules of xrt, instantiates beamline parts, such as synchrotron or geometric
sources, various optical elements, apertures and screens, specifies required
materials for reflection, refraction or diffraction, defines plots and sets job
parameters.

The Qt tool xrtQook takes these ingredients and prepares a ready to use script
that can be run within the tool itself or in an external Python context.
xrtQook features a parallelly updated help panel that, unlike the main
documentation, provides a complete list of parameters for the used classes,
also including those from the parental classes. xrtQook writes/reads the
recipes of beamlines into/from xml files.

xrtGlow -- an interactive 3D beamline viewer
--------------------------------------------

The beamline created in xrtQook can be interactively viewed in an OpenGL based
widget xrtGlow. It visualizes beams, footprints, surfaces, apertures and
screens. The brightness represents intensity and the color represents an
auxiliary user-selected distribution, typically energy. A virtual screen can be
put at any position and dragged by mouse with simultaneous observation of the
beam distribution on it.

The primary purpose of xrtGlow is to demonstrate the alignment correctness
given the fact that xrtQook can automatically calculate several positional and
angular parameters.

Dependencies
------------

numpy, scipy and matplotlib are required. If you use OpenCL for calculations on
GPU or CPU, you need AMD/NVIDIA drivers, ``Intel CPU only OpenCL runtime``
(these are search key words), pytools and pyopencl. PyQt4 or PyQt5 are needed
for xrtQook. Spyder (as library of Spyder IDE) is highly recommended for nicer
view of xrtQook. OpenGL is required for xrtGlow.

Python 2 and 3
--------------
The code can run in both Python branches without any modification.

Get xrt
-------
xrt is available as source distribution from `pypi.python.org
<https://pypi.python.org/pypi/xrt>`_ and from `GitHub
<https://github.com/kklmn/xrt>`_. The distribution archive also includes tests,
and examples. The complete documentation is available at
`Read the Docs <http://xrt.readthedocs.io>`_ and as zip file from
`GitHub <https://github.com/kklmn/xrt>`_ .

"""

setup(
    name='xrt',
    version='1.3.1',
    description='Ray tracing and wave propagation in x-ray regime, primarily '
                'meant for modeling synchrotron sources, beamlines and '
                'beamline elements. Includes a GUI for creating a beamline '
                'and viewing it in 3D.',
    long_description=long_description,
    author='Konstantin Klementiev, Roman Chernikov',
    author_email='konstantin.klementiev@gmail.com, rchernikov@gmail.com',
    url='http://xrt.readthedocs.io',
    platforms='OS Independent',
    license='MIT License',
    keywords='',
    # python_requires=,
    zip_safe=True,
    packages=['xrt', 'xrt.backends', 'xrt.backends.raycing', 'xrt.gui',
              'xrt.gui.commons', 'xrt.gui.xrtGlow', 'xrt.gui.xrtQook'],
    package_data={
        'xrt.backends.raycing': ['data/*.npz', 'data/*.dat', '*.cl'],
        'xrt': ['*.cl, *.ico'],
        'xrt.gui': ['*.pyw'],
        'xrt.gui.commons': ['_images/*.*',
                            '_themes/qook/*.*', '_themes/qook/static/*.*'],
        'xrt.gui.xrtQook': ['_icons/*.*'],
        'xrt.gui.xrtGlow': ['_icons/*.*']},
    scripts=['xrt/gui/xrtQookStart.pyw', 'xrt/gui/xrtQookStart.py'],
    install_requires=['numpy>=1.8.0', 'scipy>=0.17.0', 'matplotlib>=2.0.0',
                      'sphinx>=1.6.2'],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Science/Research',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Scientific/Engineering :: Physics',
                 'Topic :: Scientific/Engineering :: Visualization'])
