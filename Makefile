# ~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=
#
#      Set up the Zabbix Backup Tool
#
# ~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=

SHELL 		:= /bin/bash
VENV    	:= .venv
SCRIPT		:= zabbix_export.py
EXE 		:= $(SCRIPT:%.py=%)
BACKUPS		:= BACKUPS
P_WD 		:= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
# keep the snapshots of the x last days
DAYS        := 15


define _script
#!/bin/bash

CWD=$$(dirname $$(realpath $$0))

source $${CWD}/.venv/bin/activate

no_proxy=* $${CWD}/$(SCRIPT) -d $(BACKUPS) -z $$@
deactivate
endef

export _script

.PHONY: 	install uninstall venv


install: 	| $(VENV) $(EXE)
	@if ! $$(crontab -l | grep -q $(P_WD)/$(BACKUPS)); then \
	  { crontab -l; \
	    echo "0 1 * * * find $(P_WD)/$(BACKUPS)/ -ctime +$(DAYS) -delete; $(P_WD)/$(EXE)"; \
		} | crontab -u root - ; \
	   echo "Daily rotation set to $(DAYS) last backups"; \
	   echo "Remember to set the configuration (ref. zbx_config.ini)"; \
	fi;


uninstall:
	@crontab -l | grep -wv $(P_WD)/$(EXE) | crontab -
	@echo "Backups rotation removed"

venv: | $(VENV)

$(EXE):
	@echo "$$_script" > $@
	@chmod +x $@


$(VENV):
	python3 -m venv $@
	source $@/bin/activate  && pip install -r requirements.txt

