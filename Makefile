# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS      ?=
SPHINXBUILD     ?= sphinx-build
SPHINXAUTOBUILD ?= sphinx-autobuild
SOURCEDIR       = docs
BUILDDIR        = _build
DOCKERUSER      ?= gzynda

####################################
# Sanity checks
####################################
PROGRAMS := docker
.PHONY: $(PROGRAMS)
.SILENT: $(PROGRAMS)

docker:
	docker info 1> /dev/null 2> /dev/null && \
	if [ ! $$? -eq 0 ]; then \
		echo "\n[ERROR] Could not communicate with docker daemon. You may need to run with sudo.\n"; \
		exit 1; \
	fi
####################################
# Docker containers
####################################
CONTAINERS := $(shell echo $(DOCKERUSER)/{sleepy-server,update-server})

$(DOCKERUSER)/%: scripts/%.py | docker
	docker build --build-arg FILE="$(notdir $<)" -t $@:latest $(dir $<)
	docker push $@:latest

containers: $(CONTAINERS)
	@echo Done!

####################################
# Sphinx
####################################
# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "  livehtml    to watch the source directory for changes and rebuild the html"

.PHONY: help Makefile clean

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
#%: Makefile
#	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf $(BUILDDIR)/*

livehtml:
	@$(SPHINXAUTOBUILD) -b html $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)/html"
