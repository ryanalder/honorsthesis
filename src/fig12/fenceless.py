# run this script once per gateway

from os import system
import signal
import sys

def signal_handler(signal, frame):
    print("Caught SIGINT, exiting...")
    sys.exit(1);

def main():
    signal.signal(signal.SIGINT, signal_handler)

    for i in range(5):
        sys_call = f'./waf --command-template="%s --RngRun={i}" --run fenceless-grazing'
        print(sys_call)
        ret = system(sys_call)

        if (ret):
            print("System call error, exiting...")
            return

        sys_call = f'mv phyPerformance.txt phyPerformance{i}.txt; \
                     mv nodeData.txt nodeData{i}.txt; \
                     mv globalPerformance.txt globalPerformance{i}.txt; \
                     mv total.txt total{i}.txt; \
                     mv *.txt ~/1gw' # adjust this based on # gateways

        print("Renaming and moving files...")
        ret = system(sys_call)

        if (ret):
            print("System call error, exiting...")
            return

if __name__ == "__main__":
    main()
