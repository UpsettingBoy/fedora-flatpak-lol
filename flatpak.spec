%global bubblewrap_version 0.1.8
%global ostree_version 2017.6

Name:           flatpak
Version:        0.9.5
Release:        1%{?dist}
Summary:        Application deployment framework for desktop apps

Group:          Development/Tools
License:        LGPLv2+
URL:            http://flatpak.org/
Source0:        https://github.com/flatpak/flatpak/releases/download/%{version}/%{name}-%{version}.tar.xz

BuildRequires:  pkgconfig(fuse)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(gobject-introspection-1.0) >= 1.40.0
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libarchive) >= 2.8.0
BuildRequires:  pkgconfig(libelf) >= 0.8.12
BuildRequires:  pkgconfig(libsoup-2.4)
BuildRequires:  pkgconfig(libxml-2.0) >= 2.4
BuildRequires:  pkgconfig(ostree-1) >= %{ostree_version}
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  pkgconfig(libseccomp)
BuildRequires:  pkgconfig(xau)
BuildRequires:  bubblewrap >= %{bubblewrap_version}
BuildRequires:  docbook-dtds
BuildRequires:  docbook-style-xsl
BuildRequires:  gpgme-devel
BuildRequires:  intltool
BuildRequires:  libattr-devel
BuildRequires:  libcap-devel
BuildRequires:  libdwarf-devel
BuildRequires:  systemd
BuildRequires:  /usr/bin/xmlto
BuildRequires:  /usr/bin/xsltproc

# Crashes with older kernels (the bug being introduced in 4.0.2), without the
# upstream fixes in this version.
Requires:       kernel >= 4.0.4-202

# Needed for the document portal.
Requires:       /usr/bin/fusermount

Requires:       bubblewrap >= %{bubblewrap_version}
Requires:       ostree-libs%{?_isa} >= %{ostree_version}

# Remove in F27.
Provides:       xdg-app = %{version}-%{release}
Obsoletes:      xdg-app <= 0.5.2-2

%description
flatpak is a system for building, distributing and running sandboxed desktop
applications on Linux. See https://wiki.gnome.org/Projects/SandboxedApps for
more information.

%package builder
Summary:        Build helper for %{name}
Group:          Development/Tools
License:        LGPLv2+
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       /usr/bin/bzip2
Requires:       /usr/bin/bzr
Requires:       /usr/bin/git
Requires:       /usr/bin/patch
Requires:       /usr/bin/strip
Requires:       /usr/bin/tar
Requires:       /usr/bin/unzip
# For debuginfo.
Requires:       /usr/bin/eu-strip
# Remove in F27.
Provides:       xdg-app-builder = %{version}-%{release}
Obsoletes:      xdg-app-builder <= 0.5.2-2

%description builder
flatpak-builder is a tool that makes it easy to build applications and their
dependencies by automating the configure && make && make install steps.

%package devel
Summary:        Development files for %{name}
Group:          Development/Libraries
License:        LGPLv2+
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
# Remove in F27.
Provides:       xdg-app-devel%{?_isa} = %{version}-%{release}
Obsoletes:      xdg-app-devel <= 0.5.2-2

%description devel
This package contains the pkg-config file and development headers for %{name}.

%package libs
Summary:        Libraries for %{name}
Group:          Development/Libraries
License:        LGPLv2+
Requires:       bubblewrap >= %{bubblewrap_version}
Requires:       ostree%{?_isa} >= %{ostree_version}
# Remove in F27.
Provides:       xdg-app-libs%{?_isa} = %{version}-%{release}
Obsoletes:      xdg-app-libs <= 0.5.2-2

%description libs
This package contains libflatpak.


%prep
%setup -q


%build
(if ! test -x configure; then NOCONFIGURE=1 ./autogen.sh; CONFIGFLAGS=--enable-gtk-doc; fi;
 # User namespace support is sufficient.
 %configure --with-dwarf-header=%{_includedir}/libdwarf --with-priv-mode=none \
            --with-system-bubblewrap --enable-docbook-docs $CONFIGFLAGS)
%make_build V=1


%install
%make_install
install -pm 644 NEWS README.md %{buildroot}/%{_pkgdocdir}
# The system repo is not installed by the flatpak build system.
install -d %{buildroot}%{_localstatedir}/lib/flatpak
install -d %{buildroot}%{_sysconfdir}/flatpak/remotes.d
rm -f %{buildroot}%{_libdir}/libflatpak.la
%find_lang %{name}


%post
# Create an (empty) system-wide repo.
flatpak remote-list --system &> /dev/null || :

%post libs -p /sbin/ldconfig


%postun libs -p /sbin/ldconfig


