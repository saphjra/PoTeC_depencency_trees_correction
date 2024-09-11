import pandas as pd
import sys
# Load the TSV file into a DataFrame
file_path = 'manually_corrected_dependency_trees.tsv'  # Update this with the correct path
df = pd.read_csv(file_path, header=0, sep='\t')

# Function to check for inconsistencies in dependency relationships
def check_dependency_inconsistencies(df):
    inconsistencies = []

    # Iterate over the rows of the dataframe
    for index, row in df.iterrows():
        word = row['spacy_word']
        head = row['dependency_head']
        head_pos = row['dependency_head_pos']
        head_children = row['dependency_children']

        # Check if the word is a child of its head in any row
        if head != "ROOT":
            head_row = df[(df['spacy_word'] == head) & (df['text_id'] == row['text_id']) & (df['sent_index_in_text'] == row['sent_index_in_text'])]

            if not head_row.empty:
                head_children_list = head_row.iloc[0]['dependency_children']
                head_tag = head_row.iloc[0]['spacy_pos']

                # If the word is not found in the head's children list, log an inconsistency
                try:
                    if word not in head_children_list:
                        inconsistencies.append({
                        'type': 'dependency_inconsistency',
                        'word': word,
                        'head': head,
                        'expected_in_head_children': word,
                        'head_children_found': head_children_list
})
                except TypeError:
                    print(f"Error: {head_children_list}, {word},{index}")
                # Check for POS tag consistency between head and dependency_head_pos
                if head_tag != head_pos:
                    inconsistencies.append({
                        'type': 'pos_inconsistency',
                        'word': word,
                        'head': head,
                        'expected_head_pos': head_tag,
                        'found_head_pos': head_pos
                    })

    return inconsistencies

# Run the function to find inconsistencies
inconsistencies = check_dependency_inconsistencies(df)

sys.stdout = open('problematic_dependency_rows.txt','wt', encoding='utf-8')

print(len(inconsistencies))

    # Show the inconsistencies
if inconsistencies:
    for inconsistency in inconsistencies:
        if inconsistency['type'] == 'dependency_inconsistency':
            print(f"[Dependency Inconsistency] Word: {inconsistency['word']}, Head: {inconsistency['head']}")
            print(f"Expected in head's children: {inconsistency['expected_in_head_children']}")
            print(f"Head's children found: {inconsistency['head_children_found']}\n")
        elif inconsistency['type'] == 'pos_inconsistency':
            print(f"[POS Inconsistency] Word: {inconsistency['word']}, Head: {inconsistency['head']}")
            print(f"Expected POS of head: {inconsistency['expected_head_pos']}")
            print(f"Found POS of head: {inconsistency['found_head_pos']}\n")
else:
    print("No inconsistencies found.")
