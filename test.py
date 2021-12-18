def the_funt(dispatch, *args, **kargs):
    dispatch("hello")


the_funt(print, "192.168.1.52", port=80)
