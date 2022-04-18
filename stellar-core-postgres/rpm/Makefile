PROJECTNAME=stellar-core-postgres
PROJECTTMPDIR=/tmp/$(PROJECTNAME)

clean:
	rm -rf $(PROJECTTMPDIR)

spec:
	rpmspec -P $(PROJECTNAME)/rpm/$(PROJECTNAME).spec

rpmbuild:
	mkdir -p $(PROJECTTMPDIR)
	rpkg srpm --spec $(PROJECTNAME)/rpm/$(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	rpmbuild --nocheck --rebuild $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm
