import os
import time

import pandas as pd
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.stemmers import Stemmer
from collections import defaultdict
from sumy.utils import get_stop_words

# Initialize LexRankSummarizer and Tokenizer
stemmer = Stemmer("english")
summarizer = LsaSummarizer(stemmer)
tokenizer = Tokenizer("english")
summarizer.stop_words = get_stop_words("english")


def increase_weight_for_key_words(sentences, key_words):
    sentence_weights = defaultdict(float)

    for sentence in sentences:
        for word in key_words:
            if word.lower() in str(sentence).lower():
                sentence_weights[sentence] += 1
    return sentence_weights


def new_sum(text, key_words, num_sentences):
    parser = PlaintextParser.from_string(text, tokenizer)
    initial_summary = summarizer(parser.document, num_sentences)
    # Increase weight
    sentence_weights = increase_weight_for_key_words(parser.document.sentences, key_words)

    # Combine weights from initial summary with additional weights
    for sentence in initial_summary:
        sentence_weights[sentence] += 1  # Initial summary sentences get additional weight

    # Select top sentences as final summary
    final_summary = sorted(sentence_weights, key=sentence_weights.get, reverse=True)[:num_sentences]

    # Output final summary
    final_summary_text = " ".join(str(sentence) for sentence in final_summary)

    return final_summary_text


def from_csv_summarize(folder_path, saving_path):
    # Get list of all CSV files in the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    a = time.time()
    # Iterate through each CSV file
    for csv_file in csv_files:
        print(csv_file)
        # Build complete file path
        file_path = os.path.join(folder_path, csv_file)

        # Read CSV file
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="Windows-1252")
        symbol = csv_file.split(".")[0].upper()
        # AAPL
        df.columns = df.columns.str.capitalize()
        key_words_value = {symbol}
        num_sentences_value = 3
        # text_ratio = 0.25
        # Process text column, here simply applying new_sum function to Text column
        df['New_text'] = df['Text'].apply(new_sum, key_words=key_words_value, num_sentences=num_sentences_value)
        # df['New_text'] = df['Text'].apply(summarize, num_sentences=num_sentences_value)
        # Remove redundant rows
        df = df.drop(columns=['Text'])
        # Remove rows where Mark is not 1
        df = df[df['Mark'] == 1]
        print(time.time()-a, "s")
        # Save modified DataFrame to CSV file
        df.to_csv(os.path.join(saving_path, symbol.upper()+".csv"), index=False)


if __name__ == "__main__":
    # headline_path = "headline_files_dated"
    headline_path = "news_data_preprocessed"
    headline_saving_path = "news_data_summarized"
    from_csv_summarize(headline_path, headline_saving_path)
    # key_words = {'AAPL', 'invest'}
    # new_sum(text, key_words, 4)
    # summarize(text, 4)

