# GLOBAL DEBUG_PRINT 
def debug_print(flag, *args, **kwargs):
    if flag:
        print(*args, **kwargs)