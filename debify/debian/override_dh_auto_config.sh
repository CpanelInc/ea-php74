#!/bin/bash

source debian/vars.sh

set -x 

# Prevent %%doc confusion over LICENSE files
cp Zend/LICENSE Zend/ZEND_LICENSE
cp TSRM/LICENSE TSRM_LICENSE
cp sapi/fpm/LICENSE fpm_LICENSE
cp ext/mbstring/libmbfl/LICENSE libmbfl_LICENSE
cp ext/fileinfo/libmagic/LICENSE libmagic_LICENSE
cp ext/bcmath/libbcmath/LICENSE libbcmath_LICENSE

# Remove the bundled version of litespeed
# and replace it with the latest version
pushd sapi
tar -xvf $SOURCE1 --exclude=Makefile.frag --exclude=config.m4
popd

# ----- Manage known as failed test -------
# affected by systzdata patch
rm -f ext/date/tests/timezone_location_get.phpt
rm -f ext/date/tests/timezone_version_get.phpt
rm -f ext/date/tests/timezone_version_get_basic1.phpt
# fails sometime
rm -f ext/sockets/tests/mcast_ipv?_recv.phpt
# Should be skipped but fails sometime
rm -f ext/standard/tests/file/file_get_contents_error001.phpt
# cause stack exhausion
rm Zend/tests/bug54268.phpt
rm Zend/tests/bug68412.phpt

# Safety check for API version change.
pver=$(sed -n '/#define PHP_VERSION /{s/.* "//;s/".*$//;p}' main/php_version.h)
if test "x$pver" != "x$version"; then
   : Error: Upstream PHP version is now $pver, expecting $version.
   : Update the version macros and rebuild.
   exit 1
fi

vapi=`sed -n '/#define PHP_API_VERSION/{s/.* //;p}' main/php.h`
if test "x$vapi" != "x$apiver"; then
   : Error: Upstream API version is now $vapi, expecting $apiver.
   : Update the apiver macro and rebuild.
   exit 1
fi

vzend=`sed -n '/#define ZEND_MODULE_API_NO/{s/^[^0-9]*//;p;}' Zend/zend_modules.h`
if test "x$vzend" != "x$zendver"; then
   : Error: Upstream Zend ABI version is now $vzend, expecting $zendver.
   : Update the zendver macro and rebuild.
   exit 1
fi

# Safety check for PDO ABI version change
vpdo=`awk '/^#define PDO_DRIVER_API/ { print $3 } ' ext/pdo/php_pdo_driver.h`
if test "x$vpdo" != "x$pdover"; then
   : Error: Upstream PDO ABI version is now $vpdo, expecting $pdover.
   : Update the pdover macro and rebuild.
   exit 1
fi

# https://bugs.php.net/63362 - Not needed but installed headers.
# Drop some Windows specific headers to avoid installation,
# before build to ensure they are really not needed.
rm -f TSRM/tsrm_win32.h \
      TSRM/tsrm_config.w32.h \
      Zend/zend_config.w32.h \
      ext/mysqlnd/config-win.h \
      ext/standard/winver.h \
      main/win32_internal_function_disabled.h \
      main/win95nt.h

# Fix some bogus permissions
find . -name \*.[ch] -exec chmod 644 {} \;
chmod 644 README.*

# Create the macros.php files
sed -e "s/@PHP_APIVER@/$apiver$isasuffix/" \
    -e "s/@PHP_ZENDVER@/$zendver$isasuffix/" \
    -e "s/@PHP_PDOVER@/$pdover$isasuffix/" \
    -e "s/@PHP_VERSION@/$version/" \
    -e "s:@LIBDIR@:$_libdir:" \
    -e "s:@ETCDIR@:$_sysconfdir:" \
    -e "s:@INCDIR@:$_includedir:" \
    -e "s:@BINDIR@:$_bindir:" \
    -e "s/@SCL@/${ns_name}_${pkg}_/" \
    $SOURCE3 | tee macros.php
# php-fpm configuration files for tmpfiles.d
# TODO echo "d /run/php-fpm 755 root root" >php-fpm.tmpfiles

# Some extensions have their own configuration file
cp $SOURCE50 10-opcache.ini
sed -e '/opcache.huge_code_pages/s/0/1/' -i 10-opcache.ini
cp $SOURCE51 .
sed -e 's:%{_root_sysconfdir}:%{_sysconfdir}:' -i 10-opcache.ini

export EXTENSION_DIR=/opt/cpanel/ea-php74/root/usr/lib64/php/modules
export PEAR_INSTALLDIR=${_datadir}/pear
export PKG_CONFIG_PATH=/usr/lib/pkgconfig:/usr/share/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig
export CFLAGS="-mshstk $CFLAGS"
export LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lxml2 -lsystemd $LDFLAGS"

KERBEROS_CFLAGS="-I/usr/include"
KERBEROS_LIBS="-L/usr/lib/x86_64-linux-gnu"
JPEG_CFLAGS="-I/usr/include"
JPEG_LIBS="-L/usr/lib/x86_64-linux-gnu -ljpeg"
SASL_CFLAGS="-I/usr/include"
SASL_LIBS="-L/usr/lib/x86_64-linux-gnu"
XSL_CFLAGS="-I/usr/include/libxml2"
XSL_LIBS="-L/usr/lib/x86_64-linux-gnu -lxml2"
LIBZIP_CFLAGS="-I/usr/include"
LIBZIP_LIBS="-L/usr/lib/x86_64-linux-gnu -lzip"

cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >>aclocal.m4

# Force use of system libtool:
libtoolize --force --copy
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >build/libtool.m4

# pulled from apr-util
mkdir -p config
cp $ea_apr_config config/apr-1-config
cp $ea_apr_config config/apr-config
cp /usr/share/pkgconfig/ea-apr16-1.pc config/apr-1.pc
cp /usr/share/pkgconfig/ea-apr16-util-1.pc config/apr-util-1.pc
cp /usr/share/pkgconfig/ea-apr16-1.pc config
cp /usr/share/pkgconfig/ea-apr16-util-1.pc config

export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:`pwd`/config"
echo "PKG_CONFIG_PATH :$PKG_CONFIG_PATH:"

touch configure.in
./buildconf --force

pushd build

ln -s ../configure

./configure \
    --with-apxs2=${_httpd_apxs} \
    --build=x86_64-linux-gnu \
    --host=x86_64-linux-gnu \
    --target=x86_64-pc-linux-gnu \
    --program-prefix= \
    --disable-dependency-tracking \
    --prefix=/opt/cpanel/ea-php74/root/usr \
    --exec-prefix=/opt/cpanel/ea-php74/root/usr \
    --bindir=/opt/cpanel/ea-php74/root/usr/bin \
    --sbindir=/opt/cpanel/ea-php74/root/usr/sbin \
    --sysconfdir=/opt/cpanel/ea-php74/root/etc \
    --datadir=/opt/cpanel/ea-php74/root/usr/share \
    --includedir=/opt/cpanel/ea-php74/root/usr/include \
    --libdir=/opt/cpanel/ea-php74/root/usr/lib64 \
    --libexecdir=/opt/cpanel/ea-php74/root/usr/libexec \
    --localstatedir=/opt/cpanel/ea-php74/root/var \
    --sharedstatedir=/opt/cpanel/ea-php74/root/var/lib \
    --mandir=/opt/cpanel/ea-php74/root/usr/share/man \
    --infodir=/opt/cpanel/ea-php74/root/usr/share/info \
    --cache-file=../config.cache \
    --with-libdir=lib \
    --with-config-file-path=/opt/cpanel/ea-php74/root/etc \
    --with-config-file-scan-dir=/opt/cpanel/ea-php74/root/etc/php.d \
    --disable-debug \
    --with-password-argon2=/opt/cpanel/libargon2 \
    --with-pic \
    --without-pear \
    --with-bz2=shared \
    --with-freetype \ \
    --with-xpm \
    --with-sodium=shared \
    --without-gdbm \
    --with-gettext=shared \
    --with-iconv=shared \
    --with-jpeg \
    --with-openssl \
    --with-pcre-regex=/usr \
    --with-zlib \ \
    --with-layout=GNU \
    --enable-exif=shared \
    --enable-ftp=shared \
    --enable-sockets=shared \
    --with-kerberos \
    --enable-shmop=shared \
    --with-libxml \
    --with-system-tzdata \
    --with-mhash \
    --enable-fpm \
    --with-fpm-systemd \
    --libdir=/opt/cpanel/ea-php74/root/usr/lib64/php \
    --with-mysqli=shared \
    --enable-pdo=shared \
    --with-pdo-mysql=shared,mysqlnd \
    --with-pdo-pgsql=shared \
    --with-pdo-sqlite=shared \
    --with-sqlite3=shared \
    --with-pdo-odbc=shared,unixodbc,/usr \
    --enable-pcntl \
    --enable-gd=shared \
    --enable-dba=shared \
    --with-unixODBC=shared \
    --enable-opcache=shared \
    --enable-xmlreader=shared \
    --enable-xmlwriter=shared \
    --enable-phar=shared \
    --enable-fileinfo=shared \
    --enable-json=shared \
    --with-pspell=shared \
    --with-curl=shared \
    --enable-posix=shared \
    --enable-xml=shared \
    --enable-simplexml=shared \
    --enable-ctype=shared \
    --enable-sysvmsg=shared \
    --enable-sysvshm=shared \
    --enable-sysvsem=shared \
    --with-gmp=shared \
    --enable-calendar=shared \
    --with-imap=shared,/usr/lib \
    --with-imap-ssl \
    --enable-mbstring=shared \
    --enable-bcmath=shared \
    --with-tcadb=/usr \
    --enable-tokenizer=shared \
    --with-xmlrpc=shared \
    --with-ldap=shared \
    --with-ldap-sasl \
    --enable-mysqlnd=shared \
    --with-mysql-sock=/var/lib/mysql/mysql.sock \
    --enable-dom=shared \
    --with-pgsql=shared \
    --with-snmp=shared \
    --with-xsl=shared \
    --with-zip=shared \
    --enable-soap=shared \
    --enable-intl=shared \
    --with-tidy=shared \
    --with-enchant=shared \
    --enable-litespeed \
    --enable-phpdbg \
    --with-webp
if test $? != 0; then
  : configure failed
  exit 1
fi

make

