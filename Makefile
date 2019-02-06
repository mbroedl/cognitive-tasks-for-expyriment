COMPILER = stickytape
COMPILER_OUTPUT = --output-file

EXPERIMENTS = \
	digitspan \
	trailmaking \
	rt_simple \
	nback

RELEASE = $(shell date +%Y-%m-%d)

TARGET_FILE = cognitive-tasks-$(RELEASE).zip

CONFIG = config.conf
I18N = i18n.conf

ifeq ($(FORCE),)
ifneq ($(shell git rev-parse --abbrev-ref HEAD), master)
$(error Not on branch master)
endif
ifneq ($(shell git status -s --untracked-files=no),)
$(error Uncommited changes to master branch)
endif
endif

build: mkdir $(EXPERIMENTS)

mkdir:
	@mkdir -p build

$(EXPERIMENTS): %:
	@mkdir -p build/$*
	$(COMPILER) tasks/$*/$*.py $(COMPILER_OUTPUT) build/$*/$*.py
	@sed -i '2i# -*- coding: utf-8 -*-' build/$*/$*.py
	@cp tasks/$*/$(CONFIG) build/$*/
	@cp tasks/$*/$(I18N) build/$*/

zip:
	@cd build;\
	zip -r $(TARGET_FILE) */*

release: mkdir clean build zip
	@echo ::::::
	@echo built build/$(TARGET_FILE)
	@stat build/$(TARGET_FILE) -c"%s bytes"

clean:
	@rm -r build
