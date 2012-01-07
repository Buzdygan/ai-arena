TOP := $(dir $(lastword $(MAKEFILE_LIST)))

ifeq ($(LANG), CPP)
	include $(TOP)/cpp.mk
else ifeq ($(LANG), C)
	include $(TOP)/c.mk
else ifeq ($(LANG), JAVA)
print settings.MAKEFILE_DIR
	include $(TOP)/java.mk
endif
