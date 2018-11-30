COMPILER = stickytape
COMPILER_OUTPUT = --output-file

EXPERIMENTS = \
	digitspan \
	trailmaking

RELEASE = $(shell date +%Y-%M-%d)

TARGET_FILE = cognitive-tasks-$(RELEASE).zip

CONFIG = config.conf
I18N = i18n.conf

build: mkdir $(EXPERIMENTS)

mkdir:
	@mkdir -p build

$(EXPERIMENTS): %:
	@mkdir -p build/$*
	$(COMPILER) tasks/$*/$*.py $(COMPILER_OUTPUT) build/$*/$*.py
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
