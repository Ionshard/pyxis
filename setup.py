from distutils.core import setup

setup(name='pyxis',
      version='0.2.1',
      description='Command Line XM and SIRIUS Radio Player',
      author='Corey Ling',
      author_email='kasuko@ionshard.com',
      url='http://www.ionshard.com/pyxis',
      packages=['pyxis'],
      package_data={'pyxis' : ['data/*']},
      scripts=['bin/pyxis'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.5',
          'Topic :: Multimedia :: Sound/Audio :: Players'
          ]
     )

