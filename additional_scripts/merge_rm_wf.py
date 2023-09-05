#!/usr/bin/env python3
"""
TODO: clean again, r is never closed?
Call: python3 merge_rm_wf.py
To specify custom file paths see argparse arguments at the bottom of the file.
"""
import argparse
import csv
import os
from pathlib import Path

import pandas as pd
from tqdm import tqdm


def merge_rm_word_features(
        reading_measure_folder: str,
        word_features_folder: str,
        reader_ids_file: str,
        output_folder: str,
):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(reader_ids_file, 'r', encoding='utf8') as f:  # open file containing all reader ids as a list in one line
        reader_ids = [int(r) for r in sorted(f.readline().split('\t'))]

    texts = ['b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'p0', 'p1', 'p2', 'p3', 'p4', 'p5']

    # Read and merge data

    # Read text features
    for textIndex, text in tqdm(enumerate(texts), desc='Merging files...', total=len(texts)):
        filename_features = os.path.join(word_features_folder, 'word_features_' + text + '.csv')

        word_features = pd.read_csv(
            filename_features, sep='\t', na_values=['None', '.', 'NA'],
            usecols=['word', 'is_technical_term', 'word_index_in_sent', 'sent_index_in_text', 'word_length',
                     'word_index_in_text', 'is_in_quote', 'is_in_parentheses', 'is_clause_beginning',
                     'is_sent_beginning',
                     'is_abbreviation', 'contains_abbreviation', 'contains_hyphen', 'contains_symbol',
                     'type', 'lemma',
                     'lemma_length_chars', 'type_length_syllables',
                     'annotated_type_frequency_normalized', 'type_frequency_normalized',
                     'lemma_frequency_normalized', 'familiarity_normalized',
                     'regularity_normalized', 'document_frequency_normalized',
                     'sentence_frequency_normalized',
                     'cumulative_syllable_corpus_frequency_normalized',
                     'cumulative_syllable_lexicon_frequency_normalized',
                     'cumulative_character_corpus_frequency_normalized',
                     'cumulative_character_lexicon_frequency_normalized',
                     'cumulative_character_bigram_corpus_frequency_normalized',
                     'cumulative_character_bigram_lexicon_frequency_normalized',
                     'cumulative_character_trigram_corpus_frequency_normalized',
                     'cumulative_character_trigram_lexicon_frequency_normalized',
                     'initial_letter_frequency_normalized',
                     'initial_bigram_frequency_normalized',
                     'initial_trigram_frequency_normalized', 'avg_cond_prob_in_bigrams',
                     'avg_cond_prob_in_trigrams',
                     'neighbors_coltheart_higher_freq_cum_freq_normalized',
                     'neighbors_coltheart_higher_freq_count_normalized',
                     'neighbors_coltheart_all_cum_freq_normalized',
                     'neighbors_coltheart_all_count_normalized',
                     'neighbors_levenshtein_higher_freq_cum_freq_normalized',
                     'neighbors_levenshtein_higher_freq_count_normalized',
                     'neighbors_levenshtein_all_cum_freq_normalized',
                     'neighbors_levenshtein_all_count_normalized'],
            encoding='utf-8',
            engine='python',
        )

        # replace missing values with 0s (affects frequency measures: if word does not occur in corpus, frequency = 0)
        word_features = word_features.fillna(0)

        # add Eye movements data for each reader
        for readerIndex, reader in enumerate(reader_ids):
            filename_reading_measures = os.path.join(
                reading_measure_folder,
                'reader' + str(reader) + '_' + text + '_rm.csv'
            )
            reading_measure_csv = pd.read_csv(
                filename_reading_measures,
                sep='\t',
                na_values=['None', '.', 'NA'],
                usecols=['FRT', 'SL_out', 'TRC_in', 'FFD', 'FPRT', 'RPD_exc', 'TFT', 'RRT', 'FPF', 'FD', 'RR', 'Fix',
                         'LP', 'word_index_in_sent', 'SL_in', 'RPD_inc', 'FPReg', 'TRC_out', 'sent_index_in_text',
                         'SFD', 'RBRT', 'topic', 'trial', 'gender', 'major', 'expert_status', 'age', 'acc_bq_1',
                         'acc_bq_2', 'acc_bq_3', 'acc_tq_1', 'acc_tq_2', 'acc_tq_3', 'mean_acc_bq', 'mean_acc_tq',
                         'domain_expert_status', 'text_id', 'reader']
            )

            # sort columns. Necessary because different col ordering in different input files
            reading_measure_csv = reading_measure_csv[
                ["word_index_in_sent", "sent_index_in_text", "FFD", "SFD", "FD", "FPRT", "FRT", "TFT", "RRT", "RPD_inc",
                 "RPD_exc",
                 "RBRT", "Fix", "FPF", "RR", "FPReg", "TRC_out", "TRC_in", "LP", "SL_in", "SL_out", "acc_bq_1",
                 "acc_bq_2", "acc_bq_3", "acc_tq_1", "acc_tq_2", "acc_tq_3", "mean_acc_tq", "mean_acc_bq", "topic",
                 "trial",
                 "text_id", "reader", "gender", "major", "age", "expert_status", "domain_expert_status"]
            ]

            # concatenate text features with eye movements
            merged_df = pd.merge(word_features, reading_measure_csv,
                                 how='inner',
                                 left_on=['word_index_in_sent', 'sent_index_in_text'],
                                 right_on=['word_index_in_sent', 'sent_index_in_text'],
                                 suffixes=(None, '_rm'),
                                 )

            # write merged data
            filename_merged_data = os.path.join(output_folder, 'reader' + str(reader) + '_' + text + '_merged.csv')
            merged_df.to_csv(path_or_buf=filename_merged_data, header=True, na_rep='NA', sep='\t', index=False)


def create_parser():
    base_path = Path(os.getcwd()).parent
    pars = argparse.ArgumentParser()

    pars.add_argument(
        '--reading_measure_folder',
        default=base_path / 'eyetracking_data/reading_measures',
    )

    pars.add_argument(
        '--word_features_folder',
        default=base_path / 'stimuli/word_features',
    )

    pars.add_argument(
        '--reader_ids_file',
        default=base_path / 'participants/readerIDs.txt',
    )

    pars.add_argument(
        '--output_folder',
        default=base_path / 'eyetracking_data/reader_rm_wf',
    )

    return pars


if __name__ == '__main__':
    parser = create_parser()
    args = vars(parser.parse_args())
    merge_rm_word_features(**args)
