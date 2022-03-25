%global debug_package %{nil}
%define st_pkg_assets %{_builddir}/%{name}-%{version}/%{name}

Name:           stellar-horizon
Version:        2.15.1
Release:        1%{?dist}
Summary:        stellar horizon server

License:        GPLv3
Source0:        stellar-packages.tar.gz
Source1:        https://github.com/stellar/go/archive/refs/tags/horizon-v%{version}.tar.gz

BuildRequires:  golang
BuildRequires:  systemd-rpm-macros
BuildRequires:  postgresql-server

Provides:       %{name} = %{version}

%description
Client-facing API server for the Stellar network. It acts as the interface between Stellar Core and
applications that want to access the Stellar network. It allows you to submit transactions to the network,
check the status of accounts, subscribe to event streams and more.

%prep

%setup -q -n %{name}-%{version}
%setup -q -b 1 -T -D -n  go-horizon-v%{version}

%build
# the onliner bellow do the same as the next two rows
# go build --mod mod -ldflags="-s -w" -o %{name} services/horizon/*.go
# but I want to be sure that the tests use the same source code
go mod vendor
go build --mod vendor -ldflags="-s -w" -o %{name} services/horizon/*.go

%install
install -Dpm 0755 %{name}                                      %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 %{st_pkg_assets}/rpm/%{name}.sysconfig       %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -Dpm 0644 %{st_pkg_assets}/rpm/%{name}.service         %{buildroot}%{_unitdir}/%{name}.service

%check
export PGDATA=`mktemp -d`
initdb --locale=en_US.UTF-8 -E UTF8 -U postgres
echo -e "logging_collector=off\nlog_min_messages=INFO\nunix_socket_directories='$PGDATA'\n" >> $PGDATA/postgresql.conf
pg_ctl -l $PGDATA/log.txt start
sleep 1
go test -count=1 ./services/horizon/... || pg_ctl stop
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
- init horizon rpm
