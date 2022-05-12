PROJECTNAME=stellar-system
PROJECTTMPDIR=/tmp/$(PROJECTNAME)

clean:
	rm -rf $(PROJECTTMPDIR)

spec:
	rpmspec -P $(PROJECTNAME)/rpm/$(PROJECTNAME).spec

rpmbuild:
	mkdir -p $(PROJECTTMPDIR)
	rpkg srpm --spec $(PROJECTNAME)/rpm/$(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	rpmbuild --nocheck --rebuild $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm

epel7:
	mkdir -p $(PROJECTTMPDIR)
	rpkg srpm --spec $(PROJECTNAME)/rpm/$(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	mock -r custom-epel-7-x86_64 --resultdir=rpm-results  $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm
