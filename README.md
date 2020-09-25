# kci_aipu_driver

adapt aipu driver with Linux kernel

################ usage ####################

KCI is for adapting AIPU driver with evolutionary Linux kernel version.
This framework take use of server/client infrastructure. The server side
will compile Linux kernel, transfer generated Linux Image one by one to
Juno.

server side: there are two choices to boot kci server

1.	if there's no Linux kernel image, compile Linux kernel firstly via adding -c parameter
	this way will compile Linux firstly, then loop and test all images.

	# ./kci/kci_server.py
		-i 10.190.0.120
		-p 19998
		-t /media/disk_4t_1/runtime/test_user/qiahua/toolchain/gcc-linaro-6.2.1-2016.11-x86_64_aarch64-linux-gnu/bin/
		-b juno
		-k linux-android-4.9.51
		-f test_defconfig
		-c
		-v

2.	if it has generated Linux kernel images, just omit -c parameter, there are
	three ways for referencing.

	2.1.	loop and test all images belong to specific board (-b)

		# ./kci/kci_server.py
			-i 10.190.0.120
			-p 19998
			-t /media/disk_4t_1/runtime/test_user/qiahua/toolchain/gcc-linaro-6.2.1-2016.11-x86_64_aarch64-linux-gnu/bin/
			-b juno
			-k linux-android-4.9.51
			-f test_defconfig
			-v

	2.2.	loop and test all images belong to specific board (-b) and linux version (-k)

		# ./kci/kci_server.py
			-i 10.190.0.120
			-p 19998
			-t /media/disk_4t_1/runtime/test_user/qiahua/toolchain/gcc-linaro-6.2.1-2016.11-x86_64_aarch64-linux-gnu/bin/
			-b juno
			-k linux-android-4.9.51
			-v

	2.3.	just test one image (-f) belong to specific board (-b) and linux version (-k)

		# ./kci/kci_server.py
		-i 10.190.0.120
		-p 19998
		-t /media/disk_4t_1/runtime/test_user/qiahua/toolchain/gcc-linaro-6.2.1-2016.11-x86_64_aarch64-linux-gnu/bin/
		-b juno
		-k linux-android-4.9.51
		-f test_defconfig
		-v

3.	command line arguments

	-i: server IP address
	-p: server listen port
	-t: cross compile toolchain directory
	-b: hardware platform name (juno, 6cg)
	-k: Linux kernel version name
	-f: Linux kernel defconfig name
	-c: indicate whether compile Linux or not
	-v: dump debug log

client side: boot kci client on Juno

1.	bootup AIPU test on client side

	# ./main_entry.py
		-p juno-linux-4.9
		-a Z1_0904
		-b ../Z1_0904
		-l 1
		-f runtime.txt
		-t runtime_test
		--ip 10.190.0.120
		--port 19998

2.	command line arguments

	-p: hardware platform
	-a: AIPU hardware architecture
	-b: the benchmark directory
	-l: test loop times
	-f: result record file
	-t: run runtime test
	--ip: server IP address
	--port: server listen port
