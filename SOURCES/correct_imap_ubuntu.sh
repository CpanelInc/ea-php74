pre_imap () {
    if test -n "$IN_IMAP"; then
        save_CFLAGS="$CFLAGS"; CFLAGS="-I$IMAP_INC_DIR $CFLAGS"
        save_LIBS="$LIBS";
        LIBS=`echo $LIBS | sed -- "s/-limap//g"`
        LIBS="-L$IMAP_LIBDIR -lc-client $LIBS"
    fi
}

post_imap () {
    if test -n "$IN_IMAP"; then
        CFLAGS="$save_CFLAGS"
        LIBS="$save_LIBS"
    fi
}

