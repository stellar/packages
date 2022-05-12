%global debug_package %{nil}
%define system_name stellar

Name: %{system_name}-system
Version: 0.0.6
Release: 2%{?dist}
Summary: system configuration for the Stellar infra
License: Apache 2.0
Source0: {{{ git_dir_pack }}}

BuildRequires: systemd-rpm-macros
Requires(pre): shadow-utils

%if 0%{?rhel} && 0%{?rhel} == 7
# rhel7 uses rpm-4.11
# Requires: %{name}-selinux
%else
# starting with rpm-4.13, RPM is able to process boolean expressions
Requires: (%{name}-selinux if selinux-policy-targeted)
%endif

Provides: user(%{system_name})
Provides: group(%{system_name})

%description
The stellar-system package contains a set of important system configuration and
setup files for Stellar infra.

%package selinux
Summary:        SELinux policy module for %{name}
License:        LGPLv2+
BuildRequires:  selinux-policy
BuildRequires:  selinux-policy-devel
BuildArch:      noarch
%{?selinux_requires}

%description selinux
This package contains the SELinux policy module for %{name}.

%prep
{{{ git_dir_setup_macro }}}

%build
make -f /usr/share/selinux/devel/Makefile
bzip2 -9 %{name}.pp

%install
install -p -m644 -D dist/sysusers.d/%{system_name}.conf %{buildroot}%{_sysusersdir}/%{system_name}.conf
install -p -m644 -D dist/tmpfiles.d/%{system_name}.conf %{buildroot}%{_tmpfilesdir}/%{system_name}.conf
install -D -m 644 %{name}.pp.bz2                 %{buildroot}%{_datadir}/selinux/packages/%{name}.pp.bz2

%files
%{_sysusersdir}/%{system_name}.conf
%{_tmpfilesdir}/%{system_name}.conf

%files selinux
%{_datadir}/selinux/packages/%{name}.pp.bz2

%pre
getent group '%{system_name}' >/dev/null || groupadd -r '%{system_name}'
getent passwd '%{system_name}' >/dev/null || \
    useradd -m -r -g '%{system_name}' -d '/var/lib/%{system_name}' -s '/sbin/nologin' -c '%{system_name} system user' '%{system_name}'
# -m, --create-home Create the user's home directory

%post
systemd-sysusers || :
systemd-tmpfiles --create &>/dev/null || :

%pre selinux
%selinux_relabel_pre -s %{selinuxtype}

%post selinux
%selinux_modules_install %{_datadir}/selinux/packages/%{name}.pp.bz2

%postun selinux
if [ $1 -eq 0 ]; then
    %selinux_modules_uninstall %{_datadir}/selinux/packages/%{name}.pp.bz2
fi

%changelog
* Sun Apr 03 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- init stellar-system rpm
