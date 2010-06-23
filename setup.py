from distutils.core import setup

setup(name='Pyxis',
      version='0.1',
      description='Command Line XM and SIRIUS Radio Player',
      author='Corey Ling',
      author_email='kasuko@gmail.com',
      url='http://kasuko.github.com/pyxis',
      packages=['pyxis'],
      package_data={'pyxis' : ['data/*']},
      scripts=['bin/pyxis'],
     )

