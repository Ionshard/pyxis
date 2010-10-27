# Contributor: Corey Ling <kasuko@gmail.com>

pkgname=pyxis
pkgver=0.1.1
pkgrel=1
pkgdesc="SIRIUS/XM Internet Radio Player for Command Line"
url="http://kasuko.github.com/pyxis"
arch=(i686 x86_64)
license=('GPL')
depends=('mplayer' 'python' 'setuptools')
makedepends=()
optdepends=('python-notify: for OSD notifications')
conflicts=() 
replaces=()
backup=()
options=(!emptydirs)
install=
source=(http://github.com/Kasuko/pyxis/tarball/python3)

build() {
	cd $srcdir/Kasuko-pyxis*
	python setup.py install --root=$pkgdir
}

md5sums=('902bc28d1c2831f3ace23c42dbb818df')
