#!/bin/sh

# ftpget -u aiftp01 -p Aio426#! 10.193.9.64 $FILE
# ftpget -u aiftp01 -p Aio426#! 10.193.9.64 $FILE
USER=aiftp01
PSWD=Aio426#!
FTP_SERVER=10.193.9.64
GARBAGE_DIR=garbage_dir

# server IP and port
SERVER_IP=10.190.0.120
SERVER_PORT=19998

# cross compile toolchain path
TOOLCHAIN_PATH=/media/disk_4t_1/runtime/test_user/qiahua/toolchain/gcc-linaro-6.2.1-2016.11-x86_64_aarch64-linux-gnu/bin/

# current work directory
PWD_DIR=`pwd`

# current top directory
TOP_DIR=${PWD_DIR}

# HW board, (juno, 6cg)
BOARD=juno

# linux versions name, optional
LINUX_VERSION=

# linux defconfig file name, optional
LINUX_DEFCONFIG=

# AIPU_runtime_validation source path, it depends on AIPU_runtime_design
# put both to the same directory
RUNTIME_VALIDATION_PATH=$TOP_DIR/runtime_version/

# Note:
# the TFTP server directory which must match with 'TFTP_DIRECTORY'
# in /etc/default/tftpd-hpa
TFTP_DIR=/media/disk_4t_1/runtime/test_user/tftp_root

# -c: compile Linux firstly
# null: no compile Linux
COMPILE_LINUX_FLAG=

# KCI test result file
FILE=kci_result.txt

export LD_LIBRARY_PATH=/media/disk_4t_1/runtime/test_user/qiahua/workspace/python/python_for_x86/python_3.6_install/lib:$LD_LIBRARY_PATH
export PATH=/media/disk_4t_1/runtime/test_user/qiahua/workspace/python/python_for_x86/python_3.6_install/bin:$PATH

function ftp_put_file()
{
	if [ ! -e $FILE ]; then
		echo "$FILE not exist"
		exit 1
	fi

	timeSec=$(date +%s)
	NEW_FILE=${FILE}_${timeSec}

	# ftp operation
	ftp -niv <<- EOF
	open 10.193.9.64
	user aiftp01 Ai16!12#
	binary
	rename $FILE ${GARBAGE_DIR}/$NEW_FILE
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
	echo "  ./kci_server.sh -b board -k linux -f linux_defconifg [-c] [--tftp path] -h"
	echo "  -b: board name (juno, 6cg)"
	echo "  -k: linux version name, same with linux source folder name"
	echo "  -f: linux kernel defconfig file name, see juno/xxx/linux_defconfig/"
	echo "  -c: [-c], decide compile Linux or not"
	echo "  --tftp: [--tftp path], specify TFTP server path"
	echo "  -h: this help"
}

function kci_test()
{
	if [ -z $LINUX_VERSION -a -z $LINUX_DEFCONIFG ]; then
		./kci_scripts/kci/kci_server.py -i $SERVER_IP -p $SERVER_PORT \
			-t $TOOLCHAIN_PATH \
			-b $BOARD \
			-r $RUNTIME_VALIDATION_PATH \
			--tftp $TFTP_DIR \
			$COMPILE_LINUX_FLAG -v
	elif [ -z $LINUX_DEFCONIFG ]; then
		./kci_scripts/kci/kci_server.py -i $SERVER_IP -p $SERVER_PORT \
			-t $TOOLCHAIN_PATH \
			-b $BOARD \
			-k $LINUX_VERSION \
			-r $RUNTIME_VALIDATION_PATH \
			--tftp $TFTP_DIR \
			$COMPILE_LINUX_FLAG -v
	else
		./kci_scripts/kci/kci_server.py -i $SERVER_IP -p $SERVER_PORT \
			-t $TOOLCHAIN_PATH \
			-b $BOARD \
			-k $LINUX_VERSION \
			-f $LINUX_DEFCONIFG \
			-r $RUNTIME_VALIDATION_PATH \
			--tftp $TFTP_DIR \
			$COMPILE_LINUX_FLAG -v
	fi

	if [ $? -eq 0 ]; then
		ftp_put_file
		# echo "KCI Server ftp [todo]"
	else
		echo "KCI Server test [fail]"
		exit 1
	fi
}

ARGS=`getopt -o hb:k:f:c --long tftp: -n 'kci_server.sh' -- "$@"`
eval set -- "$ARGS"

while [ -n "$1" ]
do
	case "$1" in
	-h|--help)
		help
		exit 0
		;;
	-b)
		BOARD=$2
		shift
		;;
	-k)
		LINUX_VERSION=$2
		shift
		;;
	-f)
		LINUX_DEFCONIFG=$2
		shift
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
