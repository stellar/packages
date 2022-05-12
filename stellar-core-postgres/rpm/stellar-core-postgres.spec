%global debug_package %{nil}

Name: stellar-core-postgres
Version: 0.0.9
Release: 1%{?dist}
Summary: Postgresql configuration for the Stellar Core
License: Apache 2.0
Source0: {{{ git_dir_pack }}}

BuildRequires: systemd-rpm-macros
Requires: stellar-core
Requires: postgresql-server

%description
The stellar-core-postgres package contains config files for postgres core db and stellar-core.

%prep
{{{ git_dir_setup_macro }}}

%install
install -d %{buildroot}%{_libexecdir}/stellar/

install -p -m 644 -D dist/%{name}-public.cfg            %{buildroot}%{_sysconfdir}/stellar/%{name}-public.cfg
install -p -m 644 -D dist/unit.postgresql.core.conf     %{buildroot}%{_sysconfdir}/systemd/system/postgresql@core.service.d/custom.conf
install -p -m 644 -D dist/unit.stellar-core.public.conf %{buildroot}%{_sysconfdir}/systemd/system/stellar-core@public.service.d/custom.conf
install -p -m 644 -D dist/postgres.16GB.cloud.conf      %{buildroot}%{_datadir}/stellar/postgres.16GB.cloud.conf
install -p -m 755 -D dist/libexec.init-db-core.sh       %{buildroot}%{_libexecdir}/stellar/init-db-core
install -p -m 755 -D dist/libexec.init-stellar-core.sh  %{buildroot}%{_libexecdir}/stellar/init-stellar-core

%files
%{_sysconfdir}/stellar/%{name}-public.cfg
%{_sysconfdir}/systemd/system/postgresql@core.service.d/custom.conf
%{_sysconfdir}/systemd/system/stellar-core@public.service.d/custom.conf
%{_datadir}/stellar/postgres.16GB.cloud.conf
%{_libexecdir}/stellar/init-db-core
%{_libexecdir}/stellar/init-stellar-core

%post
%systemd_post postgresql@core.service
%systemd_post stellar-core@public.service

%preun
%systemd_preun stellar-core@public.service
%systemd_preun postgresql@core.service

%postun
%systemd_postun_with_restart stellar-core@public.service

%changelog
* Sun Apr 10 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- init stellar-core-postgres rpm
