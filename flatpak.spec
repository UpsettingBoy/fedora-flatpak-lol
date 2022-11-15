%global bubblewrap_version 0.5.0
%global libcurl_version 7.29.0
%global ostree_version 2020.8

Name:           flatpak
Version:        1.15.0
Release:        1.lol%{?dist}
Summary:        Application deployment framework for desktop apps

License:        LGPLv2+
URL:            http://flatpak.org/
Source0:        https://github.com/flatpak/flatpak/releases/download/%{version}/%{name}-%{version}.tar.xz

%if 0%{?fedora}
# Add Fedora flatpak repositories
Source1:        flatpak-add-fedora-repos.service
%endif

# https://github.com/flatpak/flatpak/pull/5079
# No need for patch anymore
# Patch0:         flatpak-allow-modify_ldt.patch

BuildRequires:  pkgconfig(appstream-glib)

BuildRequires:  pkgconfig(appstream) >= 0.12.0
BuildRequires:  pkgconfig(dconf)
BuildRequires:  pkgconfig(fuse)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(gobject-introspection-1.0) >= 1.40.0
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libcurl) >= %{libcurl_version}
BuildRequires:  pkgconfig(libarchive) >= 2.8.0
BuildRequires:  pkgconfig(libseccomp)
BuildRequires:  pkgconfig(libsoup-2.4)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(libxml-2.0) >= 2.4
BuildRequires:  pkgconfig(libzstd) >= 0.8.1
BuildRequires:  pkgconfig(malcontent-0)
BuildRequires:  pkgconfig(ostree-1) >= %{ostree_version}
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  pkgconfig(xau)
BuildRequires:  bison
BuildRequires:  bubblewrap >= %{bubblewrap_version}
BuildRequires:  docbook-dtds
BuildRequires:  docbook-style-xsl
BuildRequires:  gettext
BuildRequires:  gpgme-devel
BuildRequires:  libcap-devel
BuildRequires:  python3-pyparsing
BuildRequires:  systemd
BuildRequires:  /usr/bin/xdg-dbus-proxy
BuildRequires:  /usr/bin/xmlto
BuildRequires:  /usr/bin/xsltproc

Requires:       bubblewrap >= %{bubblewrap_version}
Requires:       librsvg2%{?_isa}
Requires:       ostree-libs%{?_isa} >= %{ostree_version}
Requires:       /usr/bin/xdg-dbus-proxy
# https://fedoraproject.org/wiki/SELinux/IndependentPolicy
Requires:       (flatpak-selinux = %{?epoch:%{epoch}:}%{version}-%{release} if selinux-policy-targeted)
Requires:       %{name}-session-helper%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Recommends:     p11-kit-server

# Make sure the document portal is installed
%if 0%{?fedora} || 0%{?rhel} > 7
Recommends:     xdg-desktop-portal > 0.10
%else
Requires:       xdg-desktop-portal > 0.10
%endif

%description
flatpak is a system for building, distributing and running sandboxed desktop
applications on Linux. See https://wiki.gnome.org/Projects/SandboxedApps for
more information.

%package devel
Summary:        Development files for %{name}
License:        LGPLv2+
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
This package contains the pkg-config file and development headers for %{name}.

%package libs
Summary:        Libraries for %{name}
License:        LGPLv2+
Requires:       bubblewrap >= %{bubblewrap_version}
Requires:       ostree%{?_isa} >= %{ostree_version}
Requires(pre):  /usr/sbin/useradd

%description libs
This package contains libflatpak.

%package selinux
Summary:        SELinux policy module for %{name}
License:        LGPLv2+
BuildRequires:  selinux-policy
BuildRequires:  selinux-policy-devel
BuildRequires:  make
BuildArch:      noarch
%{?selinux_requires}

%description selinux
This package contains the SELinux policy module for %{name}.

%package session-helper
Summary:        User D-Bus service used by %{name} and others
License:        LGPLv2+
Conflicts:      flatpak < 1.4.1-2
Requires:       systemd

%description session-helper
This package contains the org.freedesktop.Flatpak user D-Bus service
that's used by %{name} and other packages.

%package tests
Summary:        Tests for %{name}
License:        LGPLv2+
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       %{name}-session-helper%{?_isa} = %{version}-%{release}
Requires:       bubblewrap >= %{bubblewrap_version}
Requires:       ostree%{?_isa} >= %{ostree_version}

%description tests
This package contains installed tests for %{name}.


%prep
%autosetup -p1


%build
(if ! test -x configure; then NOCONFIGURE=1 ./autogen.sh; fi;
 # Generate consistent IDs between runs to avoid multilib problems.
 export XMLTO_FLAGS="--stringparam generate.consistent.ids=1"
 %configure \
            --enable-docbook-docs \
            --enable-installed-tests \
            --enable-selinux-module \
            --with-priv-mode=none \
            --with-system-bubblewrap \
            --with-system-dbus-proxy \
            )
