# Contributor: Corey Ling <kasuko@gmail.com>

pkgname=pyxis
pkgver=0.1
pkgrel=0
pkgdesc="SIRIUS/XM Internet Radio Player for Command Line"
url="http://kasuko.github.com/pyxis"
arch=(i686 x86_64)
license=('GPL')
depends=('beautiful-soup' 'mplayer' 'python' 'setuptools')
makedepends=()
conflicts=() 
replaces=()
backup=()
options=(!emptydirs)
install=()
source=(http://github.com/Kasuko/pyxis/tarball/v$pkgver)
md5sum=('1f5674428583ad7580e3177b1f064e63')

build() {
	cd $srcdir/Kasuko-pyxis*
	python setup.py install --root=$pkgdir
}
