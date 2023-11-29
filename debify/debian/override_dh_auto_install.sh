#!/bin/bash

source debian/vars.sh

set -x 

export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:`pwd`/config"
echo "PKG_CONFIG_PATH :$PKG_CONFIG_PATH:"

rm -rf $DEB_INSTALL_ROOT
mkdir -p $DEB_INSTALL_ROOT/opt/cpanel/ea-php74

install -d $DEB_INSTALL_ROOT/usr/local/bin
ln -sf /opt/cpanel/ea-php74/root/usr/bin/php $DEB_INSTALL_ROOT/usr/local/bin/ea-php74
install -d $DEB_INSTALL_ROOT/usr/bin
ln -sf /opt/cpanel/ea-php74/root/usr/bin/php-cgi $DEB_INSTALL_ROOT/usr/bin/ea-php74

pushd build
make INSTALL_ROOT=$DEB_INSTALL_ROOT install-sapi install install-headers install-fpm
popd

# Install the default configuration file and icons
install -m 755 -d $DEB_INSTALL_ROOT$_sysconfdir/
install -m 644 $SOURCE2 $DEB_INSTALL_ROOT$_sysconfdir/php.ini
# For third-party packaging:
install -m 755 -d $DEB_INSTALL_ROOT$_datadir/php

# install the DSO
install -m 755 -d $RPM_BUILD_ROOT${_httpd_moddir}
install -m 755 build/libs/libphp7.so $RPM_BUILD_ROOT${_httpd_moddir}

# Apache config fragment
install -m 755 -d $RPM_BUILD_ROO${_httpd_contentdir}/icons
install -m 644 ext/gd/tests/php.gif $RPM_BUILD_ROOT${_httpd_contentdir}/icons/${name}.gif
install -m 755 -d $RPM_BUILD_ROOT${_root_httpd_moddir}
ln -s ${_httpd_moddir}/libphp7.so $RPM_BUILD_ROOT${_root_httpd_moddir}/libphp7.so

install -m 755 -d $DEB_INSTALL_ROOT$_sysconfdir/php.d
install -m 755 -d $DEB_INSTALL_ROOT$_localstatedir/lib
install -m 755 build/sapi/litespeed/php $DEB_INSTALL_ROOT$_bindir/lsphp
# PHP-FPM stuff
# Log
# we need to do the following to compensate for the way
# EA4 on OBS was built rather than EA4-Opensuse
install -d $DEB_INSTALL_ROOT/opt/cpanel/$ns_name-$pkg/root/usr/var/log/php-fpm
mkdir -p $DEB_INSTALL_ROOT$_localstatedir/log/php-fpm
mkdir -p $DEB_INSTALL_ROOT$_localstatedir/run/php-fpm
install -d $DEB_INSTALL_ROOT/opt/cpanel/$ns_name-$pkg/root/usr/var/run/php-fpm
ln -sf /opt/cpanel/$ns_name-$pkg/root/usr/var/log/php-fpm $DEB_INSTALL_ROOT$_localstatedir/log/php-fpm
ln -sf /opt/cpanel/$ns_name-$pkg/root/usr/var/run/php-fpm $DEB_INSTALL_ROOT$_localstatedir/run/php-fpm
# Config
install -m 755 -d $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d
install -m 644 $SOURCE4 $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.conf
sed -e "s:/run:$_localstatedir/run:" \
    -e "s:/var/log:$_localstatedir/log:" \
    -e "s:/etc:$_sysconfdir:" \
    -i $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.conf
install -m 644 $SOURCE5 $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d/www.conf
sed -e "s:/var/lib:$_localstatedir/lib:" \
    -e "s:/var/log:$_localstatedir/log:" \
    -i $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d/www.conf
