#  SDF - packages

1.  [Adding the SDF stable repository to your system](adding-the-sdf-stable-repository-to-your-system.md)
2.  [Quickstart](quickstart.md)
3.  [Installing individual packages](installing-individual-packages.md)
4.  [Upgrading](upgrading.md)
5.  [Bleeding Edge](bleeding-edge-unstable-repository.md)
6.  [Debug Symbols](debug-symbols.md)
7.  [Running Horizon in production](running-horizon-in-production.md)
8.  [Building Packages](building-packages.md)
9.  [Publishing a History archive](publishing-a-history-archive.md)
10. [Testnet Reset](testnet-reset.md)

## Building Packages

### stellar-core

#### dpkg-buildflags

`dpkg-buildflags` is a standard component of the Debian packaging system, when called it returns system wide defaults for compiler flags and is used primarily by the `dpkg-buildpackage` program to configure the build environment.

On Ubuntu 16.04 these default to:

```
# dpkg-buildflags | egrep '^(C|CPP|CXX|LD)FLAGS'
CFLAGS=-g -O2 -fstack-protector-strong -Wformat -Werror=format-security
CPPFLAGS=-Wdate-time -D_FORTIFY_SOURCE=2
CXXFLAGS=-g -O2 -fstack-protector-strong -Wformat -Werror=format-security
LDFLAGS=-Wl,-Bsymbolic-functions -Wl,-z,relro
```

When building the `stellar-core` packages, it is possible to override the compiler flags returned by `dpkg-buildflags` by setting certain variables in your build environment.

##### CXXFLAGS

If you need to modify to the c++ compiler flags, you may do so by setting `DEB_CXXFLAGS_SET` in your build environment which overrides the default `CXXFLAGS` value returned to `dpkg-buildpackage` by `dpkg-buildflags`.

One caveat to this which is not immediately obvious, is that we prepend `-stdlib=libc++ -fno-omit-frame-pointer -isystem /usr/include/libcxxabi` to the beginning of `DEB_CXXFLAGS_SET` or by default to the value returned by `dpkg-buildflags`.
We do this by setting `DEB_CXXFLAGS_MAINT_PREPEND` in the `debian/rules` make file to enforce the use of `clang++`,`libc++` and `libc++abi` during compilation.

Example:

```
DEB_CXXFLAGS_MAINT_PREPEND = -stdlib=libc++ -fno-omit-frame-pointer -isystem /usr/include/libcxxabi
CXXFLAGS = $(DEB_CXXFLAGS_MAINT_PREPEND) + $(DEB_CXXFLAGS_SET)
```

##### CFLAGS

If you need to modify the c compiler flags, you may do so by setting `DEB_CFLAGS_SET` in your build environment which overrides the default `CFLAGS` value returned to `dpkg-buildpackage` by `dpkg-buildflags`.

Example:

`CFLAGS = $(DEB_CFLAGS_SET)`

##### DEB_CONFIGURE_OPTS

If you need to modify the configure script parameters you may do so by setting `DEB_CONFIGURE_OPTS` in your build environment. This overrides the default value set within the stellar-core `debian/rules`

Example:

```
# set DEB_CONFIGURE_OPTS in your environment to override
DEB_CONFIGURE_OPTS ?= --prefix=/usr --includedir=/usr/include --mandir=/usr/share/man --infodir=/usr/share/info --sysconfdir=/etc --localstatedir=/var
./configure $(DEB_CONFIGURE_OPTS)
```

##### LDFLAGS, CPPFLAGS

The methods we use above for overriding `CFLAGS` can also be used to set other variables that `dpkg-buildflags` returns.

Example:

`LDFLAGS = $(DEB_LDFLAGS_SET)`
`CPPFLAGS = $(DEB_CPPFLAGS_SET)`
