all:transfer

transfer:
	scp ./src/iot-pump-control-server.py ec2-user@ec2-3-80-215-176.compute-1.amazonaws.com:/home/ec2-user/iot-pump/ 