import argparse
import ast
import tkinter as tk
from tkinter import messagebox
import regex as re
from nltk import TreePrettyPrinter
from nltk.tree import ParentedTree
import pandas as pd


class SampleViewer:

    def __init__(self, root, file_path, languages: list, all_samples: bool, no_punctuation: bool, sentence_id: tuple):
        self.root = root
        self.sentence_id = sentence_id
        self.file_path = file_path
        self.data = pd.read_csv(file_path, sep='\t', encoding='utf-8', index_col='index')

        self.data = self.data.sort_values(by=['text_id_numeric', 'sent_index_in_text'])
        self.data.reset_index(inplace=True, drop=True, names='index')

        self.no_punctuation = no_punctuation
        # only iterate over those instances that we have not previously annotated
        self.temp_data = self.data
        if not all_samples:
            self.temp_data = self.temp_data[self.temp_data['needs_correction'].isna()]
        self.indices_gen = (i for i in self.temp_data.index.to_list()[self.sentence_id:])

        self.current_index = None
        self.prev_index = None

        self.text_label = tk.Label(root, text="Text ID:", font=("Courier", 15))
        self.text_label.pack(anchor='nw')
        self.id_label = tk.Label(root, text="Sent ID:", font=("Courier", 15))
        self.id_label.pack(anchor='nw')

        w = root.winfo_width()
        h = root.winfo_height()
        # Create a frame to hold the canvas and scrollbar
        self.tree_frame = tk.Frame(root, width=0-9*w, height=0.7*h)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas with a scrollbar
        self.tree_canvas = tk.Canvas(self.tree_frame)
        self.scrollbar_y = tk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree_canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree_canvas.xview)
        self.tree_canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.tree_canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox("all"))

        # Pack the scrollbar and canvas to the right side
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.tree_canvas.pack(side="left", fill="both", expand=True)

        self.ok_button = tk.Button(root, text="Continue", command=self.on_ok, font=("Courier", 16), pady=10)
        self.ok_button.pack(anchor='nw')
        self.correction_button = tk.Button(root, text="Needs Correction", command=self.on_correction, font=("Courier", 16), pady=10)
        self.correction_button.pack(anchor='w')

        self.show_sample()

    def show_sample(self):
        try:
            self.current_index = next(self.indices_gen)

            # the df is sorted such that first comes the premise and then the hypothesis in the same language
            # for one instance id
            sentence = self.data.iloc[self.current_index]

            self.text_label.config(text="Text ID: " + str(sentence['text_id']))
            self.id_label.config(text="ID: " + str(sentence['sent_index_in_text']))

            x = 20
            y = 5

            self.tree_canvas.create_text(x, 0, text='Sentence:', anchor=tk.NW, font=("Courier", 15), fill="black")
            for sent in ast.literal_eval(sentence['str_constituents']):
                print(ast.literal_eval(sentence['str_constituents']))
                #print(sentence['str_constituents'])


            #for sent in ast.literal_eval(sentence['str_constituents']):

                if self.no_punctuation:
                    sent = re.sub(r'\(\$.?.?.?\s.\)', '', sent)
                tree_str = '(' + sent + ')'
                tree = ParentedTree.fromstring(tree_str)
                tree_str = TreePrettyPrinter(tree).text(nodedist=4)
                self.tree_canvas.create_text(x, y, text=tree_str, anchor=tk.NW, font=("Courier", 15), fill="black")
                y += 500

            # update the canvas and scrollbar
            self.tree_canvas.pack()
            self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox("all"))
            self.scrollbar_y.pack(side="right", fill="y")
            self.scrollbar_x.pack(side="bottom", fill="x")
            self.root.update_idletasks()

        except StopIteration:
            self.root.destroy()
            return

    def on_ok(self):
        # always show two data points at a time, and update the index accordingly
        self.data.at[self.current_index, 'needs_correction'] = False
        self.continue_next_sample()

    def on_correction(self):
        self.data.at[self.current_index, 'needs_correction'] = True
        self.continue_next_sample()

    def continue_next_sample(self):
        self.data.to_csv(self.file_path, sep='\t', encoding='utf-8', index=True, index_label='index')
        self.id_label.config(text="")
        self.tree_canvas.delete("all")
        self.show_sample()


def parse_args():
    parser = argparse.ArgumentParser(description='Annotate samples manually')
    parser.add_argument(
        '--file_path',
        type=str,
        default='constituency_trees.tsv',
        help='Path to the file containing the samples'
    )

    parser.add_argument(
        '--languages', '-l',
        type=str,
        choices=['en', 'de', 'zh'],
        default=['en', 'de', 'zh'],
        nargs='+',
    )

    parser.add_argument(
        '--all-samples',
        action='store_true',
        help='Annotate all samples',
        default=True,
    )

    parser.add_argument(
        '--no-punctuation',
        action='store_true',
        help='removes punctuation from the sentences',
        default=True,
    )
    parser.add_argument(
        '--sentence-Id', '-id',
        type=int,
        help='Display chosen sentence based on the overall sentence Index in the dataset.',
        default=0,
    )
    return parser.parse_args()


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        clean_df(file_path)
        root.destroy()


def clean_df(file_path):
    data = pd.read_csv(file_path, sep='\t', encoding='utf-8', index_col='index')

    data.to_csv(file_path, sep='\t', encoding='utf-8', index=True, index_label='index')


if __name__ == "__main__":
    args = parse_args()
    sentence_Id = 0
    file_path = 'constituency_trees_1.tsv'
    #file_path = args.file_path
    root = tk.Tk()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.title("Sample Viewer")
    w, h = root.winfo_screenwidth()*.8, root.winfo_screenheight()*.8
    root.geometry("%dx%d+0+0" % (w, h))
    # root.attributes('-fullscreen', True)
    app = SampleViewer(root, file_path, args.languages, args.all_samples, args.no_punctuation, sentence_Id)
    root.mainloop()
