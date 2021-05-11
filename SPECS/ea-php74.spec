# Defining the package namespace
# NOTE: pkg variable is a hack to fix invalid macro inside of macros.php
%global ns_name ea
%global ns_dir /opt/cpanel
%global pkg php74

# Force Software Collections on
%global _scl_prefix %{ns_dir}
%global scl %{ns_name}-%{pkg}
# HACK: OBS Doesn't support macros in BuildRequires statements, so we have
#       to hard-code it here.
# https://en.opensuse.org/openSUSE:Specfile_guidelines#BuildRequires
%global scl_prefix %{scl}-
%scl_package php

# API/ABI check
%global apiver      20190902
%global zendver     20190902
%global pdover      20170320

# Adds -z now to the linker flags
%global _hardened_build 1

# version used for php embedded library soname
%global embed_version 7.4

# Ugly hack. Harcoded values to avoid relocation.
%global _httpd_mmn         %(cat %{_root_includedir}/apache2/.mmn 2>/dev/null || echo missing-ea-apache24-devel)
%global _httpd_confdir     %{_root_sysconfdir}/apache2/conf.d
%global _httpd_moddir      %{_libdir}/apache2/modules
%global _root_httpd_moddir %{_root_libdir}/apache2/modules
%if 0%{?fedora} >= 18 || 0%{?rhel} >= 6
# httpd 2.4 values
%global _httpd_apxs        %{_root_bindir}/apxs
%global _httpd_modconfdir  %{_root_sysconfdir}/apache2/conf.modules.d
%global _httpd_contentdir  /usr/share/apache2
%else
# httpd 2.2 values
%global _httpd_apxs        %{_root_sbindir}/apxs
%global _httpd_modconfdir  %{_root_sysconfdir}/apache2/conf.d
%global _httpd_contentdir  /var/www
%endif

%global with_httpd           1

%global mysql_sock %(mysql_config --socket  2>/dev/null || echo /var/lib/mysql/mysql.sock)

# Build for LiteSpeed Web Server (LSAPI)
%global with_lsws     1

# Regression tests take a long time, you can skip 'em with this
%{!?runselftest: %{expand: %%global runselftest 1}}

# Use the arch-specific mysql_config binary to avoid mismatch with the
# arch detection heuristic used by bindir/mysql_config.
%global mysql_config %{_root_libdir}/mysql/mysql_config

%global with_fpm       1
%if 0%{?scl:1}
%global with_embed     0
%else
%global with_embed     1
%endif

%if 0%{rhel} < 7
BuildRequires: devtoolset-7-toolchain
BuildRequires: devtoolset-7-libatomic-devel
BuildRequires: devtoolset-7-gcc
BuildRequires: devtoolset-7-gcc-c++
%endif

# PHP 7.0 switched to using libwebp with the bundled version of gd,
# however it's only available in base repo using CentOS 7.  CentOS 6
# provides it as apart of epel, a repo we don't readily depend on.
%if 0%{?rhel} > 6
%global with_webp 1
%else
%global with_webp 0
%endif
%global with_curl     1
%if 0%{?rhel} >= 8
%else
%global libcurl_prefix /opt/cpanel/libcurl
%endif
%if 0%{?fedora}
%global with_interbase 1
%else
%global with_interbase 0
%endif
%if 0%{?rhel} >= 6
%global with_tidy 1
%global libtidy_prefix /opt/cpanel/libtidy
%else
%global with_tidy 0
%endif
%if 0%{?fedora} >= 11 || 0%{?rhel} > 6
%global with_intl   1
%global with_sqlite3   1
%else
%global with_intl   1
%global with_sqlite3   0
%endif
%if 0%{?fedora} || 0%{?rhel} >= 6
%global with_libedit   1
%global with_enchant   1
%else
%global with_libedit   0
%global with_enchant   0
%endif
%if 0%{?fedora} >= 27 || 0%{?rhel} >= 8
%global with_pcre      1
%else
%global with_pcre      0
%endif

%if 0%{?__isa_bits:1}
%global isasuffix -%{__isa_bits}
%else
%global isasuffix %nil
%endif

%global with_dtrace 0

%if 0%{?fedora} < 16 && 0%{?rhel} < 7
%global with_systemd 0
%else
%global with_systemd 1
%endif

%global with_zip     1

%if %{with_zip}
Requires: ea-libzip
BuildRequires: ea-libzip
BuildRequires: ea-libzip-devel
%endif

%if 0%{?fedora} < 18 && 0%{?rhel} < 7
%global db_devel  db4-devel
%else
%global db_devel  libdb-devel
%endif

%define ea_openssl_ver 1.1.1d-1

%if 0%{?rhel} >= 8
%define libcurl_ver 7.61.0
%else
%define ea_libcurl_ver 7.68.0-2
%endif

Summary:  PHP scripting language for creating dynamic web sites
%if %{with_httpd}
Summary:  PHP DSO
%endif
Vendor:   cPanel, Inc.
Name:     %{?scl_prefix}php
Version:  7.4.19
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4588 for more details
%define release_prefix 1
Release:  %{release_prefix}%{?dist}.cpanel
# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM is licensed under BSD
License:  PHP and Zend and BSD
Group:    Development/Languages
URL:      http://www.php.net/

Source0: http://www.php.net/distributions/php-%{version}.tar.bz2
Source1: https://www.litespeedtech.com/packages/lsapi/php-litespeed-7.9.tgz
Source2: php.ini
Source3: macros.php
Source4: php-fpm.conf
Source5: php-fpm-www.conf
Source6: php-fpm.service
Source7: php-fpm.logrotate
Source8: php-fpm.sysconfig
Source11: php-fpm.init
# Configuration files for some extensions
Source50: 10-opcache.ini
Source51: opcache-default.blacklist

Patch42: 0001-EA4-OBS-ready.patch

# Prevent pear package from dragging in devel, which drags in a lot of
# stuff for a production machine: https://bugzilla.redhat.com/show_bug.cgi?id=657812
Patch43: 0002-Prevent-PEAR-package-from-bringing-in-devel.patch

# cPanel patches
Patch100: 0003-Modify-standard-mail-extenstion-to-add-X-PHP-Script-.patch
Patch101: 0004-Removed-ZTS-support.patch
Patch102: 0005-Ensure-that-php.d-is-not-scanned-when-PHPRC-is-set.patch
Patch104: 0006-FPM-Ensure-docroot-is-in-the-user-s-homedir.patch
Patch105: 0007-Chroot-FPM-users-with-noshell-and-jailshell.patch
Patch106: 0008-Patch-epoll.c-per-bug-report-in-upstream.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch107: 0009-Add-support-for-use-of-the-system-timezone-database-.patch
Patch108: 0010-Add-AUTOCONF-AUTOHEADER-variables-for-C6.patch

Patch402: 0011-0022-PLESK-missed-kill.patch
Patch403: 0012-Revert-new-.user.ini-search-behavior.patch

BuildRequires: ea-libxml2-devel
BuildRequires: bzip2-devel, %{db_devel}

%if 0%{?rhel} >= 8
BuildRequires: libcurl >= %{libcurl_ver}, libcurl-devel >= %{libcurl_ver}
BuildRequires: brotli brotli-devel
%else
BuildRequires: %{ns_name}-libcurl >= %{ea_libcurl_ver}, %{ns_name}-libcurl-devel >= %{ea_libcurl_ver}
%endif

BuildRequires: pam-devel
BuildRequires: scl-utils-build
BuildRequires: libstdc++-devel

%if 0%{?rhel} > 7
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%else
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%endif

# For Argon2 support
BuildRequires: ea-libargon2-devel
Requires: ea-libargon2
%if %{with_sqlite3}
BuildRequires: sqlite-devel >= 3.7.5
%endif
BuildRequires: zlib-devel, smtpdaemon
%if %{with_libedit}
BuildRequires: libedit-devel
%else
BuildRequires: readline-devel
%endif
%if %{with_pcre}
BuildRequires: pcre2-devel >= 10.30
%else
Provides:      Provides: bundled(pcre2) = 10.32
%endif
BuildRequires: bzip2, perl, libtool >= 1.4.3, gcc-c++
BuildRequires: libtool-ltdl-devel
%if %{with_dtrace}
BuildRequires: python
BuildRequires: systemtap-sdt-devel
%endif
BuildRequires: bison

%if 0%{rhel} > 6
BuildRequires: autoconf
%else
BuildRequires: autotools-latest-autoconf
%endif


%if %{with_httpd}
BuildRequires: ea-apache24-devel
# NOTE: Typically 2 additional BuildRequires: statements are needed to let
# the RPM dependency solver know what mpm and cgi module to install.  However,
# we're using an OBS-centric Project Config called, Prefer: which does this
# for us.
Requires: ea-apache24-mmn = %{_httpd_mmn}
Provides: %{?scl_prefix}mod_php = %{version}-%{release}
Provides: ea-mod_php = %{embed_version}
Conflicts: ea-mod_php > %{embed_version}, ea-mod_php < %{embed_version}
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires(pre): ea-webserver
Requires: ea-apache24-mpm = forked
%endif

