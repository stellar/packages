VERSION=0.0.1

run:
	rpmdev-setuptree
	git archive --format=tar.gz --prefix=stellar-packages/ -o ~/rpmbuild/SOURCES/stellar-packages.tar.gz HEAD
	rpmbuild --undefine=_disable_source_fetch -ba stellar-horizon/rpm/stellar-horizon.spec
