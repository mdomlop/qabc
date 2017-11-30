PREFIX = '/usr'
DESTDIR = ''
TEMPDIR := $(shell mktemp -u --suffix .qabc)
PROGRAM_NAME := $(shell grep ^PROGRAM_NAME src/qabc.py | cut -d\" -f2)
EXECUTABLE_NAME := $(shell grep ^EXECUTABLE_NAME src/qabc.py | cut -d\" -f2)
DESCRIPTION := $(shell grep ^DESCRIPTION src/qabc.py | cut -d\" -f2)
VERSION := $(shell grep ^VERSION src/qabc.py | cut -d\" -f2)
AUTHOR := $(shell grep ^AUTHOR src/qabc.py | cut -d\" -f2)
MAIL := $(shell grep ^MAIL src/qabc.py | cut -d\" -f2)
LICENSE := $(shell grep ^LICENSE src/qabc.py | cut -d\" -f2)
TIMESTAMP = $(shell LC_ALL=C date '+%a, %d %b %Y %T %z')

documents: ChangeLog

ChangeLog: changelog.in
	@echo "$(EXECUTABLE_NAME) ($(VERSION)) unstable; urgency=medium" > $@
	@echo >> $@
	@echo "  * Git build." >> $@
	@echo >> $@
	@echo " -- $(AUTHOR) <$(MAIL)>  $(TIMESTAMP)" >> $@
	@echo >> $@
	@cat $^ >> $@

install: documents
	install -Dm 755 src/qabc.py $(DESTDIR)/$(PREFIX)/bin/qabc
	install -Dm 644 LICENSE $(DESTDIR)/$(PREFIX)/share/licenses/qabc/COPYING
	install -Dm 644 README.md $(DESTDIR)/$(PREFIX)/share/doc/qabc/README
	install -Dm 644 ChangeLog $(DESTDIR)/$(PREFIX)/share/doc/qabc/ChangeLog
	install -Dm 644 resources/qabc.desktop $(DESTDIR)/$(PREFIX)/share/applications/qabc.desktop
	install -Dm 644 resources/qabc.svg $(DESTDIR)/$(PREFIX)/share/pixmaps/qabc.svg
	install -d -m 755 $(DESTDIR)/$(PREFIX)/share/qabc
	cp -r resources/abc $(DESTDIR)/$(PREFIX)/share/qabc
	chown -R root:root $(DESTDIR)/$(PREFIX)/share/qabc
	chmod -R u=rwX,go=rX $(DESTDIR)/$(PREFIX)/share/qabc

uninstall:
	rm -f $(PREFIX)/bin/qabc
	rm -rf $(PREFIX)/share/licenses/qabc/
	rm -rf $(PREFIX)/share/doc/qabc/
	rm -rf $(PREFIX)/share/qabc/

clean:
	rm -rf *.xz *.gz *.pot po/*.mo *.tgz *.deb *.rpm ChangeLog /tmp/tmp.*.qabc debian/changelog debian/README debian/files debian/qabc debian/debhelper-build-stamp debian/qabc*


pkg: clean
	mkdir $(TEMPDIR)
	tar cf $(TEMPDIR)/qabc.tar ../qabc
	cp packages/pacman/local/PKGBUILD $(TEMPDIR)/
	cd $(TEMPDIR); makepkg
	cp $(TEMPDIR)/qabc-*.pkg.tar.xz .
	@echo Package done!
	@echo You can install it as root with:
	@echo pacman -U qabc-*.pkg.tar.xz

deb: ChangeLog
	cp README.md debian/README
	cp ChangeLog debian/changelog
	#fakeroot debian/rules clean
	#fakeroot debian/rules build
	fakeroot debian/rules binary
	mv ../qabc_$(VERSION)_all.deb .
	@echo Package done!
	@echo You can install it as root with:
	@echo dpkg -i qabc_$(VERSION)_all.deb
