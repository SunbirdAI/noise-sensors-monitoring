import os

def parse_file(file):
    """
    Read in the file, parse it and return a list of the relevant metrics
    """
    metrics = []
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line.strip()
            metrics_list = line.split(",")
            decibel_string = metrics_list[0]
            time_uploaded_string = metrics_list[1]
            decibel = float(decibel_string.split(":")[1])
            time_uploaded = time_uploaded_string[3:]
            metrics.append((decibel, time_uploaded))
    return metrics

if __name__ == '__main__':
    # print(os.getcwd())
    file = os.getcwd() + "/dblog.txt"
    metrics = parse_file(file)
    print(metrics)
