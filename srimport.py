import csv, os, urllib.parse
import pandas as pd
import re

col_sku         = 'SKU'
col_name        = 'Name'
col_piece       = 'Piece'
col_desc        = 'Description'
col_reg_price   = 'Regular price'
col_images      = 'Images'

def read_csv_file(filename):
    """
    Reads a UTF-8 encoded CSV file and returns its contents as a list of dictionaries.

    Parameters:
        filename (str): The name of the CSV file to read.

    Returns:
        A list of dictionaries representing the contents of the CSV file.
    """
    data = []
    with open(filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def read_excel_file(filename):
    """
    Reads an Excel file and returns a dictionary.

    Args:
        filename (str): The name of the Excel file to read.

    Returns:
        A dictionary representing the data in the Excel file.
    """
    # Load the Excel file into a pandas DataFrame
    df = pd.read_excel(filename)
    
    # Convert the DataFrame to a dictionary
    #data = df.to_dict()
     # Convert the DataFrame to a list of dictionaries
    data = df.to_dict(orient='records')   
    
    # Return the dictionary
    return data

def write_csv_file(filename, data):
    """
    Writes a list of dictionaries to a UTF-8 encoded CSV file.

    Parameters:
        filename (str): The name of the CSV file to write to.
        data (list of dicts): The data to write to the CSV file.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys() if len(data) > 0 else []
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def write_csv_file2(filename, data, num_rows=1000):
    """
    Writes a list of dictionaries to a UTF-8 encoded CSV file, splitting into multiple files if necessary.

    Parameters:
        filename (str): The base name of the CSV files to write to.
        data (list of dicts): The data to write to the CSV file.
        num_rows (int): The maximum number of rows per file. Default is 1000.
    """
    # Calculate number of files needed
    num_files = 1 + (len(data) - 1) // num_rows

    # Create directory to store CSV files
    if not os.path.exists(filename):
        os.makedirs(filename)

    # Write data to CSV files
    for i in range(num_files):
        start = i * num_rows
        end = min(start + num_rows, len(data))
        filename_i = os.path.join(filename, f"{i}.csv")
        with open(filename_i, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[start].keys() if len(data[start:end]) > 0 else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data[start:end]:
                writer.writerow(row)


def get_image_list(directory, url_base):
    img_list = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            url = directory + '/' + filename
            encoded_url = urllib.parse.quote(url)
            url = url_base + '/' +  encoded_url
            #url = os.path.join(directory, filename)
            #encoded_url = urllib.parse.quote(url)
            #url = url_base + '/' +  encoded_url
            img_list.append(url)
    return img_list

def process_images(data):
    if col_images not in data[0]:
        print(f"Warning: data has no column '{col_images}'")
    else:
        for i in range(len(data)):
            row = data[i]
            for label in row:
                if label == 'Images':
                    dir = row[label].lstrip().rstrip()
                    #print(dir)
                    if os.path.isdir(dir):
                        img_list = get_image_list(dir, 'https://blackdot.io/photos')
                        data[i][label] = ','.join(img_list)
                        print(img_list)
                    else:
                        print(f"{dir} does not exist.")
            
    return data



def add_div_tag_product_description(str_input):
    return '<div class="product-description">' + str_input + '</div>'

# remove a word from a string regardless of case and any surrounding spaces
def remove_substring(string, substring):
    return string.lower().replace(substring.lower(), '').strip()

# take a dictionary and output a html table
def string_to_dict(inventory_string):
    inventory_dict = {}
    for line in inventory_string.splitlines():
        if '#' in line:
            stock, dye_lot = line.split('#')
            inventory_dict['Stock'] = inventory_dict.get('Stock', []) + [stock.strip()]
            inventory_dict['Dye Lot'] = inventory_dict.get('Dye Lot', []) + [('#' + dye_lot.strip())]
        else:
            inventory_dict['Stock'] = inventory_dict.get('Stock', []) + [line.strip()]
            inventory_dict['Dye Lot'] = inventory_dict.get('Dye Lot', []) + ['']
    return inventory_dict

def dict_to_html_table(data_dict, table_class=''):
    html = f'<table class="{table_class}">\n<tr>'
    for key in data_dict.keys():
        html += '<th>' + str(key) + '</th>'
    html += '</tr>\n'
    for i in range(len(data_dict['Stock'])):
        html += '<tr>'
        for key in data_dict.keys():
            html += '<td>' + str(data_dict[key][i]) + '</td>'
        html += '</tr>\n'
    html += '</table>'
    return html

def split_at_msrp(string):
    split_string = string.split("MSRP:")
    if len(split_string) > 1:
        return split_string[0].strip(), "MSRP:" + split_string[1].strip()
    else:
        return string.strip(), None


def string_to_product_table(string, table_class='product-table-details'):
    rows = string.split('\n')
    html = f'<table class="{table_class}">\n'
    for row in rows:
        if row.strip() != '':
            if ':' in row:
                label, value = row.split(':', 1)
                html += '<tr>\n'
                html += f'<td class="label">{label.strip().capitalize()}</td>\n'
                html += f'<td class="value">{value.strip().capitalize()}</td>\n'
                html += '</tr>\n'
            else:
                html += '<tr>\n'
                html += f'<td class="item">{row.strip().capitalize()}</td>\n'
                html += '<td></td>\n'
                html += '</tr>\n'
    html += '</table>'
    return html




# 
# split description at MSRP
# convert data after MSRP into structured table
# add a div to description
def process_description(data):
    if col_desc not in data[0]:
        print(f"Warning: data has no column '{col_desc}'")
    else:
        for i in range(len(data)):
            desc = data[i][col_desc].lstrip().rstrip()
            
            part1, part2 = split_at_msrp(desc)
            
            if part2:
                table = string_to_product_table(part2)
            else:
                table = ''
                print(f"Warning: SKU: '{data[i][col_sku]}' is missing MSRP")
            
            desc = add_div_tag_product_description(part1)+add_div_tag_product_description(table)
            
            data[i][col_desc] = desc
    
    return data

def description_normalize_msrp(description):
    """
    Normalizes occurrences of 'msrp' in a string, regardless of case, to 'MSRP'.

    Args:
        description (str): The input string to normalize.

    Returns:
        str: The normalized string.
    """
    # use a regular expression to replace 'msrp' with 'MSRP', regardless of case
    normalized_description = re.sub(r'\bmsrp\b', 'MSRP', description, flags=re.IGNORECASE)
    
    return normalized_description

def process_description_normalize_msrp(data):
    if col_desc not in data[0]:
        print(f"Warning: data has no column '{col_desc}'")
    else:
        for i in range(len(data)):
            desc = data[i][col_desc].lstrip().rstrip()
            
            desc = description_normalize_msrp(desc)
            
            data[i][col_desc] = desc
            
    return data

# remove leading and trailing space from SKU numbers
def process_sku(data):
    for i in range(len(data)):
        row = data[i]
        for label in row:
            if label == 'SKU':
                sku = row[label].lstrip().rstrip()
                data[i][label] = sku
                #print(sku)
            
    return data

# capitlize first letter of each word, excpet for MSRP which will stay MSRP
def capitalize_words(input_string):
    # Split the input string into individual words
    words = re.split('(\s)', input_string)
    
    # Create an empty list to store the processed words
    capitalized_words = []
    i = 0
    while i < len(words):
        # If a word starts with 'MSRP' (ignoring case), add it to the list as is
        if words[i].upper().startswith('MSRP'):
            capitalized_words.append(words[i])
            i += 1
        else:
            capitalized_words.append(words[i].capitalize())
            i += 1
    return ''.join(capitalized_words)

def format_msrp(input_string):
    # Define the regex pattern for finding MSRP followed by a price
    pattern = r"(?i)MSRP\s*[$]?\s*(\d[\d,]*\.?\d{0,2})"

    # Define the replacement function for formatting the MSRP and price
    def replacement(match):
        price = match.group(1)
        return f"MSRP USD {price}"

    # Use re.sub() to find the MSRP pattern and replace it with the formatted version
    formatted_string = re.sub(pattern, replacement, input_string)

    return formatted_string


# remove leading, trailing space from name.  Replace any \n with space
def process_name(data):
    if col_name not in data[0]:
        print(f"Warning: data has no column '{col_name}'")
    else:
        for i in range(len(data)):
            name = data[i][col_name]
            name = name.lstrip().rstrip().replace('\n', ' ')
            name = capitalize_words(name)
            name = format_msrp(name)
            print(name)
            data[i][col_name] = name
                
    return data


# add price info to description
def process_pieces(data):
    if col_piece not in data[0]:
        print(f"Warning: data has no column '{col_piece}'")
    elif col_desc not in data[0]:
        print(f"Warning: data has no column '{col_desc}'")
    else:
        for i in range(len(data)):
            pieces = data[i][col_piece]
            if isinstance(pieces, str):
                pieces = pieces.lstrip().rstrip()
                pieces =  remove_substring(pieces, 'stock')
                pieces =  remove_substring(pieces, 'dye lot')
                pieces_dict = string_to_dict(pieces)
                #print(pieces_dict)
                pieces = dict_to_html_table(pieces_dict, table_class='product-table-pieces')
                #print(pieces)
                pieces = add_div_tag_product_description(pieces)
                data[i][col_desc] += pieces
    
    return data

# add price info to description
def process_pieces2(data):
    if col_piece not in data[0]:
        print(f"Warning: data has no column '{col_piece}'")
    elif col_desc not in data[0]:
        print(f"Warning: data has no column '{col_desc}'")
    else:
        for i in range(len(data)):
            pieces = data[i][col_piece]
            if isinstance(pieces, str):
                pieces = pieces.lstrip().rstrip()
                pieces = add_div_tag_product_description(pieces)
                data[i][col_desc] += pieces
    
    return data

def round_regular_price(data):
    if col_reg_price not in data[0]:
        print(f"Warning: data has no column '{col_reg_price}'")
    else:
        for i in range(len(data)):
            data[i][col_reg_price] = round(float(data[i][col_reg_price]), 0)
        
    return data

    # rounded_rows = []
    # for row in data:
    #     row['Regular price'] = round(float(row[col_reg_price]), 0)
    #     rounded_rows.append(row)
    # return rounded_rows


#import_filename = 'import-2023-05-13.xlsx'
import_filename = 'import.csv'
data_dir      = 'C:\\Users\\marci\\OneDrive\\silkresource\\data5'
#data_dir        = 'C:\\Users\\marci\\OneDrive\VA'

os.chdir(data_dir)

# List the contents of the current working directory
files = os.listdir()

# Print the list of files
print(files)

#data = read_excel_file(import_filename)
data = read_csv_file(import_filename)

#data = process_sku(data)
#data = process_name(data)
#data = process_description(data)
data = process_description_normalize_msrp(data)
#data = process_pieces2(data)
#data = round_regular_price(data)
#data = process_images(data)

write_csv_file2('out-test', data, 500)
