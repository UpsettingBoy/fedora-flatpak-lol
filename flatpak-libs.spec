%global bubblewrap_version 0.5.0
%global glib_version 2.46.0
%global libcurl_version 7.29.0
%global ostree_version 2020.8
%define _unpackaged_files_terminate_build 0

Name:           flatpak-libs
Version:        1.15.0
Release:        1.lol%{?dist}
Summary:        Flatpak libs

License:        LGPLv2+
URL:            http://flatpak.org/
Source0:        https://github.com/flatpak/flatpak/releases/download/%{version}/flatpak-%{version}.tar.xz

# https://github.com/flatpak/flatpak/pull/5079
# Patch0:         flatpak-allow-modify_ldt.patch

BuildRequires:  pkgconfig(appstream)
BuildRequires:  pkgconfig(dconf)
BuildRequires:  pkgconfig(fuse)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0) >= %{glib_version}
BuildRequires:  pkgconfig(gobject-introspection-1.0) >= 1.40.0
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libarchive) >= 2.8.0
BuildRequires:  pkgconfig(libseccomp)
BuildRequires:  pkgconfig(libcurl) >= %{libcurl_version}
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(libxml-2.0) >= 2.4
BuildRequires:  pkgconfig(libzstd) >= 0.8.1
BuildRequires:  pkgconfig(malcontent-0)
BuildRequires:  pkgconfig(ostree-1) >= %{ostree_version}
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  pkgconfig(xau)
BuildRequires:  autoconf automake libtool
BuildRequires:  bison
BuildRequires:  bubblewrap >= %{bubblewrap_version}
BuildRequires:  docbook-dtds
BuildRequires:  docbook-style-xsl
BuildRequires:  gettext-devel
BuildRequires:  gpgme-devel
BuildRequires:  gtk-doc
BuildRequires:  libcap-devel
BuildRequires:  python3-pyparsing
BuildRequires:  systemd
BuildRequires:  systemd-rpm-macros
BuildRequires:  /usr/bin/xdg-dbus-proxy
BuildRequires:  /usr/bin/xmlto
BuildRequires:  /usr/bin/xsltproc
BuildRequires:  selinux-policy-devel
BuildRequires:  glib2%{?_isa} >= %{glib_version}
BuildRequires:  libcurl%{?_isa} >= %{libcurl_version}

%{?sysusers_requires_compat}

Requires:       bubblewrap >= %{bubblewrap_version}
Requires:       ostree%{?_isa} >= %{ostree_version}

%description
This package contains libflatpak.

%prep
%autosetup -p1 -n flatpak-%{version}

%build
rm configure
(if ! test -x configure; then NOCONFIGURE=1 ./autogen.sh; CONFIGFLAGS=--enable-gtk-doc; fi;
 # Generate consistent IDs between runs to avoid multilib problems.
 export XMLTO_FLAGS="--stringparam generate.consistent.ids=1"
 %configure \
            --enable-docbook-docs \
            --enable-installed-tests \
            --enable-selinux-module \
            --with-curl \
            --with-priv-mode=none \
            --with-system-bubblewrap \
            --with-system-dbus-proxy \
            $CONFIGFLAGS)
%make_build V=1

%install
%make_install
rm -f %{buildroot}%{_libdir}/libflatpak.la

%files
%license COPYING
%{_libdir}/girepository-1.0/Flatpak-1.0.typelib
%{_libdir}/libflatpak.so.*

%changelog
* Thu Sep 29 2022 Jero Sanchez <jeronimosg@hotmail.es> - 1.14.0-1.lol
- Update to Flatpak 1.14.0 + allow modify_ldt
