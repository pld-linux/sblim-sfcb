# TODO: PLDify init script
Summary:	Small Footprint CIM Broker
Summary(pl.UTF-8):	Lekki broker CIM
Name:		sblim-sfcb
Version:	1.4.9
Release:	5
License:	Eclipse Public License v1.0
Group:		Libraries
Source0:	http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2
# Source0-md5:	28021cdabc73690a94f4f9d57254ce30
Patch0:		%{name}-fix.patch
Patch1:		am.patch
Patch2:		%{name}-dont-inline.patch
Patch3:		gcc10.patch
URL:		http://sblim.sourceforge.net/
BuildRequires:	curl-devel >= 7.11.1
BuildRequires:	libstdc++-devel
BuildRequires:	openslp-devel
BuildRequires:	openssl-devel >= 0.9.7
BuildRequires:	pam-devel
BuildRequires:	rpmbuild(macros) >= 1.644
BuildRequires:	sblim-cmpi-devel
BuildRequires:	sblim-sfcCommon-devel >= 1.0.1
BuildRequires:	unzip
BuildRequires:	zlib-devel
Requires(post):	openssl-tools
Requires:	sblim-sfcCommon >= 1.0.1
Provides:	cimserver
Suggests:	sblim-sfcb-schema
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# libsfcCimXmlCodec needs trimws symbol exported from broker binary
# libsfcHttpAdapter needs fallback_ipv4 symbol exported from broker binary
%define		skip_post_check_so	libsfcCimXmlCodec\.so.* libsfcHttpAdapter\.so.*

%description
sfcb is a lightweight CIM daemon (aka CIMOM) that responds to CIM
client requests for system management data and/or performs system
management tasks. sfcb supports most of the standard CIM XML over
HTTP/HTTPS protocol. It is highly modular, allowing functionality to
be easily added, removed or customized for different management
applications. sfcb is specifically targeted for small embedded system
that do not have the available CPU, memory or disk resources to
support a full-blown enterprise-level CIMOM. That said, sfcb runs very
well on a regular Linux/Unix system and supports most of the functions
required by CIM clients to manage such the system. 

%description -l pl.UTF-8
sfcb to lekki demon CIM (CIMOM), odpowiadający na zapytania klientów
CIM dotyczące zarządzania systemem i/lub wykonujący zadania związane z
zarządzaniem systemem. sfcb obsługuje większość ze standardowego XML-a
CIM z użyciem protokołu HTTP/HTTPS. Jest wysoce modularny, umożliwia
łatwe dodawanie, usuwanie lub dostosowywanie funkcjonalności do
różnych zastosowań. sfcb jest przeznaczony zwłaszcza do małych
systemów wbudowanych, nie mających wystarczająco dużo mocy procesora,
pamięci czy zasobów dyskowych do obsługi pełnego CIMOM. Oznacza to, że
sfcb działa bardzo dobrze na zwykłych systemach Linux/Unix i obsługuje
większość funkcji wymaganych przez klientów CIM do zarządzania takimi
systemami.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
cd mofc
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
cd ..
%configure \
	SYSTEMDDIR=%{systemdunitdir} \
	--disable-debug \
	--enable-pam \
	--enable-slp \
	--enable-ssl \
	--enable-uds

%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{systemdunitdir},%{_libdir}/cmpi}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	initdir=/etc/rc.d/init.d

# libraries with no headers installed
%{__rm} $RPM_BUILD_ROOT%{_libdir}/sfcb/libsfc{BrokerCore,CimXmlCodec,FileRepository,HttpAdapter,InternalProvider}.so
# the same or dlopened modules
%{__rm} $RPM_BUILD_ROOT%{_libdir}/sfcb/*.la

# packaged as %doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/sfcb-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/sfcb/server.pem -o ! -f %{_sysconfdir}/sfcb/client.pem ]; then
	%{_datadir}/sfcb/genSslCert.sh %{_sysconfdir}/sfcb
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README
%attr(754,root,root) /etc/rc.d/init.d/sfcb
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/sfcb
%dir %{_sysconfdir}/sfcb
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sfcb/sfcb.cfg
%attr(755,root,root) %{_bindir}/sfcb*
%attr(755,root,root) %{_bindir}/wbemcat
%attr(755,root,root) %{_bindir}/xmltest
%attr(755,root,root) %{_sbindir}/sfcbd
%{systemdunitdir}/sblim-sfcb.service
%dir %{_libdir}/cmpi
%dir %{_libdir}/sfcb
# libs
%attr(755,root,root) %{_libdir}/sfcb/libsfcBrokerCore.so.*.*.*
%attr(755,root,root) %{_libdir}/sfcb/libsfcBrokerCore.so.0
%attr(755,root,root) %{_libdir}/sfcb/libsfcCimXmlCodec.so.*.*.*
%attr(755,root,root) %{_libdir}/sfcb/libsfcCimXmlCodec.so.0
%attr(755,root,root) %{_libdir}/sfcb/libsfcFileRepository.so.*.*.*
%attr(755,root,root) %{_libdir}/sfcb/libsfcFileRepository.so.0
%attr(755,root,root) %{_libdir}/sfcb/libsfcHttpAdapter.so.*.*.*
%attr(755,root,root) %{_libdir}/sfcb/libsfcHttpAdapter.so.0
%attr(755,root,root) %{_libdir}/sfcb/libsfcInternalProvider.so.*.*.*
%attr(755,root,root) %{_libdir}/sfcb/libsfcInternalProvider.so.0
# providers dlopened by libsfcBrokerCore
%attr(755,root,root) %{_libdir}/sfcb/libsfcBasicAuthentication.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcBasicPAMAuthentication.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcCertificateAuthentication.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcClassProvider.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcClassProviderGz.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcClassProviderMem.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcClassProviderSf.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcCustomLib.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcElementCapabilitiesProvider.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcIndCIMXMLHandler.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcInteropProvider.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcInteropServerProvider.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcObjectImplSwapI32toP32.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcProfileProvider.so*
%attr(755,root,root) %{_libdir}/sfcb/libsfcQualifierProvider.so*
# dlopened by libcimcclient (sblib-sfcc)
%attr(755,root,root) %{_libdir}/sfcb/libcimcClientSfcbLocal.so*
%dir %{_datadir}/sfcb
%attr(755,root,root) %{_datadir}/sfcb/genSslCert.sh
%attr(755,root,root) %{_datadir}/sfcb/getSchema.sh
%attr(755,root,root) %{_datadir}/sfcb/stageschema.sh
%{_datadir}/sfcb/*.mof
%{_datadir}/sfcb/default.reg
%dir /var/lib/sfcb
%dir /var/lib/sfcb/stage
%config %verify(not md5 mtime size) /var/lib/sfcb/stage/default.reg
%dir /var/lib/sfcb/stage/mofs
%config %verify(not md5 mtime size) /var/lib/sfcb/stage/mofs/indication.mof
%dir /var/lib/sfcb/stage/mofs/root
%dir /var/lib/sfcb/stage/mofs/root/interop
%config %verify(not md5 mtime size) /var/lib/sfcb/stage/mofs/root/interop/*.mof
%{_mandir}/man1/genSslCert.1*
%{_mandir}/man1/getSchema.1*
%{_mandir}/man1/sfcb*.1*
%{_mandir}/man1/wbemcat.1*
%{_mandir}/man1/xmltest.1*