mv $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d/www.conf $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d/www.conf.example
mv ${DEB_INSTALL_ROOT}opt/cpanel/ea-php74/root/etc/php-fpm.conf.default .
# tmpfiles.d
# install -m 755 -d $DEB_INSTALL_ROOT$_prefix/lib/tmpfiles.d
# install -m 644 php-fpm.tmpfiles $DEB_INSTALL_ROOT$_prefix/lib/tmpfiles.d/php-fpm.conf
# install systemd unit files and scripts for handling server startup
install -m 755 -d $DEB_INSTALL_ROOT$_unitdir
install -m 644 $SOURCE6 $DEB_INSTALL_ROOT$_unitdir/${scl_prefix}php-fpm.service
sed -e "s:/run:$_localstatedir/run:" \
    -e "s:/etc:$_sysconfdir:" \
    -e "s:/usr/sbin:$_sbindir:" \
    -i $DEB_INSTALL_ROOT$_unitdir/${scl_prefix}php-fpm.service
# LogRotate
install -m 755 -d $DEB_INSTALL_ROOT/etc/logrotate.d
install -m 644 $SOURCE7 $DEB_INSTALL_ROOT/etc/logrotate.d/${scl_prefix}php-fpm
sed -e "s:/run:$_localstatedir/run:" \
    -e "s:/var/log:$_localstatedir/log:" \
    -i $DEB_INSTALL_ROOT/etc/logrotate.d/${scl_prefix}php-fpm
# Environment file
install -m 755 -d $DEB_INSTALL_ROOT$_sysconfdir/sysconfig
echo "SOURCE8 :$SOURCE8:"
install -m 644 $SOURCE8 $DEB_INSTALL_ROOT$_sysconfdir/sysconfig/php-fpm
mkdir -p ${DEB_INSTALL_ROOT}$_sysconfdir/php.d

# make the cli commands available in standard root for SCL build
# Generate files lists and stub .ini files for each subpackage
for mod in pgsql odbc ldap snmp xmlrpc imap \
    mysqlnd mysqli pdo_mysql \
    mbstring gd dom xsl soap bcmath dba xmlreader xmlwriter \
    simplexml bz2 calendar ctype exif ftp gettext gmp iconv \
    sockets tokenizer opcache \
    pdo pdo_pgsql pdo_odbc json \
    pdo_sqlite sqlite3 \
    enchant \
    phar fileinfo \
    intl \
    tidy \
    zip \
    sodium \
    pspell curl xml \
    posix shmop sysvshm sysvsem sysvmsg
do
    # for extension load order
    case $mod in
      opcache)
        # Zend extensions
        ini=10-${mod}.ini;;
      pdo_*|mysqli|xmlreader|xmlrpc)
        # Extensions with dependencies on 20-*
        ini=30-${mod}.ini;;
      *)
        # Extensions with no dependency
        ini=20-${mod}.ini;;
    esac
    # Some extensions have their own config file
    #
    # NOTE: rpmlint complains about the spec file using $_sourcedir macro.
    #       However, our usage acceptable given the transient nature of the ini files.
    #       https://fedoraproject.org/wiki/Packaging:RPM_Source_Dir?rd=PackagingDrafts/RPM_Source_Dir
    if [ -f "$buildroot/$ini" ]; then
      cp -p $buildroot/$ini ${DEB_INSTALL_ROOT}$_sysconfdir/php.d/$ini
    else
      cat > ${DEB_INSTALL_ROOT}$_sysconfdir/php.d/$ini <<EOF
; Enable ${mod} extension module
extension=${mod}.so
EOF
    fi
    cat > files.${mod} <<EOF
EOF
done
# The dom, xsl and xml* modules are all packaged in php-xml
cat files.dom files.xsl files.xml{reader,writer} \
    files.simplexml >> files.xml
# mysqlnd
cat files.mysqli \
    files.pdo_mysql \
    >> files.mysqlnd
