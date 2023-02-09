%global debug_package %{nil}

Name: stellar-horizon
Version: 2.24.0
Release: 1%{?dist}
Summary: Client-facing API server for the Stellar network

License: Apache 2.0
Source0: {{{ git_dir_pack }}}
Source1: https://github.com/stellar/go/archive/refs/tags/horizon-v%{version}.tar.gz

Requires: user(stellar)
Requires: group(stellar)

BuildRequires: git >= 2.0
BuildRequires: golang >= 1.18
BuildRequires: systemd-rpm-macros
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires: rh-postgresql13-postgresql-server
%else
BuildRequires: postgresql-server >= 13.0
%endif

Provides: %{name} = %{version}

%description
Client-facing API server for the Stellar network. It acts as the interface between Stellar Core and
applications that want to access the Stellar network. It allows you to submit transactions to the network,
check the status of accounts, subscribe to event streams and more.

%prep
{{{ git_dir_setup_macro }}}
%setup -q -b 1 -T -D -n go-horizon-v%{version}

%build
# the onliner bellow do the same as the next two rows
# go build --mod mod -ldflags="-s -w" -o %{name} services/horizon/*.go
# but we want to be sure that the tests use the same source code
# linkmode=external related to he rpm>=4.14.0 and build-id
# one way is to use gccgo instead of go build, and the other way is to add -ldflags=-linkmode=external flag to go build.
go mod vendor
go build --mod vendor -ldflags="-s -w -linkmode=external" -o %{name} services/horizon/*.go

%install
%{__install} -Dpm 0755 %{name} %{buildroot}%{_bindir}/%{name}
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.service   %{buildroot}%{_unitdir}/%{name}.service

%check
%if 0%{?rhel} && 0%{?rhel} == 7
    source /opt/rh/rh-postgresql13/enable
%endif
# make clean db in tmp dir, and run go test.
export PGDATA=`mktemp -d`
initdb --no-locale -E UTF8 -U postgres
echo -e "logging_collector=off\nlog_min_messages=INFO\nunix_socket_directories='$PGDATA'\n" >> $PGDATA/postgresql.conf
pg_ctl -l $PGDATA/log.txt start
sleep 1
go test -count=1 ./services/horizon/...
pg_ctl stop

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%files
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%changelog
* Thu Feb 9 2023 Anatolii Vorona <vorona.tolik@gmail.com>
- update Horizon v2.24.0

* Thu Dec 8 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update Horizon v2.23.1

* Tue Nov 1 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update Horizon v2.22.1

* Thu Oct 13 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- update Horizon v2.21.0

* Wed Mar 23 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- init stellar-horizon rpm
