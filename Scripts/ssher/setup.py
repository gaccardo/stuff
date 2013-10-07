#!/usr/bin/env python

import os
import sys
from distutils.core import setup
from distutils.command.install import install as _install

def _post_install(dir):
    from subprocess import call
    print os.path.join(dir, 'ssher')
    call([sys.executable, 'create_bin.py', os.path.join(dir, 'ssher')],
         cwd=os.path.join(dir, 'ssher'))


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,),
                     msg="Running post install task")


setup(
    name='SSHer',
    version='1.0',
    description='Multi ssh connection launcher',
    author='Guido Accardo',
    author_email='gaccardo@gmail.com',
    cmdclass={'install': install},
    install_requires=['Pybles', 'subproccess'],
    packages=['ssher'])
