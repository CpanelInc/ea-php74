#!/bin/bash

source debian/vars.sh

set -x 

rm -rf $DEB_INSTALL_ROOT
mkdir -p $DEB_INSTALL_ROOT/opt/cpanel/ea-php74

install -d $DEB_INSTALL_ROOT/usr/local/bin
ln -sf /opt/cpanel/ea-php74/root/usr/bin/php $DEB_INSTALL_ROOT/usr/local/bin/ea-php74
install -d $DEB_INSTALL_ROOT/usr/bin
ln -sf /opt/cpanel/ea-php74/root/usr/bin/php-cgi $DEB_INSTALL_ROOT/usr/bin/ea-php74

pushd build
make INSTALL_ROOT=$DEB_INSTALL_ROOT install-sapi install install-headers install-fpm
popd

echo "AFTER MAKE"
echo "DEB_INSTALL_ROOT"
ls -R $DEB_INSTALL_ROOT


echo "SYSCONFDIR :$_sysconfdir:"
echo "DATADIR :$_datadir:"
echo "LOCALSTATEDIR :$_localstatedir:"

echo "SAPI LITESPEED"
ls -R build/sapi
find . -name "*.ini"

# Install the default configuration file and icons
install -m 755 -d $DEB_INSTALL_ROOT$_sysconfdir/
install -m 644 $SOURCE2 $DEB_INSTALL_ROOT$_sysconfdir/php.ini
# For third-party packaging:
install -m 755 -d $DEB_INSTALL_ROOT$_datadir/php
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
echo "PHP_FPM"
ls -d $DEB_INSTALL_ROOT/opt/cpanel/ea-php74/root/usr/var
ls -R $DEB_INSTALL_ROOT/opt/cpanel/ea-php74/root/usr/var
install -d $DEB_INSTALL_ROOT/opt/cpanel/$ns_name-$pkg/root/usr/var/run/php-fpm
ln -sf /opt/cpanel/$ns_name-$pkg/root/usr/var/log/php-fpm $DEB_INSTALL_ROOT$_localstatedir/log/php-fpm
ln -sf /opt/cpanel/$ns_name-$pkg/root/usr/var/run/php-fpm $DEB_INSTALL_ROOT$_localstatedir/run/php-fpm
# Config
install -m 755 -d $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d
install -m 644 $SOURCE4 $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.conf
sed -e 's:/run:$_localstatedir/run:' \
    -e 's:/var/log:$_localstatedir/log:' \
    -e 's:/etc:$_sysconfdir:' \
    -i $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.conf
install -m 644 $SOURCE5 $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d/www.conf
sed -e 's:/var/lib:$_localstatedir/lib:' \
    -e 's:/var/log:$_localstatedir/log:' \
    -i $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d/www.conf
mv $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d/www.conf $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.d/www.conf.example
mv $DEB_INSTALL_ROOT$_sysconfdir/php-fpm.conf.default .
# tmpfiles.d
# install -m 755 -d $DEB_INSTALL_ROOT$_prefix/lib/tmpfiles.d
# install -m 644 php-fpm.tmpfiles $DEB_INSTALL_ROOT$_prefix/lib/tmpfiles.d/php-fpm.conf
# install systemd unit files and scripts for handling server startup
install -m 755 -d $DEB_INSTALL_ROOT$_unitdir
install -m 644 $SOURCE6 $DEB_INSTALL_ROOT$_unitdir/$scl_prefixphp-fpm.service
sed -e 's:/run:$_localstatedir/run:' \
    -e 's:/etc:$_sysconfdir:' \
    -e 's:/usr/sbin:$_sbindir:' \
    -i $DEB_INSTALL_ROOT$_unitdir/$scl_prefixphp-fpm.service
# LogRotate
install -m 755 -d $DEB_INSTALL_ROOT$_root_sysconfdir/logrotate.d
install -m 644 $SOURCE7 $DEB_INSTALL_ROOT$_root_sysconfdir/logrotate.d/$scl_prefixphp-fpm
sed -e 's:/run:$_localstatedir/run:' \
    -e 's:/var/log:$_localstatedir/log:' \
    -i $DEB_INSTALL_ROOT$_root_sysconfdir/logrotate.d/$scl_prefixphp-fpm
# Environment file
install -m 755 -d $DEB_INSTALL_ROOT$_sysconfdir/sysconfig
install -m 644 $SOURCE8 $DEB_INSTALL_ROOT$_sysconfdir/sysconfig/php-fpm
mkdir -p ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74$_sysconfdir/php.d

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
      cp -p $buildroot/$ini ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74$_sysconfdir/php.d/$ini
    else
      echo "INI :$ini:"
      ls -d ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74$_sysconfdir/php.d
      cat > ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74$_sysconfdir/php.d/$ini <<EOF
; Enable ${mod} extension module
extension=${mod}.so
EOF
      ls -d ${DEB_INSTALL_ROOT}/opt/cpanel/ea-php74$_sysconfdir/php.d/*
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
install -m 644 $SOURCE51 $DEB_INSTALL_ROOT/opt/cpanel/ea-php74$_sysconfdir/php.d/opcache-default.blacklist
# Install the macros file:
install -d $DEB_INSTALL_ROOT/opt/cpanel/ea-php74$_root_sysconfdir/rpm
install -m 644 -c macros.php \
           $DEB_INSTALL_ROOT/opt/cpanel/ea-php74$_root_sysconfdir/rpm/macros.$name
# Remove unpackaged files
rm -rf $DEB_INSTALL_ROOT$_libdir/php/modules/*.a \
       $DEB_INSTALL_ROOT$_bindir/{phptar} \
       $DEB_INSTALL_ROOT$_datadir/pear \
       $DEB_INSTALL_ROOT$_libdir/libphp7.la
# Remove irrelevant docs
rm -f README.{Zeus,QNX,CVS-RULES}

echo "AFTER INSTALL"
ls -R $DEB_INSTALL_ROOT

