#!/usr/bin/env python

from distutils.core import setup

setup(name='Sipie',
      version='0.1179843539',
      description='Player for Sirius Online Streaming',
      author='Eli Criffield',
      author_email='python@zendo.net',
      url='http://eli.criffield.net/sipie/',
      scripts=[ 'sipie.py' ],
      packages=['Sipie'],
      data_files=[
                  ( '/usr/share/sipie/', ['sipie.png'] ),
                  ( '/usr/share/sipie/', ['Sipie/glade/gtkSipie.glade'] )
                 ]
     )
