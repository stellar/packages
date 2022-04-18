PROJECTNAME=stellar-horizon
PROJECTTMPDIR=/tmp/$(PROJECTNAME)

clean:
	rm -rf $(PROJECTTMPDIR)

rpmbuild:
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME)/rpm/$(PROJECTNAME).spec
	rpkg srpm --spec $(PROJECTNAME)/rpm/$(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	rpmbuild --nocheck --rebuild $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm
