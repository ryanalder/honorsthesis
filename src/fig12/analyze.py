import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.stats as st


def calculate_results(x, data):
    return data[0]*100/(x[0] * 144)

def main():
    final_interfered = []
    final_no_receivers = []
    final_tx_power = []
    final_totalNodes = []

    for f in range(1, 5):
        interfered = []
        no_receivers = []
        under_sens = []
        tx_power = []
        totalNodes = []
        pkts = [0, 0, 0, 0]
        file = open(f'./{f}gw/total{0}.txt')
        totalNodes.append(int(float(file.readline().split()[0])) / 144)
        for j in range(5):
            file = open(f'./{f}gw/phyPerformance{j}.txt')
            for line in file:
                d = line.split()
                pkts[0] += int(d[4])
                pkts[1] += int(d[5])
                pkts[2] += int(d[6])
                pkts[3] += int(d[7])

            file.close()
        interfered.append(pkts[0] / 5)
        no_receivers.append(pkts[1] / 5)
        under_sens.append(pkts[2] / 5)
        tx_power.append(pkts[3] / 5)


        final_interfered.append(calculate_results(totalNodes, interfered) / f)
        final_no_receivers.append(calculate_results(totalNodes, no_receivers) / f)
        final_tx_power.append(calculate_results(totalNodes, tx_power) / f)

    total = [None for i in range(len(final_interfered))]
    for i in range(len(total)):
        total[i] = final_interfered[i] + final_no_receivers[i] + final_tx_power[i]

    x = [i for i in range(1, 5)]
    plt.plot(x, final_interfered, 'r.', label="Interfered")
    plt.plot(x, final_interfered, 'r')
    plt.plot(x, final_no_receivers, 'mP', label="No Receivers")
    plt.plot(x, final_no_receivers, 'm')
    plt.plot(x, final_tx_power, 'cx', label="Low TX Power")
    plt.plot(x, final_tx_power, 'c')
    plt.plot(x, total, label="Combined")
    plt.title("Packet Loss - Increasing # Gateways")
    plt.xlabel("# gateways")
    plt.ylabel("% pkt loss")
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
