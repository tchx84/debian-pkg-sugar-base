AC_INIT([sugar-base],[0.1],[],[sugar-base])

AC_PREREQ([2.59])

AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_SRCDIR([configure.ac])

AM_INIT_AUTOMAKE([1.9 foreign dist-bzip2 no-dist-gzip])

AC_DISABLE_STATIC
AC_PROG_LIBTOOL

AM_PATH_PYTHON
AM_CHECK_PYTHON_HEADERS(,[AC_MSG_ERROR(could not find Python headers)])

AC_PATH_PROG(PYGTK_CODEGEN, pygtk-codegen-2.0, no)

PKG_CHECK_MODULES(EXTENSION, pygobject-2.0)

AC_OUTPUT([
Makefile
src/Makefile
src/sugar/Makefile
])