%make_build V=1


%install
%make_install
install -pm 644 NEWS README.md %{buildroot}/%{_pkgdocdir}
# The system repo is not installed by the flatpak build system.
install -d %{buildroot}%{_localstatedir}/lib/flatpak
install -d %{buildroot}%{_sysconfdir}/flatpak/remotes.d
rm -f %{buildroot}%{_libdir}/libflatpak.la

%if 0%{?fedora}
install -D -t %{buildroot}%{_unitdir} %{SOURCE1}
%endif

%find_lang %{name}

%pre
getent group flatpak >/dev/null || groupadd -r flatpak
getent passwd flatpak >/dev/null || \
    useradd -r -g flatpak -d / -s /sbin/nologin \
     -c "User for flatpak system helper" flatpak
exit 0


%if 0%{?fedora}
%post
%systemd_post flatpak-add-fedora-repos.service
%endif


%post selinux
%selinux_modules_install %{_datadir}/selinux/packages/flatpak.pp.bz2


%if 0%{?fedora}
%preun
%systemd_preun flatpak-add-fedora-repos.service
%endif


%if 0%{?fedora}
%postun
%systemd_postun_with_restart flatpak-add-fedora-repos.service
%endif


%postun selinux
if [ $1 -eq 0 ]; then
    %selinux_modules_uninstall %{_datadir}/selinux/packages/flatpak.pp.bz2
fi


%files -f %{name}.lang
%license COPYING
# Comply with the packaging guidelines about not mixing relative and absolute
# paths in doc.
%doc %{_pkgdocdir}
%{_bindir}/flatpak
%{_bindir}/flatpak-bisect
%{_bindir}/flatpak-coredumpctl
%{_datadir}/bash-completion
%{_datadir}/dbus-1/interfaces/org.freedesktop.portal.Flatpak.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.Flatpak.Authenticator.xml
%{_datadir}/dbus-1/services/org.flatpak.Authenticator.Oci.service
%{_datadir}/dbus-1/services/org.freedesktop.portal.Flatpak.service
%{_datadir}/dbus-1/system-services/org.freedesktop.Flatpak.SystemHelper.service
%{_datadir}/fish/
%{_datadir}/%{name}
%{_datadir}/polkit-1/actions/org.freedesktop.Flatpak.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.Flatpak.rules
%{_datadir}/zsh/site-functions
%{_libexecdir}/flatpak-oci-authenticator
%{_libexecdir}/flatpak-portal
%{_libexecdir}/flatpak-system-helper
%{_libexecdir}/flatpak-validate-icon
%{_libexecdir}/revokefs-fuse
%dir %{_localstatedir}/lib/flatpak
%{_mandir}/man1/%{name}*.1*
%{_mandir}/man5/%{name}-metadata.5*
%{_mandir}/man5/flatpak-flatpakref.5*
%{_mandir}/man5/flatpak-flatpakrepo.5*
%{_mandir}/man5/flatpak-installation.5*
%{_mandir}/man5/flatpak-remote.5*
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.Flatpak.SystemHelper.conf
%dir %{_sysconfdir}/flatpak
%{_sysconfdir}/flatpak/remotes.d
%{_sysconfdir}/profile.d/flatpak.sh
%{_sysusersdir}/flatpak.conf
%{_unitdir}/flatpak-system-helper.service
%{_userunitdir}/flatpak-oci-authenticator.service
%{_userunitdir}/flatpak-portal.service
%{_systemd_system_env_generator_dir}/60-flatpak-system-only
%{_systemd_user_env_generator_dir}/60-flatpak

%if 0%{?fedora}
%{_unitdir}/flatpak-add-fedora-repos.service
%endif

%files devel
%{_datadir}/gir-1.0/Flatpak-1.0.gir
%{_includedir}/%{name}/
%{_libdir}/libflatpak.so
%{_libdir}/pkgconfig/%{name}.pc

%files libs
%license COPYING
%{_libdir}/girepository-1.0/Flatpak-1.0.typelib
%{_libdir}/libflatpak.so.*

%files selinux
%{_datadir}/selinux/packages/flatpak.pp.bz2
%{_datadir}/selinux/devel/include/contrib/flatpak.if

%files session-helper
%license COPYING
%{_datadir}/dbus-1/interfaces/org.freedesktop.Flatpak.xml
%{_datadir}/dbus-1/services/org.freedesktop.Flatpak.service
%{_libexecdir}/flatpak-session-helper
%{_userunitdir}/flatpak-session-helper.service

%files tests
%{_datadir}/installed-tests
%{_libexecdir}/installed-tests

%changelog
* Thu Sep 29 2022 Jero Sanchez <jeronimosg@hotmail.es> - 1.14.0-1.lol
- Update to Flatpak 1.14.0 + allow modify_ldt
