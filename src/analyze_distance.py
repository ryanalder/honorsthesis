import numpy as np
import matplotlib.pyplot as plt

def main():
    f = open("nodeData.txt")
    x, y = [], []
    for line in f:
        line = line.split()
        x.append(np.sqrt(float(line[2])**2 + float(line[3])**2)/1000)
        y.append(int(line[-1]))

    plt.plot(x, y, label="Data Rate")

    # hardcode LOS as determine through simulations
    plt.plot([31.2, 31.2], [1.8, 14.2], label="Loss of signal")
    plt.xlabel("Distance (km)")
    plt.ylabel("Data Rate")
    plt.grid()
    plt.legend()
    plt.title("Data Rate Change with Distance")
    plt.show()

if __name__ == "__main__":
    main()
