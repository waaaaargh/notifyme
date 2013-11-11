version=0.1~dev1
sourcedir=$(pwd)
destdir=/tmp/notifyme-packaging

# clean destination directory
if [ -d $destdir ]; then
    rm -rf $destdir
fi
mkdir -p $destdir/notifyme-$version

cp -r bin $destdir/notifyme-$version
cp -r notifyme $destdir/notifyme-$version
rm -rf $destdir/notifyme-$version/notifyme/__pycache__
cp -r setup.py $destdir/notifyme-$version
cp -r MANIFEST.in $destdir/notifyme-$version
cp -r COPYING.txt $destdir/notifyme-$version
cp -r collector.conf.yaml $destdir/notifyme-$version
cp -r subscriber.conf.yaml $destdir/notifyme-$version
cp -r doc $destdir/notifyme-$version

$(cd $destdir; tar -czf notifyme-$version.tar.gz notifyme-$version;)
rm -rf $destdir/notifyme-$version
