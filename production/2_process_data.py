# process_data.py
# Functions to format the data and create new features

import os
import pickle
import logging
from glob import glob
from datetime import datetime, date
from time import sleep

from dateutil.parser import parse
from inflection import parameterize
import numpy as np

import s3_helper


def format_price(price_value):
    "Remove extra text and convert to int"
    try:
        price = int(price_value.replace('$', ''))
    except:
        price = np.nan

    return price


def format_size(size_value):
    "Remove extra text and convert to int"
    try:
        size = int(size_value.replace('Size: ', ''))
    except:
        size = np.nan

    return size


def format_brand(brand_value):
    "Make universal format"
    try:
        brand = parameterize(brand_value, '_')
    except:
        brand = ''

    return brand


def format_link(link_value):
    "Add domain to link value"
    try:
        link = 'http://www.poshmark.com' + link_value
    except:
        link = ''

    return link


def format_date(date_value):
    "Convert string date to datetime"
    try:
        date = parse(date_value)
    except:
        date = np.nan

    return date


def format_record(record):
    "Format individual values of the record"
    record['price'] = format_price(record['price'])
    record['size'] = format_size(record['size'])
    record['brand'] = format_brand(record['brand'])
    record['link'] = format_link(record['link'])
    record['date'] = format_date(record['date'])

    return record


def find_diff(date):
    "Find the amount of days an item has been listed"
    try:
        now = datetime.now()
        diff = abs((date-now).days)
    except:
        diff = np.nan

    return diff


def calculate_length(title):
    "Find the length of the title"
    try:
        length = len(title)
    except:
        length = np.nan

    return length


def identify_condition(status):
    "Create boolean value for condition status"
    try:
        condition = bool(status)
    except:
        condition = False

    return condition


def check_stock(stock):
    "Create boolean value for stock status"
    try:
        condition = bool(stock)
    except:
        condition = False

    return condition


def create_features(record):
    "Create new features from record data"
    record['diff'] = find_diff(record['date'])
    record['length'] = calculate_length(record['title'])
    record['nwt'] = identify_condition(record['status'])
    record['sold'] = check_stock(record['stock'])

    return record


if __name__ == '__main__':
    files = s3_helper.list_files('raw')

    for f in files:
        path = 'data/'
        s3_helper.download_file(f, path)
        print('Processing', f)
        store = pickle.load(open(path + f, 'rb'))
        format_store = [format_record(item) for item in store]
        feature_store = [create_features(item) for item in format_store]
        file_name = f.replace("raw", "processed")

        pickle.dump(feature_store, open(path + file_name, 'wb'))

        s3_helper.upload_file(file_name, path)
        print('Uploaded: ', file_name, 'to S3')
