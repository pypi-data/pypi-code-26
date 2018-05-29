from setuptools import find_packages
from setuptools import setup, Extension
from distutils import ccompiler
import os
import re
import sys

from distutils.command.build_ext import build_ext

def getSundialsSources():
    srcs = [
        os.path.join('src', 'cvodes', 'cvodes_band.c'),
        os.path.join('src', 'cvodes', 'cvodes_bandpre.c'),
        os.path.join('src', 'cvodes', 'cvodes_bbdpre.c'),
        os.path.join('src', 'cvodes', 'cvodes_direct.c'),
        os.path.join('src', 'cvodes', 'cvodes_dense.c'),
        os.path.join('src', 'cvodes', 'cvodes_sparse.c'),
        os.path.join('src', 'cvodes', 'cvodes_diag.c'),
        os.path.join('src', 'cvodes', 'cvodea.c'),
        os.path.join('src', 'cvodes', 'cvodes.c'),
        os.path.join('src', 'cvodes', 'cvodes_io.c'),
        os.path.join('src', 'cvodes', 'cvodea_io.c'),
        os.path.join('src', 'cvodes', 'cvodes_spils.c'),
        os.path.join('src', 'cvodes', 'cvodes_spbcgs.c'),
        os.path.join('src', 'cvodes', 'cvodes_spgmr.c'),
        os.path.join('src', 'cvodes', 'cvodes_sptfqmr.c'),
        os.path.join('src', 'cvodes', 'cvodes_klu.c'),
        os.path.join('src', 'idas', 'idas.c'),
        os.path.join('src', 'idas', 'idas_sptfqmr.c'),
        os.path.join('src', 'idas', 'idas_spils.c'),
        os.path.join('src', 'idas', 'idas_spgmr.c'),
        os.path.join('src', 'idas', 'idas_spbcgs.c'),
        os.path.join('src', 'idas', 'idas_sparse.c'),
        os.path.join('src', 'idas', 'idas_klu.c'),
        os.path.join('src', 'idas', 'idas_io.c'),
        os.path.join('src', 'idas', 'idas_ic.c'),
        os.path.join('src', 'idas', 'idas_direct.c'),
        os.path.join('src', 'idas', 'idas_dense.c'),
        os.path.join('src', 'idas', 'idas_bbdpre.c'),
        os.path.join('src', 'idas', 'idas_band.c'),
        os.path.join('src', 'idas', 'idaa.c'),
        os.path.join('src', 'idas', 'idaa_io.c'),
        os.path.join('src', 'sundials', 'sundials_band.c'),
        os.path.join('src', 'sundials', 'sundials_dense.c'),
        os.path.join('src', 'sundials', 'sundials_sparse.c'),
        os.path.join('src', 'sundials', 'sundials_iterative.c'),
        os.path.join('src', 'sundials', 'sundials_nvector.c'),
        os.path.join('src', 'sundials', 'sundials_direct.c'),
        os.path.join('src', 'sundials', 'sundials_spbcgs.c'),
        os.path.join('src', 'sundials', 'sundials_spgmr.c'),
        os.path.join('src', 'sundials', 'sundials_sptfqmr.c'),
        os.path.join('src', 'sundials', 'sundials_math.c'),
        os.path.join('src', 'nvec_ser', 'nvector_serial.c'),
    ]
    return [os.path.join('amici', 'ThirdParty', 'sundials', src) for src in srcs]


def getSuiteSparseSources():
    srcs = [
        os.path.join('KLU', 'Source', 'klu_analyze_given.c'),
        os.path.join('KLU', 'Source', 'klu_analyze.c'),
        os.path.join('KLU', 'Source', 'klu_defaults.c'),
        os.path.join('KLU', 'Source', 'klu_diagnostics.c'),
        os.path.join('KLU', 'Source', 'klu_dump.c'),
        os.path.join('KLU', 'Source', 'klu_extract.c'),
        os.path.join('KLU', 'Source', 'klu_factor.c'),
        os.path.join('KLU', 'Source', 'klu_free_numeric.c'),
        os.path.join('KLU', 'Source', 'klu_free_symbolic.c'),
        os.path.join('KLU', 'Source', 'klu_kernel.c'),
        os.path.join('KLU', 'Source', 'klu_memory.c'),
        os.path.join('KLU', 'Source', 'klu_refactor.c'),
        os.path.join('KLU', 'Source', 'klu_scale.c'),
        os.path.join('KLU', 'Source', 'klu_sort.c'),
        os.path.join('KLU', 'Source', 'klu_solve.c'),
        os.path.join('KLU', 'Source', 'klu_tsolve.c'),
        os.path.join('KLU', 'Source', 'klu.c'),
        os.path.join('AMD', 'Source', 'amd_1.c'),
        os.path.join('AMD', 'Source', 'amd_2.c'),
        os.path.join('AMD', 'Source', 'amd_aat.c'),
        os.path.join('AMD', 'Source', 'amd_control.c'),
        os.path.join('AMD', 'Source', 'amd_defaults.c'),
        os.path.join('AMD', 'Source', 'amd_dump.c'),
        os.path.join('AMD', 'Source', 'amd_global.c'),
        os.path.join('AMD', 'Source', 'amd_info.c'),
        os.path.join('AMD', 'Source', 'amd_order.c'),
        os.path.join('AMD', 'Source', 'amd_post_tree.c'),
        os.path.join('AMD', 'Source', 'amd_postorder.c'),
        os.path.join('AMD', 'Source', 'amd_preprocess.c'),
        os.path.join('AMD', 'Source', 'amd_valid.c'),
        os.path.join('COLAMD', 'Source', 'colamd.c'),
        os.path.join('BTF', 'Source', 'btf_maxtrans.c'),
        os.path.join('BTF', 'Source', 'btf_order.c'),
        os.path.join('BTF', 'Source', 'btf_strongcomp.c'),
        os.path.join('SuiteSparse_config', 'SuiteSparse_config.c'),
    ]
    return [os.path.join('amici', 'ThirdParty', 'SuiteSparse', src) for src in srcs]


def getAmiciBaseSources():
    """Get list of source files for the amici base library"""
    import glob
    import re
    amiciBaseSources = glob.glob('amici/src/*.cpp')
    amiciBaseSources = [src for src in amiciBaseSources if not re.search(
        r'(matlab)|(\.template\.)', src)]
    return amiciBaseSources


# Find HDF5 include dir
import pkgconfig
h5pkgcfg = pkgconfig.parse("hdf5")

cxx_flags = ['-std=c++0x']
linker_flags = ['-lcblas']
# manually add linker flags. The ones passed to Extension (libraries) will end up in front of the clibs and not after, where they are required
linker_flags.extend(['-l%s' % l for l in ['hdf5_hl_cpp', 'hdf5_hl', 'hdf5_cpp', 'hdf5']])
if 'ENABLE_GCOV_COVERAGE' in os.environ and os.environ['ENABLE_GCOV_COVERAGE'] == 'TRUE':
    cxx_flags.extend(['-g', '-O0',  '--coverage'])
    linker_flags.append('--coverage')


# Build shared object
amici_module = Extension('amici/_amici',
                         sources=[
                             'amici/amici_wrap.cxx',
                         ],
                         include_dirs=['amici/include',
                                       'amici/ThirdParty/SuiteSparse/KLU/Include/',
                                       'amici/ThirdParty/SuiteSparse/AMD/Include/',
                                       'amici/ThirdParty/SuiteSparse/COLAMD/Include/',
                                       'amici/ThirdParty/SuiteSparse/BTF/Include/',
                                       'amici/ThirdParty/SuiteSparse/SuiteSparse_config/Include/',
                                       'amici/ThirdParty/SuiteSparse/include',
                                       'amici/ThirdParty/sundials/include',
                                       'amici/ThirdParty/sundials/src',
                                       *h5pkgcfg['include_dirs']],  # NOTE: requires that pkgconfig knows about hdf5
                         libraries=[
                             'hdf5_hl_cpp', 'hdf5_hl', 'hdf5_cpp', 'hdf5'
                         ],
                         library_dirs=[
                             *h5pkgcfg['library_dirs'],
                             'amici/libs/',
                         ],
                         extra_compile_args=cxx_flags,
                         extra_link_args=linker_flags
                         )

libsundials = ('sundials',
               {
                   'sources': getSundialsSources(),
                   'include_dirs': ['amici/include',
                                    'amici/ThirdParty/SuiteSparse/KLU/Include/',
                                    'amici/ThirdParty/SuiteSparse/AMD/Include/',
                                    'amici/ThirdParty/SuiteSparse/COLAMD/Include/',
                                    'amici/ThirdParty/SuiteSparse/BTF/Include/',
                                    'amici/ThirdParty/SuiteSparse/SuiteSparse_config/Include/',
                                    'amici/ThirdParty/SuiteSparse/include',
                                    'amici/ThirdParty/sundials/include',
                                    'amici/ThirdParty/sundials/src']
               }
               )
libsuitesparse = ('suitesparse', {
    'sources': getSuiteSparseSources(),
    'include_dirs': ['amici/include',
                     'amici/ThirdParty/SuiteSparse/KLU/Include/',
                     'amici/ThirdParty/SuiteSparse/AMD/Include/',
                     'amici/ThirdParty/SuiteSparse/COLAMD/Include/',
                     'amici/ThirdParty/SuiteSparse/BTF/Include/',
                     'amici/ThirdParty/SuiteSparse/SuiteSparse_config/Include/',
                     'amici/ThirdParty/SuiteSparse/include',
                     'amici/ThirdParty/sundials/include',
                     'amici/ThirdParty/sundials/src']

})
libamici = ('amici',
            {
                'sources': getAmiciBaseSources(),
                'include_dirs': ['amici/include',
                                 'amici/ThirdParty/SuiteSparse/KLU/Include/',
                                 'amici/ThirdParty/SuiteSparse/AMD/Include/',
                                 'amici/ThirdParty/SuiteSparse/COLAMD/Include/',
                                 'amici/ThirdParty/SuiteSparse/BTF/Include/',
                                 'amici/ThirdParty/SuiteSparse/SuiteSparse_config/Include/',
                                 'amici/ThirdParty/SuiteSparse/include',
                                 'amici/ThirdParty/sundials/include',
                                 'amici/ThirdParty/sundials/src',
                                 *h5pkgcfg['include_dirs']]

            }
            )
class my_build_ext(build_ext):
    def run(self):
        """Copy the generated clibs to the extensions folder to be included in the wheel"""
        # honor the --dry-run flag
        if not self.dry_run:
            if self.distribution.has_c_libraries():
                build_clib = self.get_finalized_command('build_clib')
                libraries = build_clib.get_library_names() or []
                library_dirs = build_clib.build_clib
            
            target_dir = os.path.join(self.build_lib, 'amici/libs')
            self.mkpath(target_dir)
            
            import glob
            from shutil import copyfile
            
            for lib in libraries:
                libfilenames = glob.glob('%s/*%s.*' % (build_clib.build_clib, lib))
                assert(len(libfilenames) == 1)
                copyfile(libfilenames[0], 
                         os.path.join(target_dir, os.path.basename(libfilenames[0])))
            
        build_ext.run(self)
        
with open("README.md", "r") as fh:
    long_description = fh.read()
    
def getVersionNumber():
    return '0.6.a1'
    
def main():
    # Install
    setup(
        name='amici',
        cmdclass={'build_ext': my_build_ext},
        version=getVersionNumber(),
        description='Advanced multi-language Interface to CVODES and IDAS',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/ICB-DCM/AMICI',
        author='Fabian Froehlich, Jan Hasenauer, Daniel Weindl and Paul Stapor',
        author_email='fabian.froehlich@helmholtz-muenchen.de',
        license='BSD',
        libraries=[libamici, libsundials, libsuitesparse],
        ext_modules=[amici_module, ],
        py_modules=['amici/amici'],
        packages=find_packages(),
        package_dir={'amici': 'amici'},
        install_requires=['symengine', 'python-libsbml', 'h5py'],
        python_requires='>=3',
        package_data={
            'amici': ['amici/include/amici/*',
                      'src/*template*',
                      'swig/*',
                      'libs/*',
                      'amici.py',
                      'setup.py.template',
                      #'ThirdParty/sundials/include/*/*',
                      #'ThirdParty/SuiteSparse/include/*'
                      ],
        },
        zip_safe=False,
        include_package_data=True,
        exclude_package_data={'': ['README.txt'],
                              # 'amici': ['src/*']
                              },
        test_suite="tests",
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX :: Linux',
            'Operating System :: MacOS :: MacOS X',
            'Programming Language :: Python',
            'Programming Language :: C++',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
        ],
    )

if __name__ == '__main__':
    main()
    