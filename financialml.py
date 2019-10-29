from os import listdir
from os.path import isfile, join
from ofxparse import OfxParser
import pandas as pd
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

UNCATEGORIZED = 'uncategorized'

def load_ofxs(path):
    files = []
    for f in listdir(path):
        if isfile(join(path, f)) and 'ofx' in f:
            file_path = join(path, f)
            files.append(file_path)
    return files

def get_label(phrase, words_df):
    for index, row in words_df.iterrows():
        if row['word'].lower() in phrase.lower():
            return row['label']

    # return np.nan
    return UNCATEGORIZED

def parse_file(file, transactions_data, words_df):
    print(file)
    total_file = 0.0
    competency = None
    with open(file, encoding="ISO-8859-1") as fileobj:
        ofx = OfxParser.parse(fileobj)
        for transaction in ofx.account.statement.transactions:
            if transaction.amount < 0:
                label = get_label(transaction.memo, words_df)
                day = transaction.date.strftime("%Y-%m-%d")
                month = transaction.date.strftime("%Y-%m")
                year = transaction.date.year
                transactions_data.append(
                    [
                        transaction.memo,
                        transaction.amount,
                        day,
                        month,
                        year,
                        label
                    ]
                )
                # print(transaction.memo, "\t", transaction.amount, "\t", label)

    return transactions_data

def plot_pie(title, plt, items, total, the_grid, s, e):
    labels = []
    fracs = []
    for item in items:
        labels.append(item[0])
        percentage = item[1]/total
        fracs.append(percentage)

    # Make square figures and axes

    plt.subplot(the_grid[s, e], aspect=1)
    plt.title(title)

    plt.pie(fracs, labels=labels, autopct='%1.1f%%', shadow=True)


if __name__ == '__main__':
    paths = ['./extratos/bb/', './extratos/bradesco/', './extratos/inter/']
    words_df = pd.read_csv('datasets/words.csv', delimiter=";", names=['word', 'label'])
    # print(words_df)
    transactions_data = []

    total = 0.0
    totals = {}

    for path in paths:
        for file in load_ofxs(path):
            parse_file(file, transactions_data, words_df)

    df = pd.DataFrame(transactions_data, columns = ['memo', 'amount', 'day', 'month', 'year', 'label'])
    df.to_csv('datasets/extratos.csv')
    df2 = df[df.label == UNCATEGORIZED]
    print(df2.groupby(['memo'])['memo'].count())
    despesas_by_label = {}
    total = {}
    # df.loc[df['label']!='cartao']
    for index, row in df.iterrows():
        year, month, label = row['year'], row['month'], row['label']
        # if year not in despesas_by_label:
        #     despesas_by_label[year] = {}

        if month not in despesas_by_label:
            despesas_by_label[month] = {}
            total[month] = Decimal(0.0)

        if label not in despesas_by_label[month]:
            despesas_by_label[month][label] = Decimal(0.0)

        if label != 'cartao':
            despesas_by_label[month][label] += row['amount']
            total[month] += row['amount']

    # despesas_by_label.pop('cartao', None)
    # print(despesas_by_label)
    # print(despesas_by_label.items())

    grouping_df = df.groupby(['year', 'month', 'label'])['amount'].sum()
    grouping_df.to_csv('datasets/totais.csv')
    print(grouping_df)

    # the_grid = GridSpec(3, 4)
    # s = 0
    # e = 0
    # for despesas in despesas_by_label.items():
    #     m = despesas[0]
    #     if e > 3:
    #         s += 1
    #         e = 0
    #     print(s,e,m)
    #     plot_pie(str(m), plt, despesas_by_label[m].items(), total[m], the_grid, s, e)
    #     e += 1
    # plt.show()

