VERSION=0.0.1

run:
	rpmdev-setuptree
	git archive --format=tar.gz --prefix=stellar-packages/ -o ~/rpmbuild/SOURCES/stellar-packages.tar.gz HEAD
	rpmbuild --undefine=_disable_source_fetch -ba stellar-horizon/rpm/stellar-horizon.spec

mock:
	mock -r centos-stream-8-x86_64 \
		--enable-network \
		--define='_disable_source_fetch 0'   \
		--scm-enable --scm-option method=git \
		--scm-option package=stellar-horizon \
		--scm-option git_get='git clone https://github.com/go-shortcut/stellar-packages stellar-horizon' \
		--scm-option spec='stellar-horizon/rpm/stellar-horizon.spec' \
		--scm-option branch=rpm_test \
		--scm-option write_tar=True \
		-v