# Split out the PDO modules
cat files.pdo_pgsql >> files.pgsql
cat files.pdo_odbc >> files.odbc
# sysv* packaged in php-process
cat files.shmop files.sysv* > files.process
cat files.pdo_sqlite >> files.pdo
cat files.sqlite3 >> files.pdo
# Package json and phar in -common.
cat files.json files.phar \
    files.ctype \
    files.tokenizer > files.common
# The default Zend OPcache blacklist file
install -m 644 $SOURCE51 $DEB_INSTALL_ROOT$_sysconfdir/php.d/opcache-default.blacklist
# Install the macros file:
install -d $DEB_INSTALL_ROOT/$_sysconfdir/rpm
install -m 644 -c macros.php \
           $DEB_INSTALL_ROOT$_sysconfdir/rpm/macros.$name
# Remove unpackaged files
rm -rf $DEB_INSTALL_ROOT$_libdir/php/modules/*.a \
       $DEB_INSTALL_ROOT$_bindir/{phptar} \
       $DEB_INSTALL_ROOT$_datadir/pear \
       $DEB_INSTALL_ROOT$_libdir/libphp7.la
# Remove irrelevant docs
rm -f README.{Zeus,QNX,CVS-RULES}

# The CONFIG/INSTALL script misses these files

mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/lib64/apache2/modules
mkdir -p ${DEB_INSTALL_ROOT}/usr/lib64/apache2/modules

mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/php.d
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/php-fpm.d
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/sysconfig/php-fpm
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/bin
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/lib64/apache2/modules
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-dbg
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-dbg
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-fpm
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-mbstring
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/licenses/ea-php74-php-bcmath
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/licenses/ea-php74-php-fpm
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/man/man1
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/man/man8
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/php
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/var/lib
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/var/log/php-fpm
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/var/run/php-fpm
mkdir -p ${DEB_INSTALL_ROOT}/usr/share/apache2/icons

cp build/libs/libphp7.so ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/lib64/apache2/modules
cp build/libs/libphp7.so ${DEB_INSTALL_ROOT}/usr/lib64/apache2/modules

cp -R ${DEB_INSTALL_ROOT}/etc/php-fpm.d/* ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/php-fpm.d
cp -f ./sapi/phpdbg/CREDITS ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-dbg
cp -f ./sapi/phpdbg/README.md ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-dbg
cp -f ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/php-fpm.d/php-fpm.d/www.conf.example ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/php-fpm.d
cp -R ${DEB_INSTALL_ROOT}/etc/sysconfig/php-fpm ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/sysconfig
cp -R ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/php-fpm.conf.default ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-fpm
cp -R ./fpm_LICENSE ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-fpm
cp ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/etc/php.d/* ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc/php.d
cp ./CODING_STANDARDS.md ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./EXTENSIONS ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./LICENSE ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./NEWS ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./README.REDIST.BINS ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./README.md ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./TSRM_LICENSE ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./Zend/ZEND_LICENSE ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./libmagic_LICENSE ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./php.ini-development ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./php.ini-production ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-common
cp ./fpm_LICENSE ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/licenses/ea-php74-php-fpm
cp ./libmbfl_LICENSE ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/doc/ea-php74-php-mbstring
cp ./libbcmath_LICENSE ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/licenses/ea-php74-php-bcmath
cp ${DEB_INSTALL_ROOT}/etc/php.ini ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/etc
cp build/libs/libphp7.so ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/lib64/apache2/modules

cp ext/gd/tests/php.gif ${DEB_INSTALL_ROOT}/usr/share/apache2/icons/ea-php74-php.gif
cp build/ext/phar/phar.phar ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/bin
cp build/sapi/cgi/php-cgi ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/bin
cp build/sapi/cli/php ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/bin
cp build/scripts/phpize ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/bin
cp build/sapi/phpdbg/phpdbg ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/bin

cp build/*/*/*.1 ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/man/man1
cp build/*/*/*.8 ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/man/man8

gzip ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/man/man1/*.1
gzip ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74/root/usr/share/man/man8/*.8

echo "FILELIST"
find . -type f -print | sort | xargs ls -ld

