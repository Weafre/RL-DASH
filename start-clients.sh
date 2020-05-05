#!/bin/bash
for i in  {1..10..1}
	do
		
	   ./waf --run="tcp-stream-bitrate --simulationId='testbw' --maxBuffer=50000000 --numberOfClients=1 --adaptationAlgo=rl-algorithm --segmentDuration=2000000 --bitRate=100 --bwfile=contrib/bwtrace1.txt --segmentSizeFile=contrib/dash-meets-ns3gym/segmentSizes.txt"
	done




