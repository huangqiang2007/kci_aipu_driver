#!/bin/sh

# ftpget -u aiftp01 -p Aio426#! 10.193.9.64 $FILE
# ftpget -u aiftp01 -p Aio426#! 10.193.9.64 $FILE
USER=aiftp01
PSWD=Aio426#!
FTP_SERVER=10.193.9.64

# server IP and port
SERVER_IP=10.190.0.120
SERVER_PORT=19998

# cross compile toolchain path
TOOLCHAIN_PATH=/media/disk_4t_1/runtime/test_user/qiahua/toolchain/gcc-linaro-6.2.1-2016.11-x86_64_aarch64-linux-gnu/bin/

# current work directory
PWD_DIR=`pwd`

# current top directory
TOP_DIR=${PWD_DIR}

# the directory to store Linux defconfig files
LINUX_DEFCONFIG_PATH=$TOP_DIR/linux_defconfig/

# the source code directory of Linux kernel being tested
LINUX_KERNEL_PATH=$TOP_DIR/source_code/linux_version/linux-android-4.9.51/

# the directory to store Linux Images and AIPU runtime library and test APPs
IMAGE_PATH=$TOP_DIR/images/

# AIPU_runtime_validation source path, it depends on AIPU_runtime_design
# put both to the same directory
RUNTIME_VALIDATION_PATH=$TOP_DIR/source_code/runtime_version/

# KMD build.sh
KMD_BUILD_SH=$RUNTIME_VALIDATION_PATH/AIPU_runtime_design/Linux/driver/kmd/build.sh

# Note:
# the TFTP server directory which must match with 'TFTP_DIRECTORY'
# in /etc/default/tftpd-hpa
TFTP_DIR=/media/disk_4t_1/runtime/test_user/tftp_root

# -c: compile Linux firstly
# null: no compile Linux
COMPILE_LINUX_FLAG=

# KCI test result file
FILE=$TOP_DIR/kci_result.txt

function ftp_put_file()
{
	if [ ! -e $FILE ]; then
		echo "$FILE not exist"
		exit 1
	fi

	# ftp operation
	ftp -niv <<- EOF
	open 10.193.9.64
	user aiftp01 Aio426#!
	binary
	put $FILE
	bye
	EOF
	# ftpput -u $USER -p $PSWD $FTP_SERVER $FILE

	if [ $? -ne 0 ]; then
		echo "ftp put $FILE [fail]"
		exit 1
	else
		echo "ftp put $FILE [ok]"
	fi
}

function ftp_get_file()
{
	# ftp operation
	ftp -niv <<- EOF
	open 10.193.9.64
	user aiftp01 Aio426#!
	ascii
	get $FILE
	bye
	EOF
	# ftpget -u $USER -p $PSWD $FTP_SERVER $FILE

    if [ $? -ne 0 ]; then
        echo "ftp get $FILE [fail]"
        exit 1
    else
        echo "ftp get $FILE [ok]"
    fi
}

function help()
{
    echo "help:"
    echo "  ./kci_server.sh [-c] [--tftp path] -h"
    echo "  -c: [-c], decide compile Linux or not"
    echo "  --tftp: [--tftp path], specify TFTP server path"
    echo "  -h: this help"
}

function kci_test()
{
    # if it needs recompiling Linux, clean up old images.
	if [ -n "$COMPILE_LINUX_FLAG" ]; then
		mkdir -p $IMAGE_PATH
		rm -fr ${IMAGE_PATH}/*
	fi

    # replase Linux source code path for compiling new Images
    if [ -e $LINUX_KERNEL_PATH -a -e $KMD_BUILD_SH ]; then
        LINUX_DIR_LINE="kdir=$LINUX_KERNEL_PATH"
        MODIFY_LINUX_DIR=$(echo $LINUX_DIR_LINE | sed 's/\//\\\//g')
        # echo "LINUX_DIR: "$LINUX_DIR_LINE
        # echo "KMD build: "$KMD_BUILD_SH
        # echo "LINUX_DIR_LINE: "$MODIFY_LINUX_DIR
        sed -i "1,/.*kdir.*/{s/.*kdir.*/$MODIFY_LINUX_DIR/}" $KMD_BUILD_SH
    else
        echo "$LINUX_KERNEL_PATH [not exist]"
        echo "$KMD_BUILD_SH [not exist]"
        exit 1
    fi

    # ./kci_scripts/kci/kci_server.py -i $SERVER_IP -p $SERVER_PORT \
    #     -t $TOOLCHAIN_PATH \
    #     -f $LINUX_DEFCONFIG_PATH \
    #     -k $LINUX_KERNEL_PATH \
    #     -s $IMAGE_PATH \
    #     -r $RUNTIME_VALIDATION_PATH \
    #     --tftp $TFTP_DIR \
    #     $COMPILE_LINUX_FLAG -v

    ./kci_scripts/kci/kci_server.py -i $SERVER_IP -p $SERVER_PORT \
        -t $TOOLCHAIN_PATH \
        -b juno \
        -k linux_version_name \
        -f linux_defconfig_name \
        -r $RUNTIME_VALIDATION_PATH \
        --tftp $TFTP_DIR \
        $COMPILE_LINUX_FLAG -v

	if [ $? -eq 0 ]; then
		ftp_put_file
	else
		echo "KCI Server test [fail]"
		exit 1
	fi
}

ARGS=`getopt -o hc --long tftp: -n 'kci_server.sh' -- "$@"`
eval set -- "$ARGS"

while [ -n "$1" ]
do
    case "$1" in
    -h|--help)
        help
		exit 0
        ;;
    -c)
        COMPILE_LINUX_FLAG=-c
        shift
        ;;
    --tftp)
        TFTP_DIR=$2
        shift
        ;;
    --)
        shift
        break
        ;;
    *)
        break
    esac
    shift
done

kci_test
