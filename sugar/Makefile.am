INCLUDES = -DXDG_PREFIX=sugar_mime

noinst_LTLIBRARIES = libsugar.la

libsugar_la_SOURCES = 	\
	xdgmime.c 	\
	xdgmime.h	\
	xdgmimealias.c	\
	xdgmimealias.h	\
	xdgmimecache.c	\
	xdgmimecache.h	\
	xdgmimeglob.c 	\
	xdgmimeglob.h 	\
	xdgmimeint.c 	\
	xdgmimeint.h 	\
	xdgmimemagic.c  \
	xdgmimemagic.h	\
	xdgmimeparent.c	\
	xdgmimeparent.h

sugardir = $(pythondir)/sugar
sugar_PYTHON =		\
	logger.py	\
	mime.py

pkgpyexecdir = $(pythondir)/sugar

pkgpyexec_LTLIBRARIES = _sugarbaseext.la

_sugarbaseext_la_CFLAGS = 		\
	$(EXTENSION_CFLAGS)		\
	$(PYTHON_INCLUDES)

_sugarbaseext_la_LDFLAGS = -module -avoid-version
_sugarbaseext_la_LIBADD = $(EXTENSION_LIBS)
_sugarbaseext_la_SOURCES = _sugarbaseextmodule.c
nodist__sugarbaseext_la_SOURCES = _sugarbaseext.c

_sugarbaseext.c: _sugarbaseext.defs _sugarbaseext.override

CLEANFILES = _sugarbaseext.c

EXTRA_DIST =				\
	_sugarbaseext.override		\
	_sugarbaseext.defs

.defs.c:
	(cd $(srcdir)\
	 && $(PYGTK_CODEGEN) \
	    --override $*.override \
	    --prefix py$* $*.defs) > gen-$*.c \
	&& cp gen-$*.c $*.c \
	&& rm -f gen-$*.c
