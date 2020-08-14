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

# the directory to store Linux defconfig files
LINUX_DEFCONFIG_PATH=./linux_defconfig/

# the source code directory of Linux kernel being tested
LINUX_KERNEL_PATH=/media/disk_4t_1/runtime/test_user/qiahua/workspace/kernel_src/linux-android-4.9.51/

# the directory to store Linux Images and AIPU runtime library and test APPs
IMAGE_PATH=./images/

# AIPU_runtime_validation source path, it depends on AIPU_runtime_design
# put both to the same directory
RUNTIME_VALIDATION_PATH=/media/disk_4t_1/runtime/test_user/qiahua/workspace/umd_test/runtime_for_juno

# Note:
# the TFTP server directory which must match with 'TFTP_DIRECTORY'
# in /etc/default/tftpd-hpa
TFTP_DIR=/media/disk_4t_1/runtime/test_user/tftp_root

# -c: compile Linux firstly
# null: no compile Linux
COMPILE_LINUX_FLAG=

# KCI test result file
FILE=kci_result.txt

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
	if [ -n "$COMPILE_LINUX_FLAG" ]; then
		mkdir -p $IMAGE_PATH
		rm -fr ${IMAGE_PATH}/*
	fi

    ./kci/kci_server.py -i $SERVER_IP -p $SERVER_PORT \
        -t $TOOLCHAIN_PATH \
        -f $LINUX_DEFCONFIG_PATH \
        -k $LINUX_KERNEL_PATH \
        -s $IMAGE_PATH \
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