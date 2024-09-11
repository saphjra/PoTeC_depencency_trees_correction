import re
# Let's first take a look at the contents of the file to understand its structure and identify any inconsistencies.
file_path = 'manually_corrected_constituency_trees.tsv'

# Reading the file to examine its content
with open(file_path, 'r') as file:
    content = file.readlines()

# Splitting the lines into columns and checking for consistency in the number of fields per line

# Splitting the lines based on tab separator
lines = [line.strip().split('\t') for line in content]

# Get the number of columns based on the header
expected_num_columns = len(lines[0])
#print(expected_num_columns)
# Check for inconsistencies in the number of columns per row
inconsistent_rows = []
for i, row in enumerate(lines[1:], 1):  # Skip header (first row)
    if len(row) != expected_num_columns:
        inconsistent_rows.append((i, len(row)))
#print(inconsistent_rows)
# Display any rows with inconsistent number of columns


def extract_constituents_from_tree(tree_str):
    """
    This function extracts the constituents from the constituency_tree field by
    removing the syntactic labels and brackets, leaving just the tokens.
    """
    # Using a regex to remove anything in parentheses
    return re.findall(r"\b\w[\w-]*\b", tree_str)


# Check consistency between constituency_tree, str_constituents, and pos_tags
inconsistencies = []

for i, row in enumerate(lines[1:], 1):  # Skip the header
    if len(row) == expected_num_columns:  # Only check well-formed rows
        constituency_tree = row[3]
        # constituency_tree =  re.sub(r'[()]', '', constituency_tree).split(" ")
        str_constituents = re.sub(r'[\[\]\']','',(row[4]))  # Assuming it's a string representation of a list
        pos_tags = eval(row[5])  # Assuming it's a string representation of a list

        # Extract constituents from the constituency_tree
        constituents_from_tree = extract_constituents_from_tree(constituency_tree)
        constituents_from_string = extract_constituents_from_tree(str_constituents)
        # Check if the extracted constituents match the str_constituents
        if constituents_from_string != constituents_from_tree:
            inconsistencies.append((i, 'constituents mismatch', constituency_tree, str_constituents))

        # Check if the number of pos_tags matches the number of extracted constituents
       # if len(pos_tags) != len(extracted_constituents):
       #     inconsistencies.append((i, 'pos_tags length mismatch', len(extracted_constituents), len(pos_tags)))


# Save the problematic rows to a new file for further review
output_path = 'problematic_constituency_rows.txt'

# Writing the problematic rows into a new TSV file
with open(output_path, 'w') as f:
    # Show inconsistencies found
    print(len(inconsistencies))
    for line in inconsistencies:
        print(f"{line[0]} \n{line[2]}\n{line[3]}", file= f)



