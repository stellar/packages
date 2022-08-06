#!/bin/bash
set -e -u
TMP_SPEC=$(mktemp /tmp/stellar-core.spec.XXXX)

# Stellar core user functions
STELLAR_CORE_VERSION=$(rpmspec -q --qf "%{Version}" stellar-core.spec)

# grep 'path =' .gitmodules | awk '{print $3}' | sort
StCoreSubModuleDirs=(
  lib/asio
  lib/cereal
  lib/fmt
  lib/libmedida
  lib/libsodium
  lib/spdlog
  lib/tracy
  lib/xdrpp
  src/protocol-next/xdr
)

function stellar_core_submodule_sources() {
  API_GH_STELLAR_CORE=https://api.github.com/repos/stellar/stellar-core
  REF=v${STELLAR_CORE_VERSION}

  ST_CORE_SUBMODULE_SRC=""
  declare -i i=0
  for smod in "${StCoreSubModuleDirs[@]}"; do
    TarballUrl=$(curl -s "$API_GH_STELLAR_CORE/contents/${smod}?ref=$REF" | sed -n 's#git/trees#tarball#; s#"git_url": "\(.*\)",#\1#p;')
    SourceUrl=$(curl --output-dir /tmp/ -sLOJ $TarballUrl -w '%{url}#/%{filename_effective}')
    ST_CORE_SUBMODULE_SRC+="Source10$i: $SourceUrl\n"
    i+=1
  done
  echo -e "$ST_CORE_SUBMODULE_SRC"
}

function stellar_core_submodule_prep() {
  ST_CORE_SUBMODULE_PREP=""
  declare -i i=0
  for smod in "${StCoreSubModuleDirs[@]}"; do
    ST_CORE_SUBMODULE_PREP+="tar -zxf  %{SOURCE10$i} --strip-components 1 -C ${smod}/\n"
    i+=1
  done
  echo -e "$ST_CORE_SUBMODULE_PREP"
}
# end Stellar core user functions


MARKER_SOURCES='submodule sources'
MARKER_PREP='submodules setup'

{
  sed    "/# START: $MARKER_SOURCES/q"                          stellar-core.spec
  stellar_core_submodule_sources
  sed -n "/^# END: $MARKER_SOURCES/,/^# START: $MARKER_PREP/p"  stellar-core.spec
  stellar_core_submodule_prep
  sed -n "/# END: $MARKER_PREP/,//p"                            stellar-core.spec
} > $TMP_SPEC

mv $TMP_SPEC stellar-core.spec
echo SUCCESS
