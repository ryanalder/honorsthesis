import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.stats as st

def confidence_interval(clvl, data):
    return st.t.interval(clvl, len(data)-1, loc=np.mean(data), scale=st.sem(data))

def display_results(x, data):
    return [data[i]*100/(x[i] * 144) for i in range(len(x))]

def shortenArrays(arr, cast):
    final = []
    for i in range(len(arr)):
        if cast[i] == 1:
            final.append(arr[i])
    return final

def main():
    interfered = []
    no_receivers = []
    under_sens = []
    tx_power = []
    totalNodes = []

    for i in range(265):
        pkts = [0, 0, 0, 0]
        file = open(f'./total{i}_{0}.txt')
        totalNodes.append(int(float(file.readline().split()[0])) / 144)
        for j in range(5):
            file = open(f'./phyPerformance{i}_{j}.txt')
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

    cast, x = [1], [totalNodes[0]]
    nextN = totalNodes[0]
    for i in range(1, len(totalNodes)):
        if totalNodes[i] >= nextN + 300:
            cast.append(1)
            nextN = totalNodes[i]
            x.append(totalNodes[i])
        else:
            cast.append(0)

    y = shortenArrays(display_results(totalNodes, interfered), cast)
    plt.plot(x, y, 'r.', label="Interfered")
    plt.plot(x, y, 'r')
    y = shortenArrays(display_results(totalNodes, no_receivers), cast)
    plt.plot(x, y, 'mP', label="No Receivers")
    plt.plot(x, y, 'm')
    y = shortenArrays(display_results(totalNodes, tx_power), cast)
    plt.plot(x, y, 'cx', label="Low TX Power")
    plt.plot(x, y, 'c')

    y = [(interfered[i] + no_receivers[i] + tx_power[i])*100/(totalNodes[i] * 144) for i in range(len(totalNodes))]
    plt.plot(x, shortenArrays(y, cast), label="Combined")
    plt.title("Packet Loss - Increasing # End-Nodes")
    plt.xlabel("# end-nodes")
    plt.ylabel("% pkt loss")
    plt.grid()
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
