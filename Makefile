OBS_PROJECT := EA4
OBS_PACKAGE := ea-php74
DISABLE_BUILD := arch=i586
DISABLE_BUILD += repository=CentOS_9
include $(EATOOLS_BUILD_DIR)obs.mk
