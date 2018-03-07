# -*- coding: utf-8 -*-

import re
import math
from dateutil.parser import parse


def to_datetime(data):
    """
    Convert string to datetime obj
    """
    return parse(data)


def serialize_number(data):
    return re.sub(r'[^0-9]', '', data) if data else data


def serialize_name(data):
    """
    Dee Thomas (Realtor-Keller Williams) => Dee Thomas
    """
    return re.sub(r'\(.+\)', '', data).strip() if data else data.strip()


def acres_to_sqft(data):
    """
    Convert acres to sqft
    """
    if 'acre' in data:
        number = re.search(r'([0-9\.\,]+)', data).group(1)
        return math.floor(float(number) * 43560)
    return serialize_number(data)


def rename_label(name):
    return '_'.join([x.lower() for x in name.split()])

