def try_set_process_name(name):
    try:
        import setproctitle
        setproctitle.setproctitle(name)
    except (ImportError, AttributeError):
        pass