# For backwards-compatibility, require php-cli for the time being:
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

# For C6 we need our autotools installed
%if 0%{rhel} < 7
Requires: autotools-latest-autoconf
%endif

# Don't provides extensions, which are not shared library, as .so
%{?filter_provides_in: %filter_provides_in %{_libdir}/php/modules/.*\.so$}
%if %{with_httpd}
%{?filter_provides_in: %filter_provides_in %{_httpd_moddir}/.*\.so$}
%endif
%{?filter_setup}


%description
%if %{with_httpd}
Package that installs Apache`s mod_php DSO module for PHP 7.4
%else
PHP is an HTML-embedded scripting language. PHP attempts to make it
easy for developers to write dynamically generated web pages. PHP also
offers built-in database integration for several commercial and
non-commercial database management systems, so writing a
database-enabled webpage with PHP is fairly simple. The most common
use of PHP coding is probably as a replacement for CGI scripts.
%endif


%package cli
Group: Development/Languages
Summary: Command-line interface for PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-cgi = %{version}-%{release}, %{?scl_prefix}php-cgi%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pcntl = %{version}-%{release} , %{?scl_prefix}php-pcntl%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-readline = %{version}-%{release}, %{?scl_prefix}php-readline%{?_isa} = %{version}-%{release}

# For the ea-php-cli wrapper rpm
Requires: ea-php-cli
Requires: ea-php-cli-lsphp
Requires: %{?scl_prefix}php-litespeed = %{version}-%{release}

%description cli
The php-cli package contains the command-line interface
executing PHP scripts, /usr/bin/php, and the CGI interface.

%package dbg
Group: Development/Languages
Summary: The interactive PHP debugger
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description dbg
The %{?scl_prefix}php-dbg package contains the interactive PHP debugger.

%if %{with_fpm}
%package fpm
Group: Development/Languages
Summary: PHP FastCGI Process Manager
# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM and fpm are licensed under BSD
License: PHP and Zend and BSD
Requires: ea-apache24-mod_proxy_fcgi
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
%if %{with_systemd}
BuildRequires: systemd-libs
BuildRequires: systemd-devel
BuildRequires: systemd-units
Requires: systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
# This is actually needed for the %%triggerun script but Requires(triggerun)
# is not valid.  We can use %%post because this particular %%triggerun script
# should fire just after this package is installed.
Requires(post): systemd-sysv
%else
# This is for /sbin/service
Requires(preun): initscripts
Requires(postun): initscripts
%endif

%description fpm
PHP-FPM (FastCGI Process Manager) is an alternative PHP FastCGI
implementation with some additional features useful for sites of
any size, especially busier sites.
%endif

%if %{with_lsws}
%package litespeed
Summary: LiteSpeed Web Server PHP support
Group: Development/Languages
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description litespeed
The %{?scl_prefix}php-litespeed package provides the %{_bindir}/lsphp command
used by the LiteSpeed Web Server (LSAPI enabled PHP).
%endif

%package common
Group: Development/Languages
Summary: Common files for PHP
# All files licensed under PHP version 3.01, except
# fileinfo is licensed under PHP version 3.0
# regex, libmagic are licensed under BSD
# main/snprintf.c, main/spprintf.c and main/rfc1867.c are ASL 1.0
License: PHP and BSD and ASL 1.0
# ABI/API check - Arch specific
Provides: %{?scl_prefix}php(api) = %{apiver}%{isasuffix}
Provides: %{?scl_prefix}php(zend-abi) = %{zendver}%{isasuffix}
Provides: %{?scl_prefix}php(language) = %{version}
Provides: %{?scl_prefix}php(language)%{?_isa} = %{version}
# Provides for all builtin/shared modules:
Provides: %{?scl_prefix}php-core = %{version}, %{?scl_prefix}php-core%{?_isa} = %{version}
Provides: %{?scl_prefix}php-ctype = %{version}-%{release}, %{?scl_prefix}php-ctype%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-date = %{version}-%{release}, %{?scl_prefix}php-date%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-filter = %{version}-%{release}, %{?scl_prefix}php-filter%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-gmp = %{version}-%{release}, %{?scl_prefix}php-gmp%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-hash = %{version}-%{release}, %{?scl_prefix}php-hash%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-mhash = %{version}-%{release}, %{?scl_prefix}php-mhash%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-json = %{version}-%{release}, %{?scl_prefix}php-json%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pecl-json = %{version}-%{release}, %{?scl_prefix}php-pecl-json%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pecl(json) = %{version}-%{release}, %{?scl_prefix}php-pecl(json)%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-libxml = %{version}-%{release}, %{?scl_prefix}php-libxml%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-openssl = %{version}-%{release}, %{?scl_prefix}php-openssl%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-phar = %{version}-%{release}, %{?scl_prefix}php-phar%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pcre = %{version}-%{release}, %{?scl_prefix}php-pcre%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-reflection = %{version}-%{release}, %{?scl_prefix}php-reflection%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-session = %{version}-%{release}, %{?scl_prefix}php-session%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-spl = %{version}-%{release}, %{?scl_prefix}php-spl%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-standard = %{version}, %{?scl_prefix}php-standard%{?_isa} = %{version}
Provides: %{?scl_prefix}php-tokenizer = %{version}-%{release}, %{?scl_prefix}php-tokenizer%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-zlib = %{version}-%{release}, %{?scl_prefix}php-zlib%{?_isa} = %{version}-%{release}
%{!?scl:Obsoletes: php-openssl, php-pecl-json, php-json, php-pecl-phar, php-pecl-Fileinfo}
%{?scl:Requires: %{scl}-runtime}

%description common
The %{?scl_prefix}php-common package contains files used by both
the %{?scl_prefix}php package and the php-cli package.

%package devel
Group: Development/Libraries
Summary: Files needed for building PHP extensions
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}, autoconf, automake
%if %{with_pcre}
Requires: pcre2-devel%{?_isa} >= 10.30
%endif

%description devel
The %{?scl_prefix}php-devel package contains the files needed for building PHP
extensions. If you need to compile your own PHP extensions, you will
need to install this package.

%package opcache
Summary:   The Zend OPcache
Group:     Development/Languages
License:   PHP
Requires:  %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides:  %{?scl_prefix}php-pecl-zendopcache = %{version}-%{release}
Provides:  %{?scl_prefix}php-pecl-zendopcache%{?_isa} = %{version}-%{release}
Provides:  %{?scl_prefix}php-pecl(opcache) = %{version}-%{release}
Provides:  %{?scl_prefix}php-pecl(opcache)%{?_isa} = %{version}-%{release}

%description opcache
The Zend OPcache provides faster PHP execution through opcode caching and
optimization. It improves PHP performance by storing precompiled script
bytecode in the shared memory. This eliminates the stages of reading code from
the disk and compiling it on future access. In addition, it applies a few
bytecode optimization patterns that make code execution faster.

%package bz2
Summary: A module for PHP applications that interface with .bz2 files
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-bz2 = %{version}-%{release}, %{?scl_prefix}php-bz2%{?_isa} = %{version}-%{release}

%description bz2
The php-bz2 package delivers a module which will allow PHP scripts to
interface with .bz2 files.

%package calendar
Summary: A module for PHP applications that need date/time calculations
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-calendar = %{version}-%{release}, %{?scl_prefix}php-calendar%{?_isa} = %{version}-%{release}

%description calendar
The php-calendar package delivers a module which will allow PHP scripts to
do date and time conversions and calculations.

%package curl
Summary: A module for PHP applications that need to interface with curl
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
%if 0%{rhel} < 8
Requires: %{ns_name}-libcurl >= %{ea_libcurl_ver}
%else
Requires: libcurl
%endif
BuildRequires: libssh2 libssh2-devel libidn libidn-devel ea-libnghttp2-devel
Provides: %{?scl_prefix}php-curl = %{version}-%{release}, %{?scl_prefix}php-curl%{?_isa} = %{version}-%{release}

%description curl
The php-curl package delivers a module which will allow PHP
scripts to connect and communicate to many different types of servers
with many different types of protocols. libcurl currently supports the
http, https, ftp, gopher, telnet, dict, file, and ldap
protocols. libcurl also supports HTTPS certificates, HTTP POST, HTTP
PUT, FTP uploading, HTTP form based upload, proxies, cookies, and
user+password authentication.

%package exif
Summary: A module for PHP applications that need to work with image metadata
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-exif = %{version}-%{release}, %{?scl_prefix}php-exif%{?_isa} = %{version}-%{release}

%description exif
The php-exif package delivers a module which will allow PHP scripts to
work with image meta data. For example, you may use exif functions to
read meta data of pictures taken from digital cameras by working with
information stored in the headers of the JPEG and TIFF images.

%package fileinfo
Summary: A module for PHP applications that need to detect file types
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-fileinfo = %{version}-%{release}, %{?scl_prefix}php-fileinfo%{?_isa} = %{version}-%{release}

%description fileinfo
The php-fileinfo package delivers a module which will allow PHP
scripts to try to guess the content type and encoding of a file by
looking for certain magic byte sequences at specific positions within
the file. While this is not a bullet proof approach the heuristics
used do a very good job.

%package ftp
Summary: A module for PHP applications that need full FTP protocol support
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-ftp = %{version}-%{release}, %{?scl_prefix}php-ftp%{?_isa} = %{version}-%{release}

%description ftp
The php-ftp package delivers a module which will allow PHP scripts
client access to files servers speaking the File Transfer Protocol
(FTP) as defined in http://www.faqs.org/rfcs/rfc959. This extension is
meant for detailed access to an FTP server providing a wide range of
control to the executing script. If you only wish to read from or
write to a file on an FTP server, consider using the ftp:// wrapper
with the %{?scl_prefix}php-filesystem package which provides a simpler
and more intuitive interface.

%package gettext
Summary: A module for PHP applications that need native language support
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-gettext = %{version}-%{release}, %{?scl_prefix}php-gettext%{?_isa} = %{version}-%{release}

%description gettext
The php-gettext package delivers a module which will allow PHP scripts
to access an NLS (Native Language Support) API which can be used to
internationalize your PHP applications. Please see the gettext
documentation for your system for a thorough explanation of these
functions or view the docs at
http://www.gnu.org/software/gettext/manual/gettext.html.

%package iconv
Summary: A module for PHP applications that need to convert character sets
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-iconv = %{version}-%{release}, %{?scl_prefix}php-iconv%{?_isa} = %{version}-%{release}

%description iconv
The php-iconv package delivers a module which will allow PHP scripts
to access the iconv character set conversion facility. With this
module, you can turn a string represented by a local character set
into the one represented by another character set, which may be the
Unicode character set. Supported character sets depend on the iconv
implementation of your system. Note that the iconv function on some
systems may not work as you expect. In such case, it would be a good
idea to install the GNU libiconv library. It will most likely end up
with more consistent results.

%package imap
Summary: A module for PHP applications that use IMAP
#Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Provides: %{?scl_prefix}php-imap%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

BuildRequires: krb5-devel%{?_isa}

%if 0%{?rhel} > 7
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%else
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%endif

%if 0%{?rhel} >= 8
Requires: %{?scl_prefix}libc-client
BuildRequires: %{?scl_prefix}libc-client-devel
%else
Requires: %{?scl_prefix}libc-client%{?_isa}
BuildRequires: %{?scl_prefix}libc-client-devel%{?_isa}
%endif

%description imap
The %{?scl_prefix}php-imap module will add IMAP (Internet Message Access Protocol)
support to PHP. IMAP is a protocol for retrieving and uploading e-mail
messages on mail servers. PHP is an HTML-embedded scripting language.

%package ldap
Summary: A module for PHP applications that use LDAP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

BuildRequires: cyrus-sasl-devel, openldap-devel

%if 0%{?rhel} > 7
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%else
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%endif

%description ldap
The %{?scl_prefix}php-ldap package adds Lightweight Directory Access Protocol (LDAP)
support to PHP. LDAP is a set of protocols for accessing directory
services over the Internet. PHP is an HTML-embedded scripting
language.

%package pdo
Summary: A database access abstraction module for PHP applications
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
# ABI/API check - Arch specific
Provides: %{?scl_prefix}php-pdo-abi = %{pdover}%{isasuffix}
Provides: %{?scl_prefix}php(pdo-abi) = %{pdover}%{isasuffix}
%if %{with_sqlite3}
Provides: %{?scl_prefix}php-sqlite3 = %{version}-%{release}, %{?scl_prefix}php-sqlite3%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_sqlite = %{version}-%{release}, %{?scl_prefix}php-pdo_sqlite%{?_isa} = %{version}-%{release}
%endif

%description pdo
The %{?scl_prefix}php-pdo package contains a dynamic shared object that will add
a database access abstraction layer to PHP.  This module provides
a common interface for accessing MySQL, PostgreSQL or other
databases.

%package mysqlnd
Summary: A module for PHP applications that use MySQL databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database = %{version}-%{release}
Provides: %{?scl_prefix}php-mysql = %{version}-%{release}
Provides: %{?scl_prefix}php-mysql%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-mysqli = %{version}-%{release}
Provides: %{?scl_prefix}php-mysqli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_mysql = %{version}-%{release}, %{?scl_prefix}php-pdo_mysql%{?_isa} = %{version}-%{release}

%description mysqlnd
The %{?scl_prefix}php-mysqlnd package contains a dynamic shared object that will add
MySQL database support to PHP. MySQL is an object-relational database
management system. PHP is an HTML-embeddable scripting language. If
you need MySQL support for PHP applications, you will need to install
this package and the php package.

This package use the MySQL Native Driver

%package posix
Summary: Modules for PHP scripts that need access to POSIX functions
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-posix = %{version}-%{release}, %{?scl_prefix}php-posix%{?_isa} = %{version}-%{release}

%description posix
The php-posix package adds a PHP interface to those functions defined
in the IEEE 1003.1 (POSIX.1) standards document which are not
accessible through other means.

%package pgsql
Summary: A PostgreSQL database module for PHP
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_pgsql = %{version}-%{release}, %{?scl_prefix}php-pdo_pgsql%{?_isa} = %{version}-%{release}

BuildRequires: krb5-devel, postgresql-devel

%if 0%{?rhel} > 7
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
BuildRequires: openssl, openssl-devel
Requires: openssl
%else
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}, ea-openssl11-devel >= %{ea_openssl_ver}
Requires: ea-openssl11 >= %{ea_openssl_ver}
%endif

%description pgsql
The %{?scl_prefix}php-pgsql package add PostgreSQL database support to PHP.
PostgreSQL is an object-relational database management
system that supports almost all SQL constructs. PHP is an
HTML-embedded scripting language. If you need back-end support for
PostgreSQL, you should install this package in addition to the main
php package.

%package process
Summary: Modules for PHP script using system process interfaces
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-shmop = %{version}-%{release}, %{?scl_prefix}php-shmop%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-sysvsem = %{version}-%{release}, %{?scl_prefix}php-sysvsem%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-sysvshm = %{version}-%{release}, %{?scl_prefix}php-sysvshm%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-sysvmsg = %{version}-%{release}, %{?scl_prefix}php-sysvmsg%{?_isa} = %{version}-%{release}

%description process
The %{?scl_prefix}php-process package contains dynamic shared objects which add
support to PHP using system interfaces for inter-process
communication.

%package odbc
Summary: A module for PHP applications that use ODBC databases
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# pdo_odbc is licensed under PHP version 3.0
License: PHP
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_odbc = %{version}-%{release}, %{?scl_prefix}php-pdo_odbc%{?_isa} = %{version}-%{release}
BuildRequires: unixODBC-devel

%description odbc
The %{?scl_prefix}php-odbc package contains a dynamic shared object that will add
database support through ODBC to PHP. ODBC is an open specification
which provides a consistent API for developers to use for accessing
data sources (which are often, but not always, databases). PHP is an
HTML-embeddable scripting language. If you need ODBC support for PHP
applications, you will need to install this package and the php
package.

%package soap
Summary: A module for PHP applications that use the SOAP protocol
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: ea-libxml2-devel

%description soap
The %{?scl_prefix}php-soap package contains a dynamic shared object that will add
support to PHP for using the SOAP web services protocol.

%package sockets
Summary: A module for PHP applications that need low-level access to sockets
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-sockets = %{version}-%{release}, %{?scl_prefix}php-sockets%{?_isa} = %{version}-%{release}

%description sockets
The php-sockets package delivers a module which will allow PHP scripts
access to a low-level interface to the socket communication functions
based on the popular BSD sockets, providing the possibility to act as
a socket server as well as a client.

%if %{with_interbase}
%package interbase
Summary: A module for PHP applications that use Interbase/Firebird databases
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires:  firebird-devel
Requires: %{?scl_prefix}php-pdo%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php_database = %{version}-%{release}
Provides: %{?scl_prefix}php-firebird = %{version}-%{release}, %{?scl_prefix}php-firebird%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-pdo_firebird = %{version}-%{release}, %{?scl_prefix}php-pdo_firebird%{?_isa} = %{version}-%{release}

%description interbase
The %{?scl_prefix}php-interbase package contains a dynamic shared object that will add
database support through Interbase/Firebird to PHP.

InterBase is the name of the closed-source variant of this RDBMS that was
developed by Borland/Inprise.

Firebird is a commercially independent project of C and C++ programmers,
technical advisors and supporters developing and enhancing a multi-platform
relational database management system based on the source code released by
Inprise Corp (now known as Borland Software Corp) under the InterBase Public
License.
%endif

%package snmp
Summary: A module for PHP applications that query SNMP-managed devices
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}, net-snmp
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: net-snmp-devel

%description snmp
The %{?scl_prefix}php-snmp package contains a dynamic shared object that will add
support for querying SNMP devices to PHP.  PHP is an HTML-embeddable
scripting language. If you need SNMP support for PHP applications, you
will need to install this package and the php package.

%package xml
Summary: A module for PHP applications which use XML
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-dom = %{version}-%{release}, %{?scl_prefix}php-dom%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-domxml = %{version}-%{release}, %{?scl_prefix}php-domxml%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-xmlreader = %{version}-%{release}, %{?scl_prefix}php-xmlreader%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-xmlwriter = %{version}-%{release}, %{?scl_prefix}php-xmlwriter%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-xsl = %{version}-%{release}, %{?scl_prefix}php-xsl%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-simplexml = %{version}-%{release}, %{?scl_prefix}php-simplexml%{?_isa} = %{version}-%{release}
BuildRequires: libxslt-devel >= 1.0.18-1, ea-libxml2-devel
Requires: ea-libxml2

%description xml
The %{?scl_prefix}php-xml package contains dynamic shared objects which add support
to PHP for manipulating XML documents using the DOM tree,
and performing XSL transformations on XML documents.

%package xmlrpc
Summary: A module for PHP applications which use the XML-RPC protocol
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libXMLRPC is licensed under BSD
License: PHP and BSD
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description xmlrpc
The %{?scl_prefix}php-xmlrpc package contains a dynamic shared object that will add
support for the XML-RPC protocol to PHP.

%package mbstring
Summary: A module for PHP applications which need multi-byte string handling
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libmbfl is licensed under LGPLv2
# onigurama is licensed under BSD
# ucgendat is licensed under OpenLDAP
License: PHP and LGPLv2 and BSD and OpenLDAP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: ea-oniguruma-devel
Requires: ea-oniguruma-devel

%description mbstring
The %{?scl_prefix}php-mbstring package contains a dynamic shared object that will add
support for multi-byte string handling to PHP.

%package gd
Summary: A module for PHP applications for using the gd graphics library
Group: Development/Languages
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Requires: libjpeg-turbo%{?_isa}, libpng%{?_isa}, libXpm%{?_isa}, freetype%{?_isa}
BuildRequires: libjpeg-turbo-devel%{?_isa}, libpng-devel%{?_isa}, libXpm-devel%{?_isa}, freetype-devel%{?_isa}
%if %{with_webp}
Requires: libwebp%{?_isa}
BuildRequires: libwebp-devel%{?_isa}
%endif

%description gd
The %{?scl_prefix}php-gd package contains a dynamic shared object that will add
support for using the gd graphics library to PHP.

%package gmp
Summary: A module for PHP applications for using the GNU MP library
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires: gmp-devel%{?_isa}
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description gmp
These functions allow you to work with arbitrary-length integers
using the GNU MP library.

%package bcmath
Summary: A module for PHP applications for using the bcmath library
Group: Development/Languages
# All files licensed under PHP version 3.01, except
# libbcmath is licensed under LGPLv2+
License: PHP and LGPLv2+
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description bcmath
The %{?scl_prefix}php-bcmath package contains a dynamic shared object that will add
support for using the bcmath library to PHP.

%package dba
Summary: A database abstraction layer module for PHP applications
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
BuildRequires: %{db_devel}, tokyocabinet-devel
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}

%description dba
The %{?scl_prefix}php-dba package contains a dynamic shared object that will add
support for using the DBA database abstraction layer to PHP.

%if %{with_tidy}
%package tidy
Summary: Standard PHP module provides tidy library support
Group: Development/Languages
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Requires: %{ns_name}-libtidy
BuildRequires: %{ns_name}-libtidy-devel

%description tidy
The %{?scl_prefix}php-tidy package contains a dynamic shared object that will add
support for using the tidy library to PHP.
%endif

%if %{with_embed}
%package embedded
Summary: PHP library for embedding in applications
Group: System Environment/Libraries
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
# doing a real -devel package for just the .so symlink is a bit overkill
Provides: %{?scl_prefix}php-embedded-devel = %{version}-%{release}
Provides: %{?scl_prefix}php-embedded-devel%{?_isa} = %{version}-%{release}

%description embedded
The %{?scl_prefix}php-embedded package contains a library which can be embedded
into applications to provide PHP scripting language support.
%endif

%package pspell
Summary: A module for PHP applications for using pspell interfaces
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: aspell-devel >= 0.50.0

%description pspell
The %{?scl_prefix}php-pspell package contains a dynamic shared object that will add
support for using the pspell library to PHP.

%if %{with_intl}
%package intl
Summary: Internationalization extension for PHP applications
Group: System Environment/Libraries
# All files licensed under PHP version 3.01
License: PHP
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Requires: ea-libicu
BuildRequires: ea-libicu-devel >= 50.1

%description intl
The %{?scl_prefix}php-intl package contains a dynamic shared object that will add
support for using the ICU library to PHP.
%endif

%if %{with_enchant}
%package enchant
Summary: Enchant spelling extension for PHP applications
# All files licensed under PHP version 3.0
License: PHP
Group: System Environment/Libraries
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
BuildRequires: enchant-devel >= 1.2.4

%description enchant
The %{?scl_prefix}php-enchant package contains a dynamic shared object that will add
support for using the enchant library to PHP.
%endif

%if %{with_zip}
%package zip
Summary: A module for PHP applications that need to handle .zip files
Group: Development/Languages
License: PHP
Requires: ea-libzip
Requires: %{?scl_prefix}php-common%{?_isa} = %{version}-%{release}
Requires: %{?scl_prefix}php-cli%{?_isa} = %{version}-%{release}
Provides: %{?scl_prefix}php-zip = %{version}-%{release}, %{?scl_prefix}php-zip%{?_isa} = %{version}-%{release}

%description zip
The %{?scl_prefix}php-zip package delivers a module which will allow PHP scripts
to transparently read or write ZIP compressed archives and the files
inside them.
%endif


%prep
: Building %{name}-%{version}-%{release} with systemd=%{with_systemd} interbase=%{with_interbase} sqlite3=%{with_sqlite3} tidy=%{with_tidy} zip=%{with_zip}

%setup -q -n php-%{version}

%patch42 -p1 -b .systemdpackage
%patch43 -p1 -b .phpize
%patch100 -p1 -b .cpanelmailheader
%patch101 -p1 -b .disablezts
%patch102 -p1 -b .cpanelea4ini
%patch104 -p1 -b .fpmuserini
%patch105 -p1 -b .fpmjailshell
%patch106 -p1 -b .fpmepoll
%patch107 -p1 -b .systzdata

%if 0%{rhel} < 7
%patch108 -p1 -b .autoconfheader
%endif

%patch402 -p1 -b .missedkill
%patch403 -p1 -b .userini

# 7.4 does not need this for tidy even thought the instructions say to do it, weird ...
# sed -i 's/buffio.h/tidybuffio.h/' ext/tidy/*.c


# Fixes for tests
#%patch300 -p1 -b .datetests
#%if %{with_libpcre}
#if ! pkg-config libpcre --atleast-version 8.34 ; then
# Only apply when system libpcre < 8.34
#%patch301 -p1 -b .pcre834
#fi
#%endif

# Prevent %%doc confusion over LICENSE files
cp Zend/LICENSE Zend/ZEND_LICENSE
cp TSRM/LICENSE TSRM_LICENSE
cp sapi/fpm/LICENSE fpm_LICENSE
cp ext/mbstring/libmbfl/LICENSE libmbfl_LICENSE
cp ext/fileinfo/libmagic/LICENSE libmagic_LICENSE
cp ext/bcmath/libbcmath/LICENSE libbcmath_LICENSE

%if %{with_lsws}
# Remove the bundled version of litespeed
# and replace it with the latest version
cd sapi
tar -xvf %{SOURCE1} --exclude=Makefile.frag --exclude=config.m4
cd ..
%endif

# Multiple builds for multiple SAPIs
mkdir \
%if %{with_embed}
    build-embedded \
%endif
%if %{with_fpm}
    build-fpm \
%endif
%if %{with_httpd}
    build-apache \
%endif
    build-cgi

# ----- Manage known as failed test -------
# affected by systzdata patch
rm -f ext/date/tests/timezone_location_get.phpt
rm -f ext/date/tests/timezone_version_get.phpt
rm -f ext/date/tests/timezone_version_get_basic1.phpt
# fails sometime
rm -f ext/sockets/tests/mcast_ipv?_recv.phpt
# Should be skipped but fails sometime
rm ext/standard/tests/file/file_get_contents_error001.phpt
# cause stack exhausion
rm Zend/tests/bug54268.phpt
rm Zend/tests/bug68412.phpt

# Safety check for API version change.
pver=$(sed -n '/#define PHP_VERSION /{s/.* "//;s/".*$//;p}' main/php_version.h)
if test "x${pver}" != "x%{version}"; then
   : Error: Upstream PHP version is now ${pver}, expecting %{version}.
   : Update the version macros and rebuild.
   exit 1
fi

vapi=`sed -n '/#define PHP_API_VERSION/{s/.* //;p}' main/php.h`
if test "x${vapi}" != "x%{apiver}"; then
   : Error: Upstream API version is now ${vapi}, expecting %{apiver}.
   : Update the apiver macro and rebuild.
   exit 1
fi

vzend=`sed -n '/#define ZEND_MODULE_API_NO/{s/^[^0-9]*//;p;}' Zend/zend_modules.h`
if test "x${vzend}" != "x%{zendver}"; then
   : Error: Upstream Zend ABI version is now ${vzend}, expecting %{zendver}.
   : Update the zendver macro and rebuild.
   exit 1
fi

# Safety check for PDO ABI version change
vpdo=`awk '/^#define PDO_DRIVER_API/ { print $3 } ' ext/pdo/php_pdo_driver.h`
if test "x${vpdo}" != "x%{pdover}"; then
   : Error: Upstream PDO ABI version is now ${vpdo}, expecting %{pdover}.
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
sed -e "s/@PHP_APIVER@/%{apiver}%{isasuffix}/" \
    -e "s/@PHP_ZENDVER@/%{zendver}%{isasuffix}/" \
    -e "s/@PHP_PDOVER@/%{pdover}%{isasuffix}/" \
    -e "s/@PHP_VERSION@/%{version}/" \
    -e "s:@LIBDIR@:%{_libdir}:" \
    -e "s:@ETCDIR@:%{_sysconfdir}:" \
    -e "s:@INCDIR@:%{_includedir}:" \
    -e "s:@BINDIR@:%{_bindir}:" \
    -e 's/@SCL@/%{ns_name}_%{pkg}_/' \
    %{SOURCE3} | tee macros.php
# php-fpm configuration files for tmpfiles.d
# TODO echo "d /run/php-fpm 755 root root" >php-fpm.tmpfiles

# Some extensions have their own configuration file
cp %{SOURCE50} 10-opcache.ini
%ifarch x86_64
%if 0%{?rhel} != 6
sed -e '/opcache.huge_code_pages/s/0/1/' -i 10-opcache.ini
%endif
%endif
cp %{SOURCE51} .
sed -e 's:%{_root_sysconfdir}:%{_sysconfdir}:' \
    -i 10-opcache.ini



%build
%if 0%{?rhel} < 7
. /opt/rh/devtoolset-7/enable
%endif

# aclocal workaround - to be improved
%if 0%{?fedora} >= 11 || 0%{?rhel} >= 6
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >>aclocal.m4
%endif

# Force use of system libtool:
libtoolize --force --copy
%if 0%{?fedora} >= 11 || 0%{?rhel} >= 6
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >build/libtool.m4
%else
cat `aclocal --print-ac-dir`/libtool.m4 > build/libtool.m4
%endif

# Regenerate configure scripts (patches change config.m4's)
touch configure.in

%if 0%{rhel} < 7
scl enable autotools-latest './buildconf --force'
%else
./buildconf --force
%endif

%if 0%{rhel} < 8
CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-pointer-sign"
%else
CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-pointer-sign -mshstk"
%endif
export CFLAGS

%if 0%{?rhel} < 8
export SNMP_SHARED_LIBADD="-Wl,-rpath=/opt/cpanel/ea-openssl11/%{_lib}"
export CURL_SHARED_LIBADD="-Wl,-rpath=/opt/cpanel/ea-openssl11/%{_lib} -Wl,-rpath=/opt/cpanel/ea-brotli/%{_lib}"
%else
export CURL_SHARED_LIBADD="-Wl,-rpath=/opt/cpanel/ea-brotli/%{_lib}"
%endif

# Install extension modules in %{_libdir}/php/modules.
EXTENSION_DIR=%{_libdir}/php/modules; export EXTENSION_DIR

# Set PEAR_INSTALLDIR to ensure that the hard-coded include_path
# includes the PEAR directory even though pear is packaged
# separately.
PEAR_INSTALLDIR=%{_datadir}/pear; export PEAR_INSTALLDIR
%if 0%{?rhel} >= 8
export XLDFLAGS=$LDFLAGS
%endif

# Shell function to configure and build a PHP tree.
build() {
# Old/recent bison version seems to produce a broken parser;
# upstream uses GNU Bison 2.3. Workaround:
mkdir Zend && cp ../Zend/zend_{language,ini}_{parser,scanner}.[ch] Zend

# Always static:
# date, filter, libxml, reflection, spl: not supported
# hash: for PHAR_SIG_SHA256 and PHAR_SIG_SHA512
# session: dep on hash, used by soap
# pcre: used by filter, zip
# pcntl, readline: only used by CLI sapi
# openssl: for PHAR_SIG_OPENSSL
# zlib: used by image

%if 0%{rhel} < 8
export PKG_CONFIG_PATH=/opt/cpanel/ea-php74/root/usr/%{_lib}/pkgconfig:/opt/cpanel/ea-php74/root/usr/share/pkgconfig:/usr/%{_lib}/pkgconfig:/opt/cpanel/ea-openssl11/%{_lib}/pkgconfig:/opt/cpanel/ea-libxml2/%{_lib}/pkgconfig:/opt/cpanel/ea-libicu/lib/pkgconfig:/opt/cpanel/ea-oniguruma/%{_lib}/pkgconfig
%else
export PKG_CONFIG_PATH=/opt/cpanel/ea-php74/root/usr/%{_lib}/pkgconfig:/opt/cpanel/ea-php74/root/usr/share/pkgconfig:/usr/%{_lib}/pkgconfig:/opt/cpanel/ea-libxml2/%{_lib}/pkgconfig:/opt/cpanel/ea-libicu/lib/pkgconfig:/opt/cpanel/ea-oniguruma/%{_lib}/pkgconfig
%endif

export LIBXML_CFLAGS=-I/opt/cpanel/ea-libxml2/include/libxml2
export LIBXML_LIBS="-L/opt/cpanel/ea-libxml2/%{_lib} -lxml2"
export XSL_CFLAGS=-I/opt/cpanel/ea-libxml2/include/libxml2
export XSL_LIBS="-L/opt/cpanel/ea-libxml2/%{_lib} -lxml2"
%if 0%{?rhel} < 8
export CURL_CFLAGS=-I/opt/cpanel/libcurl/include
export CURL_LIBS="-L/opt/cpanel/libcurl/%{_lib} -lcurl"
%endif
export JPEG_CFLAGS=-I/usr/include
export JPEG_LIBS="-L/usr/%{_lib} -ljpeg"
export KERBEROS_CFLAGS=-I/usr/include
export KERBEROS_LIBS=-L/usr/%{_lib}
export SASL_CFLAGS=-I/usr/include
export SASL_LIBS=-L/usr/%{_lib}

%if 0%{?rhel} < 8
export OPENSSL_CFLAGS=-I/opt/cpanel/ea-openssl11/include
export OPENSSL_LIBS="-L/opt/cpanel/ea-openssl11/lib -lssl -lcrypto -lresolv"
%endif

%if %{with_systemd}
export SYSTEMD_LIBS=-lsystemd
%endif

%if %{with_zip}
export LIBZIP_CFLAGS=-I/opt/cpanel/ea-libzip/include
export LIBZIP_LIBS="-L/opt/cpanel/ea-libzip/lib64 -lzip"
%endif

%if 0%{?rhel} >= 8
export LDFLAGS="$XLDFLAGS -Wl,-rpath-link,/lib64 -Wl,-rpath,/lib64"
%else
export LDFLAGS="-Wl,-rpath=/opt/cpanel/ea-brotli/lib"
%endif

ln -sf ../configure
%configure \
    --cache-file=../config.cache \
    --with-libdir=%{_lib} \
    --with-config-file-path=%{_sysconfdir} \
    --with-config-file-scan-dir=%{_sysconfdir}/php.d \
    --disable-debug \
    --with-password-argon2=/opt/cpanel/libargon2 \
    --with-pic \
    --without-pear \
    --with-bz2 \
    --with-freetype \
    --with-xpm \
    --without-gdbm \
    --with-gettext \
    --with-iconv \
    --with-jpeg \
    --with-openssl \
%if %{with_pcre}
    --with-pcre-regex=%{_root_prefix} \
%endif
    --with-zlib \
    --with-layout=GNU \
    --enable-exif \
    --enable-ftp \
    --enable-sockets \
    --with-kerberos \
    --enable-shmop \
    --with-libxml \
    --with-system-tzdata \
    --with-mhash \
%if %{with_dtrace}
    --enable-dtrace \
%endif
    $*
if test $? != 0; then
  tail -500 config.log
  : configure failed
  exit 1
fi

make %{?_smp_mflags}
}

# Build /usr/bin/php-cgi with the CGI SAPI, and most the shared extensions
pushd build-cgi

build --libdir=%{_libdir}/php \
      --enable-pcntl \
      --enable-opcache \
      --enable-phpdbg \
      --with-imap=shared,%{_prefix} \
      --with-imap-ssl \
      --enable-mbstring=shared \
%if %{with_webp}
      --with-webp \
%endif
      --enable-gd=shared \
      --with-gmp=shared \
      --enable-calendar=shared \
      --enable-bcmath=shared \
      --with-bz2=shared \
      --enable-ctype=shared \
      --enable-dba=shared --with-db4=%{_root_prefix} \
                          --with-tcadb=%{_root_prefix} \
      --enable-exif=shared \
      --enable-ftp=shared \
      --with-gettext=shared \
      --with-iconv=shared \
      --enable-sockets=shared \
      --enable-tokenizer=shared \
      --with-xmlrpc=shared \
      --with-ldap=shared --with-ldap-sasl \
      --enable-mysqlnd=shared \
      --with-mysqli=shared,mysqlnd \
      --with-mysql-sock=%{mysql_sock} \
%if %{with_interbase}
      --with-interbase=shared,%{_libdir}/firebird \
      --with-pdo-firebird=shared,%{_libdir}/firebird \
%endif
      --enable-dom=shared \
      --with-pgsql=shared \
      --enable-simplexml=shared \
      --enable-xml=shared \
      --with-snmp=shared,%{_root_prefix} \
      --enable-soap=shared \
      --with-xsl=shared,%{_root_prefix} \
      --enable-xmlreader=shared --enable-xmlwriter=shared \
%if 0%{?rhel} >= 8
      --with-curl=shared \
%else
      --with-curl=shared,%{libcurl_prefix} \
%endif
      --enable-pdo=shared \
      --with-pdo-odbc=shared,unixODBC,%{_root_prefix} \
      --with-pdo-mysql=shared,mysqlnd \
      --with-pdo-pgsql=shared,%{_root_prefix} \
%if %{with_sqlite3}
      --with-pdo-sqlite=shared,%{_root_prefix} \
      --with-sqlite3=shared,%{_root_prefix} \
%else
      --without-sqlite3 \
      --without-pdo-sqlite \
%endif
      --enable-json=shared \
%if %{with_zip}
      --with-zip=shared \
%endif
      --without-readline \
%if %{with_libedit}
      --with-libedit \
%else
      --with-readline \
%endif
      --with-pspell=shared \
      --enable-phar=shared \
%if %{with_tidy}
      --with-tidy=shared,%{libtidy_prefix} \
%endif
      --enable-sysvmsg=shared --enable-sysvshm=shared --enable-sysvsem=shared \
      --enable-shmop=shared \
      --enable-posix=shared \
      --with-unixODBC=shared,%{_root_prefix} \
%if %{with_intl}
      --enable-intl=shared \
%endif
%if %{with_enchant}
      --with-enchant=shared,%{_root_prefix} \
%endif
      --enable-fileinfo=shared
popd

without_shared="--disable-gd \
      --disable-dom --disable-dba --without-unixODBC \
      --disable-opcache \
      --disable-xmlreader --disable-xmlwriter \
      --without-sqlite3 --disable-phar --disable-fileinfo \
      --disable-json --without-pspell \
      --without-curl --disable-posix --disable-xml \
      --disable-simplexml --disable-exif --without-gettext \
      --without-iconv --disable-ftp --without-bz2 --disable-ctype \
      --disable-shmop --disable-sockets --disable-tokenizer \
      --disable-sysvmsg --disable-sysvshm --disable-sysvsem \
      --without-gmp --disable-calendar"

%if %{with_httpd}
# Build Apache module, and the CLI SAPI, /usr/bin/php
pushd build-apache
build --with-apxs2=%{_httpd_apxs} \
      --libdir=%{_libdir}/php \
%if %{with_lsws}
      --enable-litespeed \
%endif
      --without-mysqli \
      --disable-pdo \
      ${without_shared}
popd
%endif

%if %{with_fpm}
# Build php-fpm
pushd build-fpm
build --enable-fpm \
%if %{with_systemd}
      --with-fpm-systemd \
%endif
      --libdir=%{_libdir}/php \
      --without-mysqli \
      --disable-pdo \
      --enable-pcntl \
      ${without_shared}
popd
%endif

%if %{with_embed}
# Build for inclusion as embedded script language into applications,
# /usr/lib[64]/libphp7.so
pushd build-embedded
build --enable-embed \
      --without-mysqli --disable-pdo \
      ${without_shared}
popd
%endif

%check
%if %runselftest

# Increase stack size (required by bug54268.phpt)
ulimit -s 32712

%if %{with_httpd}
cd build-apache
%else
cd build-cgi
%endif

# Run tests, using the CLI SAPI
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
export SKIP_ONLINE_TESTS=1
unset TZ LANG LC_ALL
if ! make test; then
  set +x
  for f in $(find .. -name \*.diff -type f -print); do
    if ! grep -q XFAIL "${f/.diff/.phpt}"
    then
      echo "TEST FAILURE: $f --"
      head -n 100 "$f"
      echo -e "\n-- $f result ends."
    fi
  done
  set -x
  #exit 1
fi
unset NO_INTERACTION REPORT_EXIT_STATUS MALLOC_CHECK_
%endif

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

# Make the eaphp## symlinks
install -d $RPM_BUILD_ROOT/usr/local/bin
ln -sf /opt/cpanel/ea-php74/root/usr/bin/php $RPM_BUILD_ROOT/usr/local/bin/ea-php74
install -d $RPM_BUILD_ROOT/usr/bin
ln -sf /opt/cpanel/ea-php74/root/usr/bin/php-cgi $RPM_BUILD_ROOT/usr/bin/ea-php74

%if %{with_embed}
# Install the version for embedded script language in applications + php_embed.h
make -C build-embedded install-sapi install-headers \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%endif

%if %{with_fpm}
# Install the php-fpm binary
make -C build-fpm install-fpm \
     INSTALL_ROOT=$RPM_BUILD_ROOT
%endif

# Install everything from the CGI SAPI build
make -C build-cgi install \
     INSTALL_ROOT=$RPM_BUILD_ROOT

# Install the default configuration file and icons
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/php.ini

# For third-party packaging:
install -m 755 -d $RPM_BUILD_ROOT%{_datadir}/php

%if %{with_httpd}
# install the DSO
install -m 755 -d $RPM_BUILD_ROOT%{_httpd_moddir}
install -m 755 build-apache/libs/libphp7.so $RPM_BUILD_ROOT%{_httpd_moddir}

# Apache config fragment
install -m 755 -d $RPM_BUILD_ROOT%{_httpd_contentdir}/icons
install -m 644 ext/gd/tests/php.gif $RPM_BUILD_ROOT%{_httpd_contentdir}/icons/%{name}.gif
%if %{?scl:1}0
install -m 755 -d $RPM_BUILD_ROOT%{_root_httpd_moddir}
ln -s %{_httpd_moddir}/libphp7.so      $RPM_BUILD_ROOT%{_root_httpd_moddir}/libphp7.so
%endif

%endif

install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php.d
install -m 755 -d $RPM_BUILD_ROOT%{_localstatedir}/lib

%if %{with_lsws}
install -m 755 build-apache/sapi/litespeed/php $RPM_BUILD_ROOT%{_bindir}/lsphp
%endif

%if %{with_fpm}
# PHP-FPM stuff
# Log

# we need to do the following to compensate for the way
# EA4 on OBS was built rather than EA4-Opensuse

install -d $RPM_BUILD_ROOT/opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/log/php-fpm
install -d $RPM_BUILD_ROOT/opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/run/php-fpm

ln -sf /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/log/php-fpm $RPM_BUILD_ROOT%{_localstatedir}/log/php-fpm
ln -sf /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/run/php-fpm $RPM_BUILD_ROOT%{_localstatedir}/run/php-fpm

# Config
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d
install -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.conf
sed -e 's:/run:%{_localstatedir}/run:' \
    -e 's:/var/log:%{_localstatedir}/log:' \
    -e 's:/etc:%{_sysconfdir}:' \
    -i $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.conf
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf
sed -e 's:/var/lib:%{_localstatedir}/lib:' \
    -e 's:/var/log:%{_localstatedir}/log:' \
    -i $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf
mv $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/www.conf.example
mv $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.conf.default .
# tmpfiles.d
# install -m 755 -d $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d
# install -m 644 php-fpm.tmpfiles $RPM_BUILD_ROOT%{_prefix}/lib/tmpfiles.d/php-fpm.conf
# install systemd unit files and scripts for handling server startup
%if %{with_systemd}
install -m 755 -d $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_unitdir}/%{?scl_prefix}php-fpm.service
sed -e 's:/run:%{_localstatedir}/run:' \
    -e 's:/etc:%{_sysconfdir}:' \
    -e 's:/usr/sbin:%{_sbindir}:' \
    -i $RPM_BUILD_ROOT%{_unitdir}/%{?scl_prefix}php-fpm.service
%else
# Service
install -m 755 -d $RPM_BUILD_ROOT%{_root_initddir}
install -m 755 %{SOURCE11} $RPM_BUILD_ROOT%{_root_initddir}/%{?scl_prefix}php-fpm
# Needed relocation for SCL
sed -e '/php-fpm.pid/s:/var:%{_localstatedir}:' \
    -e '/subsys/s/php-fpm/%{?scl_prefix}php-fpm/' \
    -e 's:/etc/sysconfig/php-fpm:%{_sysconfdir}/sysconfig/php-fpm:' \
    -e 's:/etc/php-fpm.conf:%{_sysconfdir}/php-fpm.conf:' \
    -e 's:/usr/sbin:%{_sbindir}:' \
    -i $RPM_BUILD_ROOT%{_root_initddir}/%{?scl_prefix}php-fpm
%endif

# LogRotate
install -m 755 -d $RPM_BUILD_ROOT%{_root_sysconfdir}/logrotate.d
install -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_root_sysconfdir}/logrotate.d/%{?scl_prefix}php-fpm
sed -e 's:/run:%{_localstatedir}/run:' \
    -e 's:/var/log:%{_localstatedir}/log:' \
    -i $RPM_BUILD_ROOT%{_root_sysconfdir}/logrotate.d/%{?scl_prefix}php-fpm
# Environment file
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/php-fpm
%endif


# make the cli commands available in standard root for SCL build
%if 0%{?scl:1}
#install -m 755 -d $RPM_BUILD_ROOT%{_root_bindir}
#ln -s %{_bindir}/php       $RPM_BUILD_ROOT%{_root_bindir}/%{?scl_prefix}php
#ln -s %{_bindir}/phar.phar $RPM_BUILD_ROOT%{_root_bindir}/%{?scl_prefix}phar
%endif

# Generate files lists and stub .ini files for each subpackage
for mod in pgsql odbc ldap snmp xmlrpc imap \
    mysqlnd mysqli pdo_mysql \
    mbstring gd dom xsl soap bcmath dba xmlreader xmlwriter \
    simplexml bz2 calendar ctype exif ftp gettext gmp iconv \
    sockets tokenizer opcache \
    pdo pdo_pgsql pdo_odbc json \
%if %{with_sqlite3}
    pdo_sqlite sqlite3 \
%endif
%if %{with_interbase}
    interbase pdo_firebird \
%endif
%if %{with_enchant}
    enchant \
%endif
    phar fileinfo \
%if %{with_intl}
    intl \
%endif
%if %{with_tidy}
    tidy \
%endif
%if %{with_zip}
    zip \
%endif
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
    # NOTE: rpmlint complains about the spec file using %{_sourcedir} macro.
    #       However, our usage acceptable given the transient nature of the ini files.
    #       https://fedoraproject.org/wiki/Packaging:RPM_Source_Dir?rd=PackagingDrafts/RPM_Source_Dir
    if [ -f %{_sourcedir}/$ini ]; then
      cp -p %{_sourcedir}/$ini %{buildroot}%{_sysconfdir}/php.d/$ini
    else
      cat > %{buildroot}%{_sysconfdir}/php.d/$ini <<EOF
; Enable ${mod} extension module
extension=${mod}.so
EOF
    fi
    cat > files.${mod} <<EOF
%attr(755,root,root) %{_libdir}/php/modules/${mod}.so
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/php.d/${ini}
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
%if %{with_interbase}
cat files.pdo_firebird >> files.interbase
%endif

# sysv* packaged in php-process
cat files.shmop files.sysv* > files.process

%if %{with_sqlite3}
cat files.pdo_sqlite >> files.pdo
cat files.sqlite3 >> files.pdo
%endif
# Package json and phar in -common.
cat files.json files.phar \
    files.ctype \
    files.tokenizer > files.common

# The default Zend OPcache blacklist file
install -m 644 %{SOURCE51} $RPM_BUILD_ROOT%{_sysconfdir}/php.d/opcache-default.blacklist

# Install the macros file:
install -d $RPM_BUILD_ROOT%{_root_sysconfdir}/rpm
install -m 644 -c macros.php \
           $RPM_BUILD_ROOT%{_root_sysconfdir}/rpm/macros.%{name}

# Remove unpackaged files
rm -rf $RPM_BUILD_ROOT%{_libdir}/php/modules/*.a \
       $RPM_BUILD_ROOT%{_bindir}/{phptar} \
       $RPM_BUILD_ROOT%{_datadir}/pear \
       $RPM_BUILD_ROOT%{_libdir}/libphp7.la

# Remove irrelevant docs
rm -f README.{Zeus,QNX,CVS-RULES}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
rm files.* macros.*

%if %{with_fpm}
%post fpm
%if 0%{?systemd_post:1}
%systemd_post %{?scl_prefix}php-fpm.service
%else
if [ $1 = 1 ]; then
    # Initial installation
%if %{with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
    /sbin/chkconfig --add %{?scl_prefix}php-fpm
%endif
fi
%endif

%preun fpm
%if 0%{?systemd_preun:1}
%systemd_preun %{?scl_prefix}php-fpm.service
%else
if [ $1 = 0 ]; then
    # Package removal, not upgrade
%if %{with_systemd}
    /bin/systemctl --no-reload disable %{?scl_prefix}php-fpm.service >/dev/null 2>&1 || :
    /bin/systemctl stop %{?scl_prefix}php-fpm.service >/dev/null 2>&1 || :
%else
    /sbin/service %{?scl_prefix}php-fpm stop >/dev/null 2>&1
    /sbin/chkconfig --del %{?scl_prefix}php-fpm
%endif
fi
%endif

%postun fpm
%if 0%{?systemd_postun_with_restart:1}
%systemd_postun_with_restart %{?scl_prefix}php-fpm.service
%else
%if %{with_systemd}
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ]; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart %{?scl_prefix}php-fpm.service >/dev/null 2>&1 || :
fi
%else
if [ $1 -ge 1 ]; then
    /sbin/service %{?scl_prefix}php-fpm condrestart >/dev/null 2>&1 || :
fi
%endif
%endif

# Handle upgrading from SysV initscript to native systemd unit.
# We can tell if a SysV version of php-fpm was previously installed by
# checking to see if the initscript is present.
%triggerun fpm -- %{?scl_prefix}php-fpm
%if %{with_systemd}
if [ -f /etc/rc.d/init.d/%{?scl_prefix}php-fpm ]; then
    # Save the current service runlevel info
    # User must manually run systemd-sysv-convert --apply php-fpm
    # to migrate them to systemd targets
    /usr/bin/systemd-sysv-convert --save %{?scl_prefix}php-fpm >/dev/null 2>&1 || :

    # Run these because the SysV package being removed won't do them
    /sbin/chkconfig --del %{?scl_prefix}php-fpm >/dev/null 2>&1 || :
    /bin/systemctl try-restart %{?scl_prefix}php-fpm.service >/dev/null 2>&1 || :
fi
%endif
%endif

%if %{with_embed}
%post embedded -p /sbin/ldconfig
%postun embedded -p /sbin/ldconfig
%endif

%{!?_licensedir:%global license %%doc}

%files
%defattr(-,root,root)

%if %{with_httpd}
%{_httpd_moddir}/libphp7.so
%if 0%{?scl:1}
#%dir %{_libdir}/apache2
#%dir %{_libdir}/apache2/modules
%{_root_httpd_moddir}/libphp7.so
%endif
%{_httpd_contentdir}/icons/%{name}.gif
%endif

%files common -f files.common
%defattr(-,root,root)
%doc CODING_STANDARDS.md EXTENSIONS LICENSE NEWS README*
%doc Zend/ZEND_* TSRM_LICENSE
%doc libmagic_LICENSE
%doc php.ini-*
%config(noreplace) %{_sysconfdir}/php.ini
%dir %{_sysconfdir}/php.d
%dir %{_libdir}/php
%dir %{_libdir}/php/modules
%dir %{_localstatedir}/lib
%dir %{_datadir}/php

%files cli
%defattr(-,root,root)
%{_bindir}/php
# Add the ea-php## symlinks
/usr/bin/%{ns_name}-%{pkg}
/usr/local/bin/%{ns_name}-%{pkg}
%{_bindir}/php-cgi
%{_bindir}/phar.phar
%{_bindir}/phar
# provides phpize here (not in -devel) for pecl command
%{_bindir}/phpize
%{_mandir}/man1/php.1*
%{_mandir}/man1/php-cgi.1*
%{_mandir}/man1/phar.1*
%{_mandir}/man1/phar.phar.1*
%{_mandir}/man1/phpize.1*

#{?scl: %{_root_bindir}/%{?scl_prefix}php}
#{?scl: %{_root_bindir}/%{?scl_prefix}phar}

%files dbg
%defattr(-,root,root)
%{_bindir}/phpdbg
%{_mandir}/man1/phpdbg.1*
%doc sapi/phpdbg/{README.md,CREDITS}

%if %{with_fpm}
%files fpm
%defattr(-,root,root)
# we need to do the following to compensate for the way
# EA4 on OBS was built rather than EA4-Opensuse
%attr(770,nobody,root) %dir /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/log/php-fpm
%attr(711,root,root) %dir /opt/cpanel/%{ns_name}-%{pkg}/root/usr/var/run/php-fpm
%doc php-fpm.conf.default
%license fpm_LICENSE
%config(noreplace) %{_sysconfdir}/php-fpm.conf
%config(noreplace) %{_sysconfdir}/php-fpm.d/www.conf.example
%config(noreplace) %{_sysconfdir}/php-fpm.d/www.conf.default
%config(noreplace) %{_root_sysconfdir}/logrotate.d/%{?scl_prefix}php-fpm
%config(noreplace) %{_sysconfdir}/sysconfig/php-fpm
# %{_prefix}/lib/tmpfiles.d/php-fpm.conf
%if %{with_systemd}
%{_unitdir}/%{?scl_prefix}php-fpm.service
%else
%{_root_initddir}/%{?scl_prefix}php-fpm
%endif
%{_sbindir}/php-fpm
%attr(0710,root,root) %dir %{_sysconfdir}/php-fpm.d
# log owned by nobody for log
%attr(770,nobody,root) %{_localstatedir}/log/php-fpm
%attr(711,root,root) %{_localstatedir}/run/php-fpm
%{_mandir}/man8/php-fpm.8*
%dir %{_datadir}/fpm
%{_datadir}/fpm/status.html
%dir %{_sysconfdir}/sysconfig
%dir %{_mandir}/man8
%dir %{_localstatedir}/log
%dir %{_localstatedir}/run
%endif

%if %{with_lsws}
%files litespeed
%defattr(-,root,root,-)
%{_bindir}/lsphp
%endif

%files devel
%defattr(-,root,root,-)
%{_bindir}/php-config
%{_includedir}/php
%{_libdir}/php/build
%{_mandir}/man1/php-config.1*
%{_root_sysconfdir}/rpm/macros.%{name}

%if %{with_embed}
%files embedded
%defattr(-,root,root,-)
%{_libdir}/libphp7.so
%{_libdir}/libphp7-%{embed_version}.so
%endif

%files bz2 -f files.bz2
%files calendar -f files.calendar
%files curl -f files.curl
%files exif -f files.exif
%files fileinfo -f files.fileinfo
%files ftp -f files.ftp
%files gettext -f files.gettext
%files iconv -f files.iconv
%files sockets -f files.sockets
%files posix -f files.posix
%files pgsql -f files.pgsql
%files odbc -f files.odbc
%files imap -f files.imap
%files ldap -f files.ldap
%files snmp -f files.snmp
%files xml -f files.xml
%files xmlrpc -f files.xmlrpc
%files mbstring -f files.mbstring
%defattr(-,root,root,-)
%doc libmbfl_LICENSE
%files gd -f files.gd
%defattr(-,root,root,-)
%files soap -f files.soap
%files bcmath -f files.bcmath
%defattr(-,root,root,-)
%license libbcmath_LICENSE
%files gmp -f files.gmp
%files dba -f files.dba
%files pdo -f files.pdo
%if %{with_tidy}
%files tidy -f files.tidy
%endif
%files pspell -f files.pspell
%if %{with_intl}
%files intl -f files.intl
%endif
%files process -f files.process
%if %{with_interbase}
%files interbase -f files.interbase
%endif
%if %{with_enchant}
%files enchant -f files.enchant
%endif
%files mysqlnd -f files.mysqlnd
%files opcache -f files.opcache
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/php.d/opcache-default.blacklist
%if %{with_zip}
%files zip -f files.zip
%endif

%changelog
* Thu May 06 2021 Cory McIntire <cory@cpanel.net> - 7.4.19-1
- EA-9752: Update ea-php74 from v7.4.18 to v7.4.19

* Fri Apr 30 2021 Cory McIntire <cory@cpanel.net> - 7.4.18-1
- EA-9737: Update ea-php74 from v7.4.16 to v7.4.18

* Fri Mar 05 2021 Cory McIntire <cory@cpanel.net> - 7.4.16-2
- EA-9625: Update litespeed to 7.9

* Thu Mar 04 2021 Cory McIntire <cory@cpanel.net> - 7.4.16-1
- EA-9622: Update ea-php74 from v7.4.15 to v7.4.16

* Thu Feb 04 2021 Cory McIntire <cory@cpanel.net> - 7.4.15-1
- EA-9565: Update ea-php74 from v7.4.14 to v7.4.15

* Thu Jan 07 2021 Cory McIntire <cory@cpanel.net> - 7.4.14-1
- EA-9517: Update ea-php74 from v7.4.13 to v7.4.14

* Tue Dec 01 2020 Julian Brown <julian.brown@cpanel.net> - 7.4.13-2
- ZC-8005: Replace ea-openssl11 with system openssl on C8

* Sun Nov 29 2020 Cory McIntire <cory@cpanel.net> - 7.4.13-1
- EA-9448: Update ea-php74 from v7.4.12 to v7.4.13

* Wed Nov 11 2020 Tim Mullin <tim@cpanel.net> - 7.4.12-2
- EA-9424: Fix the build on CentOS 8

* Tue Nov 03 2020 Cory McIntire <cory@cpanel.net> - 7.4.12-1
- EA-9401: Update ea-php74 from v7.4.11 to v7.4.12

* Thu Oct 29 2020 Daniel Muey <dan@cpanel.net> - 7.4.11-4
- ZC-7893: Update DSO config to factor in PHP 8

* Wed Oct 28 2020 Tim Mullin <tim@cpanel.net> - 7.4.11-3
- EA-9390: Fix build with latest ea-brotli (v1.0.9)

* Wed Oct 21 2020 Daniel Muey <dan@cpanel.net> - 7.4.11-2
- ZC-7497: Reinstate `runselftest`

* Thu Oct 01 2020 Cory McIntire <cory@cpanel.net> - 7.4.11-1
- EA-9339: Update ea-php74 from v7.4.10 to v7.4.11

* Fri Sep 04 2020 Tim Mullin <tim@cpanel.net> - 7.4.10-2
- EA-9281: Update litespeed from upstream to 7.8

* Thu Sep 03 2020 Cory McIntire <cory@cpanel.net> - 7.4.10-1
- EA-9282: Update ea-php74 from v7.4.9 to v7.4.10

* Thu Aug 06 2020 Cory McIntire <cory@cpanel.net> - 7.4.9-1
- EA-9224: Update ea-php74 from v7.4.8 to v7.4.9

* Fri Jul 24 2020 Tim Mullin <tim@cpanel.net> - 7.4.8-2
- EA-9189: Update litespeed from upstream to 7.7

* Thu Jul 09 2020 Cory McIntire <cory@cpanel.net> - 7.4.8-1
- EA-9150: Update ea-php74 from v7.4.7 to v7.4.8

* Mon Jun 29 2020 Julian Brown <julian.brown@cpanel.net> - 7.4.7-2
- ZC-6967: Build on C8

* Fri Jun 12 2020 Cory McIntire <cory@cpanel.net> - 7.4.7-1
- EA-9109: Update ea-php74 from v7.4.6 to v7.4.7

* Wed Jun 10 2020 Tim Mullin <tim@cpanel.net> - 7.4.6-3
- EA-9087: Fix PHP version in DSO description

* Mon May 18 2020 Tim Mullin <tim@cpanel.net> - 7.4.6-2
- EA-9072: Revert new .user.ini search behavior

* Thu May 14 2020 Cory McIntire <cory@cpanel.net> - 7.4.6-1
- EA-9070: Update ea-php74 from v7.4.5 to v7.4.6

* Thu Apr 23 2020 Daniel Muey <dan@cpanel.net> - 7.4.5-3
- ZC-6649: Re-enable multibyte regex for 7.4

* Wed Apr 22 2020 Tim Mullin <tim@cpanel.net> - 7.4.5-2
- EA-9014: Build ea-php74 with jpeg support

* Thu Apr 16 2020 Cory McIntire <cory@cpanel.net> - 7.4.5-1
- EA-9007: Update ea-php74 from v7.4.2 to v7.4.5

* Thu Mar 26 2020 Julian Brown <julian.brown@cpanel.net> - 7.4.2-3
- ZC-6287: Add php_intl with ea-libicu for C6

* Mon Mar 09 2020 Daniel Muey <dan@cpanel.net> - 7.4.2-2
- ZC-6287: Add libzip to zip Requires for C6

* Wed Feb 05 2020 Daniel Muey <dan@cpanel.net> - 7.4.2-1
- EA-8867: Update ea-php74 from v7.4.1 to v7.4.2

* Tue Dec 24 2019 Dan Muey <dan@cpanel.net> - 7.4.1-1
- ZC-4640: Initial packaging
