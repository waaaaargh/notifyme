#!/bin/sh

. $(pwd)/packaging/make_source_tarball.sh

# python library package
tar xzf $destdir/notifyme-$version.tar.gz -C $destdir
cp -r $(pwd)/packaging/debian/python3-notifyme/debian $destdir/notifyme-$version/
cd $destdir/notifyme-$version
debuild -us -uc
cd $sourcedir

# collector package
rm -rf $destdir/notifyme-$version
tar xzf $destdir/notifyme-$version.tar.gz -C $destdir
cp -r $(pwd)/packaging/debian/notifyme-collector/debian $destdir/notifyme-$version/
cd $destdir/notifyme-$version
debuild -us -uc
cd $sourcedir

# emitter package
rm -rf $destdir/notifyme-$version
tar xzf $destdir/notifyme-$version.tar.gz -C $destdir
cp -r $(pwd)/packaging/debian/notifyme-emitter/debian $destdir/notifyme-$version/
cd $destdir/notifyme-$version
debuild -us -uc
cd $sourcedir

# subscriber package
rm -rf $destdir/notifyme-$version
tar xzf $destdir/notifyme-$version.tar.gz -C $destdir
cp -r $(pwd)/packaging/debian/notifyme-subscriber/debian $destdir/notifyme-$version/
cd $destdir/notifyme-$version
debuild -us -uc
cd $sourcedir
