ifeq ($(MAKE_ENV), container)
    include makefile.container
else
    include makefile.local
endif
