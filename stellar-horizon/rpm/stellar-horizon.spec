%global debug_package %{nil}

Name: stellar-horizon
Version: 2.15.1
Release: 4%{?dist}
Summary: Client-facing API server for the Stellar network

License: Apache 2.0
Source0: {{{ git_dir_pack }}}
Source1: https://github.com/stellar/go/archive/refs/tags/horizon-v%{version}.tar.gz

Requires: user(stellar)
Requires: group(stellar)

BuildRequires: git >= 2.0
BuildRequires: golang
BuildRequires: systemd-rpm-macros
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires: rh-postgresql12-postgresql-server
%else
BuildRequires: postgresql-server >= 10.0
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
go mod vendor
go build --mod vendor -ldflags="-s -w" -o %{name} services/horizon/*.go

%install
install -Dpm 0755 %{name} %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.service   %{buildroot}%{_unitdir}/%{name}.service

%check
%if 0%{?rhel} && 0%{?rhel} == 7
    source /opt/rh/rh-postgresql12/enable
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
* Wed Mar 23 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- init stellar-horizon rpm
