import csv
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import matplotlib.dates as md

def plot_single_file(file, x_axis, y_axis, title, label, loc, time_index, price_index, millisecond=False):
    fig, ax = plt.subplots(figsize=(20, 12), dpi=80)

    with open(file) as csvfile:
        time_range, price = [], []
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)
        for item in reader:
            time_range.append(int(item[time_index]) if not millisecond else int(item[time_index]) / 1000)
            price.append(float(item[price_index]))

        secs = md.epoch2num(time_range)
        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        plt.title(title)
        ax.ticklabel_format(style='plain', axis='y')
        ax.plot_date(secs, price, "b-", label=label)
        date_fmt = '%d-%m-%y'
        date_formatter = md.DateFormatter(date_fmt)
        ax.xaxis.set_major_formatter(date_formatter)
        fig.autofmt_xdate()
    legend = ax.legend(loc=loc, shadow=True, fontsize='x-large')
    plt.show()

def plot_multiple_files(files_config, x_axis, y_axis, title, loc, time_index, price_index, millisecond=False):
    fig, ax = plt.subplots(figsize=(20, 12), dpi=80)
    for f in files_config:
        with open(f[0]) as csvfile:
            time_range, price = [], []
            reader = csv.reader(csvfile, delimiter=',')
            next(reader, None)
            for item in reader:
                time_range.append(int(item[time_index]) if not millisecond else int(item[time_index]) / 1000)
                price.append(float(item[price_index]))
            secs = md.epoch2num(time_range)
            plt.xlabel(x_axis)
            plt.ylabel(y_axis)
            plt.title(title)
            ax.plot_date(secs, price, f[1], label=f[0].split("/")[3].split("-")[0])
            date_fmt = '%d-%m-%y'

            date_formatter = md.DateFormatter(date_fmt)
            ax.xaxis.set_major_formatter(date_formatter)
            fig.autofmt_xdate()
    legend = ax.legend(loc=loc, shadow=True, fontsize='x-large')
    plt.show()

def plot_fill_between(files, x_axis, y_axis, title, loc, time_index, price_index, millisecond=False):
    fig, ax = plt.subplots(figsize=(20, 12), dpi=80)
    rate = [[], []]
    for index, f in enumerate(files):
        with open(f[0]) as csvfile:
            time_range = []
            reader = csv.reader(csvfile, delimiter=',')
            next(reader, None)
            for item in reader:
                time_range.append(int(item[time_index]) if not millisecond else int(item[time_index]) / 1000)
                rate[index].append(float(item[price_index]))

            secs = md.epoch2num(time_range)
            plt.xlabel(x_axis)
            plt.ylabel(y_axis)
            plt.title(title)
            ax.plot_date(secs, rate[index], f[1], label=f[0].split("/")[2])
            date_fmt = '%d-%m-%y'

            date_formatter = md.DateFormatter(date_fmt)
            ax.xaxis.set_major_formatter(date_formatter)
            fig.autofmt_xdate()
    ax.fill_between(secs, rate[0], rate[1], color='blue', alpha=0.3)
    ax.fill_between(secs, rate[1], 0, color='red', alpha=0.3)
    legend = ax.legend(loc=loc, shadow=True, fontsize='x-large')
    plt.show()