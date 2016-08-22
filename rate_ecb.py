#!/usr/bin/env python2
'''rate from Euro Central Bank
Argentine peso          ARS
Australian dollar       AUD
Bulgarian lev           BGN
Brazilian real          BRL
Canadian dollar         CAD
Swiss franc             CHF
Chinese yuan renminbi   CNY
Czech koruna            CZK
Danish krone            DKK
Algerian dinar          DZD
Euro                    EUR
UK pound sterling       GBP
Hong Kong dollar        HKD
Croatian kuna           HRK
Hungarian forint        HUF
Indonesian rupiah       IDR
Israeli shekel          ILS
Indian rupee            INR
Japanese yen            JPY
Korean won (Republic)   KRW
Moroccan dirham         MAD
Mexican peso            MXN
Malaysian ringgit       MYR
Norwegian krone         NOK
New Zealand dollar      NZD
Philippine peso         PHP
Polish zloty            PLN
Romanian leu            RON
Russian rouble          RUB
Swedish krona           SEK
Singapore dollar        SGD
Thai baht               THB
Turkish lira            TRY
New Taiwan dollar       TWD
US dollar               USD
South African rand      ZAR
'''
import sys
from getopt import getopt, GetoptError
from datetime import datetime
try:
    from datetime.datetime import strptime
except:
    from time import strptime
from urllib2 import Request, urlopen, HTTPError
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print('ImportError')
        sys.exit(1)


CURRENCY = 'ARS,AUD,BGN,BRL,CAD,CHF,CNY,CZK,DKK,DZD,EUR,GBP,HKD,HRK,HUF,IDR,ILS,INR,JPY,KRW,MAD,MXN,MYR,NOK,NZD,PHP,PLN,RON,RUB,SEK,SGD,THB,TRY,TWD,USD,ZAR'
REVERSE_RATE = False


def using():
    '''help for using'''
    print('%s --currFrom=USD --currTo=EUR --startPeriod=2016-08-01 --endPeriod=2016-08-10' % (sys.argv[0],))
    sys.exit(0)


def opt_parse():
    '''parsing input options'''
    opts = dict()
    #param1 = 'f:t:b:e:h'
    paramShort = ''
    paramLong = ['currFrom=', 'currTo=', 'startPeriod=', 'endPeriod=']
    try:
        opts, args = getopt(sys.argv[1:], paramShort, paramLong)
    except GetoptError:
        print('GetoptError')
        sys.exit(1)
    opts = dict(opts)
    return opts


def validate(opts):
    '''validate options'''
    try:
        currFrom = opts['--currFrom']
        currTo = opts['--currTo']
        startPeriod = opts['--startPeriod']
        endPeriod = opts['--endPeriod']
    except KeyError:
        raise ValueError
    if not currFrom in CURRENCY.split(','):
        raise ValueError
    if not currTo in CURRENCY.split(','):
        raise ValueError
    if not currFrom == 'EUR' and not currTo == 'EUR':
        raise ValueError
    if currFrom == currTo:
        raise ValueError
    try:
        startPeriod = strptime(startPeriod, '%Y-%m-%d')
        endPeriod = strptime(endPeriod, '%Y-%m-%d')
    except ValueError:
        raise ValueError


def get_json(currFrom, currTo, startPeriod, endPeriod):
    '''get json from ecb'''
    if currFrom == 'EUR':
        global REVERSE_RATE
        REVERSE_RATE = True
        currTemp = currFrom
        currFrom = currTo
        currTo = currTemp
    #ecb_url = 'https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?startPeriod=2016-08-01&endPeriod=2016-08-02'
    ecb_url = 'https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D.%s.%s.SP00.A?startPeriod=%s&endPeriod=%s' % (currFrom, currTo, startPeriod, endPeriod)
    req = Request(ecb_url)
    req.add_header('Accept', 'application/vnd.sdmx.data+json;version=1.0.0-cts')
    try:
        resp = urlopen(req)
    except HTTPError:
        print('HTTPError')
        sys.exit(1)
    content = resp.read()
    return content


if __name__ == '__main__':
    '''main loop'''
    rates = dict()
    opts = opt_parse()
    try:
        validate(opts)
    except ValueError:
        print('ValueError')
        sys.exit(1)
    try:
        data_json = get_json(currFrom=opts['--currFrom'], currTo=opts['--currTo'],
                             startPeriod=opts['--startPeriod'], endPeriod=opts['--endPeriod'])
        data_json = json.loads(data_json)
        #open('ecb_rate.json', 'w').write(json.dumps(data_json, sort_keys=True, indent=4))
        rates = data_json['dataSets'][0]['series']['0:0:0:0:0']['observations']
        rates = dict([(int(key), rates[key][0]) for key in rates])

        dates = data_json['structure']['dimensions']['observation'][0]['values']
        dates = [key['id'] for key in dates]

        rates = dict([(dates[key], rates[key]) for key in rates])

    except KeyError:
        print('JsonError')
        sys.exit(1)
    for key in sorted(rates):
        key_str = key.split('-')
        key_str.reverse()
        key_str = '-'.join(key_str)
        if not REVERSE_RATE:
            print key_str, rates[key]
        else:
            print key_str, 1/rates[key]