%files -f %{name}.lang
%license COPYING
# Comply with the packaging guidelines about not mixing relative and absolute
# paths in doc.
%doc %{_pkgdocdir}
%{_bindir}/flatpak
%{_bindir}/flatpak-bisect
%{_datadir}/bash-completion
%{_datadir}/dbus-1/interfaces/org.freedesktop.Flatpak.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.portal.Documents.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.impl.portal.PermissionStore.xml
%{_datadir}/dbus-1/services/org.freedesktop.Flatpak.service
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.PermissionStore.service
%{_datadir}/dbus-1/services/org.freedesktop.portal.Documents.service
%{_datadir}/dbus-1/system-services/org.freedesktop.Flatpak.SystemHelper.service
# Co-own directory.
%{_datadir}/gdm/env.d
%{_datadir}/%{name}
%{_datadir}/polkit-1/actions/org.freedesktop.Flatpak.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.Flatpak.rules
%{_libexecdir}/flatpak-dbus-proxy
%{_libexecdir}/flatpak-session-helper
%{_libexecdir}/flatpak-system-helper
%{_libexecdir}/xdg-document-portal
%{_libexecdir}/xdg-permission-store
%dir %{_localstatedir}/lib/flatpak
%{_mandir}/man1/%{name}*.1*
%{_mandir}/man5/%{name}-metadata.5*
%{_mandir}/man5/flatpak-flatpakref.5*
%{_mandir}/man5/flatpak-flatpakrepo.5*
%{_mandir}/man5/flatpak-installation.5*
%{_mandir}/man5/flatpak-manifest.5*
%{_mandir}/man5/flatpak-remote.5*
%exclude %{_mandir}/man1/flatpak-builder.1*
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.Flatpak.SystemHelper.conf
%{_sysconfdir}/flatpak/remotes.d
%{_sysconfdir}/profile.d/flatpak.sh
%{_unitdir}/flatpak-system-helper.service
%{_userunitdir}/flatpak-session-helper.service
%{_userunitdir}/xdg-document-portal.service
%{_userunitdir}/xdg-permission-store.service
# Co-own directory.
%{_userunitdir}/dbus.service.d

%files builder
%{_bindir}/flatpak-builder
%{_mandir}/man1/flatpak-builder.1*

%files devel
%{_datadir}/gir-1.0/Flatpak-1.0.gir
%{_datadir}/gtk-doc/
%{_includedir}/%{name}/
%{_libdir}/libflatpak.so
%{_libdir}/pkgconfig/%{name}.pc

%files libs
%license COPYING
%{_libdir}/girepository-1.0/Flatpak-1.0.typelib
%{_libdir}/libflatpak.so.*


%changelog
* Sat Jun 10 2017 David King <amigadave@amigadave.com> - 0.9.5-1
- Update to 0.9.5 (#1460437)

* Tue May 23 2017 David King <amigadave@amigadave.com> - 0.9.4-1
- Update to 0.9.4 (#1454750)

* Mon Apr 24 2017 David King <amigadave@amigadave.com> - 0.9.3-1
- Update to 0.9.3

* Fri Apr 07 2017 David King <amigadave@amigadave.com> - 0.9.2-2
- Add eu-strip dependency for flatpak-builder

* Wed Apr 05 2017 Kalev Lember <klember@redhat.com> - 0.9.2-1
- Update to 0.9.2

* Wed Mar 15 2017 Kalev Lember <klember@redhat.com> - 0.9.1-1
- Update to 0.9.1

* Fri Mar 10 2017 Kalev Lember <klember@redhat.com> - 0.8.4-1
- Update to 0.8.4

* Sun Feb 19 2017 David King <amigadave@amigadave.com> - 0.8.3-3
- Make flatpak-builder require bzip2 (#1424857)

* Wed Feb 15 2017 Kalev Lember <klember@redhat.com> - 0.8.3-2
- Avoid pulling in all of ostree and only depend on ostree-libs subpackage

* Tue Feb 14 2017 Kalev Lember <klember@redhat.com> - 0.8.3-1
- Update to 0.8.3

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 27 2017 Kalev Lember <klember@redhat.com> - 0.8.2-1
- Update to 0.8.2

* Wed Jan 18 2017 David King <amigadave@amigadave.com> - 0.8.1-1
- Update to 0.8.1

* Tue Dec 20 2016 Kalev Lember <klember@redhat.com> - 0.8.0-1
- Update to 0.8.0

* Tue Nov 29 2016 David King <amigadave@amigadave.com> - 0.6.14-2
- Add a patch to fix a GNOME Software crash
- Silence repository listing during post

* Tue Nov 29 2016 Kalev Lember <klember@redhat.com> - 0.6.14-1
- Update to 0.6.14

* Wed Oct 26 2016 David King <amigadave@amigadave.com> - 0.6.13-2
- Add empty /etc/flatpak/remotes.d

* Tue Oct 25 2016 David King <amigadave@amigadave.com> - 0.6.13-1
- Update to 0.6.13

* Thu Oct 06 2016 David King <amigadave@amigadave.com> - 0.6.12-1
- Update to 0.6.12

* Tue Sep 20 2016 Kalev Lember <klember@redhat.com> - 0.6.11-1
- Update to 0.6.11
- Set minimum ostree and bubblewrap versions

* Mon Sep 12 2016 David King <amigadave@amigadave.com> - 0.6.10-1
- Update to 0.6.10

* Tue Sep 06 2016 David King <amigadave@amigadave.com> - 0.6.9-2
- Look for bwrap in PATH

* Thu Aug 25 2016 David King <amigadave@amigadave.com> - 0.6.9-1
- Update to 0.6.9

* Mon Aug 01 2016 David King <amigadave@amigadave.com> - 0.6.8-1
- Update to 0.6.8 (#1361823)

* Thu Jul 21 2016 David King <amigadave@amigadave.com> - 0.6.7-2
- Use system bubblewrap

* Fri Jul 01 2016 David King <amigadave@amigadave.com> - 0.6.7-1
- Update to 0.6.7

* Thu Jun 23 2016 David King <amigadave@amigadave.com> - 0.6.6-1
- Update to 0.6.6

* Fri Jun 10 2016 David King <amigadave@amigadave.com> - 0.6.5-1
- Update to 0.6.5

* Wed Jun 01 2016 David King <amigadave@amigadave.com> - 0.6.4-1
- Update to 0.6.4

* Tue May 31 2016 David King <amigadave@amigadave.com> - 0.6.3-1
- Update to 0.6.3
- Move bwrap to main package

* Tue May 24 2016 David King <amigadave@amigadave.com> - 0.6.2-1
- Rename from xdg-app to flatpak (#1337434)
