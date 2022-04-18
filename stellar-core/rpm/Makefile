PROJECTNAME=stellar-core
PROJECTTMPDIR=/tmp/$(PROJECTNAME)

clean:
	rm -rf $(PROJECTTMPDIR)

submodules:
	cd $(PROJECTNAME)/rpm/ && bash update.submodules.sh  > $(PROJECTNAME).spec

spec:
	rpkg spec --spec $(PROJECTNAME)/rpm/$(PROJECTNAME).spec -p

rpmbuild:
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME)/rpm/$(PROJECTNAME).spec
	rpkg srpm --spec $(PROJECTNAME)/rpm/$(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	rpmbuild --nocheck --rebuild $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm
