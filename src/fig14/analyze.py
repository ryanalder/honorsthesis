import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.stats as st


def display_results(x, data):
    return [data[i]*100/(x[i]) for i in range(len(x))]

def main():
    interfered = []
    no_receivers = []
    under_sens = []
    tx_power = []
    x = []
    totalTransmissions = []
    for i in range(1, 20):
        pkts = [0, 0, 0, 0]

        file = open(f'./total{i}.txt')
        totalTransmissions.append(int(float(file.readline().split()[0])))
        x.append(totalTransmissions[-1] / 144)
        file = open(f'./phyPerformance{i}.txt')
        for line in file:
            d = line.split()
            pkts[0] += int(d[4])
            pkts[1] += int(d[5])
            pkts[2] += int(d[6])
            pkts[3] += int(d[7])

        file.close()
        interfered.append(pkts[0])
        no_receivers.append(pkts[1])
        under_sens.append(pkts[2])
        tx_power.append(pkts[3])

    y = display_results(totalTransmissions, interfered)
    plt.plot(x, y, 'r.', label="Interfered")
    plt.plot(x, y, 'r')
    y = display_results(totalTransmissions, no_receivers)
    plt.plot(x, y, 'mP', label="No Receivers")
    plt.plot(x, y, 'm')
    y = display_results(totalTransmissions, tx_power)
    plt.plot(x, y, 'cx', label="Low TX Power")
    plt.plot(x, y, 'c')

    y = [(interfered[i] + no_receivers[i] + tx_power[i])*100/(totalTransmissions[i]) for i in range(len(x))]
    plt.plot(x, y, label="Combined")
    plt.title("Packet Loss - Constant Position")
    plt.xlabel("# end-nodes")
    plt.ylabel("% pkt loss")
    plt.grid()
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
