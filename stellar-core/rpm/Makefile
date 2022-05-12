# required packages:
# dnf install rpmdevtools rpkg

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

epel7:
	spectool --get-files --directory $(PROJECTTMPDIR) $(PROJECTNAME)/rpm/$(PROJECTNAME).spec
	rpkg srpm --spec $(PROJECTNAME)/rpm/$(PROJECTNAME).spec --outdir $(PROJECTTMPDIR)
	mock --no-clean -r custom-epel-7-x86_64 --resultdir=rpm-results  $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm
	#mock -r epel-7-x86_64 --resultdir=rpm-results  $(PROJECTTMPDIR)/$(PROJECTNAME)-*.src.rpm