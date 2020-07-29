import numpy as np
from setuptools import Extension, setup, find_packages
# from Cython.Build import cythonize, build_ext
from Cython.Distutils import build_ext


ext_modules = [
    Extension(
        "vanetgraph.utils.constructor",
        ["vanetgraph/utils/constructor.pyx"],
        include_dirs=["vanetgraph/constructor/", np.get_include(), "."],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
        language="c++"
    )
]

print(find_packages())
setup(
    name="vanetgraph",
    author='Caio Dadauto',
    author_email='caiodadauto@gmail.com',
    packages=find_packages(),
    ext_modules = ext_modules,
    cmdclass = {'build_ext': build_ext},
    zip_safe=False
)


