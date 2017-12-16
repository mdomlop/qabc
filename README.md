![qabc-preview](https://github.com/mdomlop/qabc/blob/master/preview.png "qabc interface")

Qabc (Alpha version)
====

An [ABC](http://abcnotation.com) music format manager.

Qabc is an open source ABC editor written in python with Qt 5. There is another
similar program called [EasyABC](http://www.nilsliberg.se/ksp/easyabc/), that yet
is better, and offers a most mature solution for managing ABC tunebooks, but this
just an alternative that I'm writing while learn python and Qt.

Qabc actually is alpha state. Features and interface are not definitive and may vary.

### Features:

- Good ABC standard coverage thanks to internal use of abcm2ps and abc2midi.

- Export to MIDI.

- Play the active tune as midi.

- The musical score is automatically updated as you type in ABC code.

- Unicode (UTF-8) encoding.

- Transposing functionality (using abc2abc).

- Good tune search by real time filtering.

- Change tempo for playing (using abc2midi).

- Renumbering and alphabetically sorting of tunes.

- Some others ;-).


### Interface:

The main window is divided into three resizable parts: a list of tunes, 
a musical score panel and the ABC code editor. You can hide, show or change 
the position of any of this at you wish.

Additionally you can show a log panel to see possible errors in the ABC code
of the tune.

Installation
------------

Execute:

		$ make
		# make install

You also can build a Debian package. For it:

		$ make deb

And install it with:

 		# dpkg -i qabc*.deb


