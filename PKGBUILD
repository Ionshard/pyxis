# Contributor: Corey Ling <kasuko@gmail.com>

pkgname=pyxis
pkgver=0.1.1
pkgrel=0
pkgdesc="SIRIUS/XM Internet Radio Player for Command Line"
url="http://kasuko.github.com/pyxis"
arch=(i686 x86_64)
license=('GPL')
depends=('beautiful-soup' 'mplayer' 'python' 'setuptools')
makedepends=()
optdepends=('python-notify: for OSD notifications')
conflicts=() 
replaces=()
backup=()
options=(!emptydirs)
install=
source=(http://github.com/Kasuko/pyxis/tarball/v$pkgver)

build() {
	cd $srcdir/Kasuko-pyxis*
	python setup.py install --root=$pkgdir
}
md5sums=('3f84a475f2a55e48f21f58769ba42733')

