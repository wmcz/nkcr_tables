import sys
import json
import csv


##
# Convert to string keeping encoding in mind...
##
def to_string(s):
    try:
        return str(s)
    except:
        # Change the encoding type if needed
        return s.encode('utf-8')

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def move():
    # Reading arguments
    node = "features"
    name = "pam_2010"
    json_file_path = name+".json"
    csv_file_path = name+".csv"

    fp = open(json_file_path, 'r')
    json_value = fp.read()
    raw_data = json.loads(json_value)

    try:
        data_to_be_processed = raw_data[node]
    except:
        data_to_be_processed = raw_data

    processed_data = []
    header = []
    first = True
    for item in data_to_be_processed:
        attr = item['attributes']
        geo = item['geometry']
        reduced_item = merge_two_dicts(attr, geo)

        # if first:
        header += reduced_item.keys()
            # first = False

        processed_data.append(reduced_item)

    header = list(set(header))
    header.sort()

    with open(csv_file_path, 'w+') as f:
        writer = csv.DictWriter(f, header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in processed_data:
            writer.writerow(row)

    print("Just completed writing csv file with %d columns" % len(header))

move()