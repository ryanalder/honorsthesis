import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.stats as st

nRuns = 250

def confidence_interval(clvl, data):
    return st.t.interval(clvl, len(data)-1, loc=np.mean(data), scale=st.sem(data))

def display_results(data, npkts, ax, title):
    int_x = [i for i in range(1, len(data) + 1)]
    int_y = [data[0]*100/npkts]
    int_ci = None

    int_count = data[0]
    int_avg = 0
    for i in range(1, len(data)):
        int_count += data[i]
        int_avg = int_count / (i+1)
        int_y.append(int_avg*100 / npkts)

    ax.plot(int_x, int_y, label="Average pkt loss")
    ci = confidence_interval(0.95, np.array(data))
    ax.plot([int_x[-1], int_x[-1]], [ci[0]*100/npkts, ci[1]*100/npkts], label="95% CI")
    ax.set_title(title)
    ax.legend()
    ax.grid()

def datarate():
    dr = [0 for i in range(12)]
    for i in range(nRuns):
        file = open(sys.argv[1] + f'/node/nodeData{i}.txt')
        for line in file:
            l = line.split()
            if l[0] == "85800":
                dr[int(l[4])] += 1
        file.close()
    for i in range(len(dr)):
        dr[i] /= nRuns
        print(f'Avg # devices w/ data rate {i}: {dr[i]}')


def main():
    if len(sys.argv) != 3:
        print("Incorrect arguments")
        return

    if sys.argv[-1] == "dr":
       datarate()
        return

    folder = sys.argv[1]

    interfered = []
    no_receivers = []
    under_sens = []
    tx_power = []

    npkts = int(sys.argv[2]) * 144

    for i in range(250):
        pkts = [0, 0, 0, 0]
        file = open(folder + f'/phy/phyPerformance{i}.txt')

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

    fig, axs = plt.subplots(3)

    display_results(interfered, npkts, axs[0], "Packet Loss - Interfered")
    display_results(no_receivers, npkts, axs[1], "Packet Loss - No Receivers")
    display_results(tx_power, npkts, axs[2], "Packet Loss - Low TX Power")

    for ax in axs.flat:
        ax.set(xlabel="# simulations", ylabel="% pkt loss")
    for ax in axs.flat:
        ax.label_outer()

    plt.show()

if __name__ == "__main__":
    main()
