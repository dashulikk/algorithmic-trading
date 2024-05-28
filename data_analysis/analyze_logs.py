import matplotlib.pyplot as plt


def analyze_logs(filename, save_location):
    with open(filename, 'r') as file:
        data = [float(line.strip()) for line in file]

    plt.figure(figsize=(10, 6))
    plt.plot(data, label='Net Worth')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Net Worth Over Time')
    plt.legend()
    plt.grid(True)

    plt.savefig(save_location)
    plt.close()

#analyze_logs('../logs/transaction_cost_bot.txt', 'transaction_cost.png')
#analyze_logs('../logs/no_transaction_cost_bot.txt', 'no_transaction_cost.png')
