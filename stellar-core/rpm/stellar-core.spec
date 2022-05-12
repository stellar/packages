%global debug_package %{nil}
%define system_name stellar

Name: stellar-core
Version: 18.5.0
Release: 8%{?dist}
Summary: Stellar is a decentralized, federated peer-to-peer network

License: Apache 2.0
Source0: {{{ git_dir_pack }}}
Source1: https://github.com/stellar/stellar-core/archive/refs/tags/v%{version}.tar.gz#/stellar-core-v%{version}.tar.gz
# START: submodule sources
Source100: https://api.github.com/repos/chriskohlhoff/asio/tarball/b84e6c16b2ea907dbad94206b7510d85aafc0b42#/chriskohlhoff-asio-asio-1-18-1-0-gb84e6c1.tar.gz
Source101: https://api.github.com/repos/fmtlib/fmt/tarball/b6f4ceaed0a0a24ccf575fab6c56dd50ccf6f1a9#/fmtlib-fmt-8.1.1-0-gb6f4cea.tar.gz
Source102: https://api.github.com/repos/gabime/spdlog/tarball/eb3220622e73a4889eee355ffa37972b3cac3df5#/gabime-spdlog-v1.9.2-0-geb32206.tar.gz
Source103: https://api.github.com/repos/stellar/libsodium/tarball/4f5e89fa84ce1d178a6765b8b46f2b6f91216677#/stellar-libsodium-1.0.18-0-g4f5e89f.tar.gz
Source104: https://api.github.com/repos/stellar/medida/tarball/361443a1e0addcde9b6645105ba0064b6c4f667b#/stellar-medida-361443a.tar.gz
Source105: https://api.github.com/repos/stellar/tracy/tarball/7c74f6eb094d29e6b23ba670686c3597e1e96b96#/stellar-tracy-v0.6.3-2048-g7c74f6e.tar.gz
Source106: https://api.github.com/repos/USCiLab/cereal/tarball/02eace19a99ce3cd564ca4e379753d69af08c2c8#/USCiLab-cereal-v1.3.0-0-g02eace1.tar.gz
Source107: https://api.github.com/repos/xdrpp/xdrpp/tarball/9fd7ca222bb26337e1443c67b18fbc5019962884#/xdrpp-xdrpp-9fd7ca2.tar.gz

# END: submodule sources
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires: llvm-toolset-7.0-clang
BuildRequires: devtoolset-8-gcc-c++
BuildRequires: rh-postgresql12-postgresql-devel, rh-postgresql12-postgresql-server
%else
BuildRequires: clang >= 10
BuildRequires: gcc-c++ >= 8
BuildRequires: postgresql-devel, postgresql-server
%endif

Requires: user(stellar)
Requires: group(stellar)

BuildRequires: automake
BuildRequires: bison
BuildRequires: flex
BuildRequires: git
BuildRequires: hostname
BuildRequires: libtool
BuildRequires: libunwind-devel
BuildRequires: parallel
BuildRequires: systemd-rpm-macros

Provides: %{name} = %{version}

%description
Stellar is a decentralized, federated peer-to-peer network that allows people to send payments in any asset
anywhere in the world instantaneously, and with minimal fee. Stellar-core is the core component of this network.
Stellar-core is a C++ implementation of the Stellar Consensus Protocol configured to construct a chain of ledgers
that are guaranteed to be in agreement across all the participating nodes at all times.

%prep
{{{ git_dir_setup_macro }}}
%setup -q -b 1 -T -D -n %{name}-%{version}
sed -i "s|\x25\x25VERSION\x25\x25|%{version}-%{release}|" src/main/StellarCoreVersion.cpp.in
git init
git add -N .
# START: submodules setup
tar -zxf  %{SOURCE100} --strip-components 1 -C lib/asio/
tar -zxf  %{SOURCE101} --strip-components 1 -C lib/fmt/
tar -zxf  %{SOURCE102} --strip-components 1 -C lib/spdlog/
tar -zxf  %{SOURCE103} --strip-components 1 -C lib/libsodium/
tar -zxf  %{SOURCE104} --strip-components 1 -C lib/libmedida/
tar -zxf  %{SOURCE105} --strip-components 1 -C lib/tracy/
tar -zxf  %{SOURCE106} --strip-components 1 -C lib/cereal/
tar -zxf  %{SOURCE107} --strip-components 1 -C lib/xdrpp/

# END: submodules setup
./autogen.sh

%build
%if 0%{?rhel} && 0%{?rhel} == 7
    LDFLAGS=-Wl,-rpath,%{_datadir}/%{system_name}/lib/
    source /opt/rh/rh-postgresql12/enable
    source /opt/rh/devtoolset-8/enable
    source /opt/rh/llvm-toolset-7.0/enable
%endif
%configure
%make_build

%install
%make_install
install -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}.service   %{buildroot}%{_unitdir}/%{name}.service
install -Dpm 0644 %{_builddir}/{{{ git_dir_name }}}/%{name}@.service  %{buildroot}%{_unitdir}/%{name}@.service
install -Dpm 0644 %{buildroot}%{_docdir}/%{name}/stellar-core_example.cfg %{buildroot}%{_sysconfdir}/stellar/%{name}.cfg

install -d %{buildroot}/var/log/stellar
install -d %{buildroot}/var/lib/stellar/core
install -d %{buildroot}%{_sysconfdir}/stellar

%if 0%{?rhel} && 0%{?rhel} == 7
    install -D /opt/rh/rh-postgresql12/root/usr/lib64/libpq.so.rh-postgresql12-5 %{buildroot}%{_datadir}/%{system_name}/lib/libpq.so.rh-postgresql12-5
%endif

%check
%if 0%{?rhel} && 0%{?rhel} == 7
source /opt/rh/llvm-toolset-7.0/enable
%endif

make check

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%files
%{_bindir}/%{name}
%dir %{_docdir}/%{name}/
%doc %{_docdir}/%{name}/*
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%config(noreplace) %{_sysconfdir}/stellar/%{name}.cfg
%config %{_sysconfdir}/logrotate.d/%{name}
%dir %attr(0755, stellar, stellar) /var/log/stellar
%dir %attr(0755, stellar, stellar) /var/lib/stellar/core
%if 0%{?rhel} && 0%{?rhel} == 7
    %{_datadir}/%{system_name}/lib/libpq.so.rh-postgresql12-5
%endif

%changelog
* Wed Mar 23 2022 Anatolii Vorona <vorona.tolik@gmail.com>
- init stellar-core rpm
