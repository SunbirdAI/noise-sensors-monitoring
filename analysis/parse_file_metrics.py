def parse_file(file, device_id):
    """
    Read in the file, parse it and return a list of the relevant metrics
    """
    metrics = []
    with file.open('r') as f:
        lines = f.readlines()
        for line in lines:
            line.strip()
            metrics_list = str(line).split(",")
            decibel_string = metrics_list[0]
            time_uploaded_string = metrics_list[1]
            decibel = float(decibel_string.split(":")[1])
            time_uploaded = time_uploaded_string[3:]
            metrics.append({'device_id': device_id, 'db_level': decibel, 'date': time_uploaded})
    return metrics
