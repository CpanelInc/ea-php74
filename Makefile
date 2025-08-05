OBS_PROJECT := EA4
OBS_PACKAGE := ea-php74
DISABLE_BUILD := repository=CentOS_9 repository=Almalinux_10 repository=xUbuntu_22.04 repository=xUbuntu_24.04
include $(EATOOLS_BUILD_DIR)obs.mk
