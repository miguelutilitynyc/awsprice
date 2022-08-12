import json
import boto3

pricing_client = boto3.client('pricing', region_name='us-east-1')

def ec2_get_ondemand_prices(Filters):
  data  = []
  reply = pricing_client.get_products(ServiceCode='AmazonEC2', Filters=Filters, MaxResults=100)
  data.extend([json.loads(r) for r in reply['PriceList']])
  while 'NextToken' in reply.keys():
    reply = pricing_client.get_products(ServiceCode='AmazonEC2', Filters=Filters, MaxResults=100, NextToken=reply['NextToken'])
    data.extend([json.loads(r) for r in reply['PriceList']])
    print(f"\x1b[33mGET \x1b[0m{len(reply['PriceList']):3} \x1b[94m{len(data):4}\x1b[0m")

  instances = {}
  for d in data:
    attr = d['product']['attributes']
    type = attr['instanceType']
    if type in data:  continue

    region  = attr.get('location',              '')
    clock   = attr.get('clockSpeed',            '')
    type    = attr.get('instanceType',          '')
    market  = attr.get('marketoption',          '')
    ram     = attr.get('memory',                '')
    os      = attr.get('operatingSystem',       '')
    arch    = attr.get('processorArchitecture', '')
    region  = attr.get('regionCode',            '')
    storage = attr.get('storage',               '')
    tenancy = attr.get('tenancy',               '')
    usage   = attr.get('usagetype',             '')
    vcpu    = attr.get('vcpu',                  '')

    terms    = d['terms']
    ondemand = terms['OnDemand']

    ins      = ondemand[next(iter(ondemand))]
    pricedim = ins['priceDimensions']
    price    = pricedim[next(iter(pricedim))]
    desc     = price['description']
    p        = float(price['pricePerUnit']['USD'])
    unit     = price['unit'].lower()

    if 'GiB' not in ram: print('\x1b[31mWARN\x1b[0m')
    if 'hrs'!=unit:      print('\x1b[31mWARN\x1b[0m')

    if p==0.: continue
    instances[type] = {'type':type, 'market':market, 'vcpu':vcpu, 'ram':float(ram.replace('GiB','')), 'ondm':p, 'unit':unit, 'terms':list(terms.keys()), 'desc':desc}

  instances = {k:v for k,v in sorted(instances.items(), key=lambda e: e[1]['ondm'])}
  for ins in instances.values():
    p = ins['ondm']
    print(f"{ins['type']:32} {ins['market'].lower()}\x1b[91m: \x1b[0m{ins['vcpu']:3} vcores\x1b[91m, \x1b[0m{ins['ram']:7.1f} GB, \x1b[0m{p:7.4f} \x1b[95m$/h\x1b[0m, \x1b[0m\x1b[0m{p*720:8,.1f} \x1b[95m$/m\x1b[0m, \x1b[0m\x1b[0m{p*720*12:7,.0f} \x1b[95m$/y\x1b[0m, \x1b[0m{ins['unit']}\x1b[91m, \x1b[0m{ins['terms']}\x1b[0m")
    # print(desc, , sep='\n')

  print(f'\x1b[92m{len(instances)}\x1b[0m')

flt = [
  # {'Field': 'instanceType',    'Value': 't4g.nano',  'Type': 'TERM_MATCH'},  # enable this filter to select only 1 instance type
  {'Field': 'regionCode',      'Value': 'us-east-2', 'Type': 'TERM_MATCH'},  # alternative notation?: {'Field': 'location', 'Value': 'US East (Ohio)', 'Type': 'TERM_MATCH'},
  {'Field': 'operatingSystem', 'Value': 'Linux',     'Type': 'TERM_MATCH'},
  {'Field': 'tenancy',         'Value': 'shared',    'Type': 'TERM_MATCH'},
  {'Field': 'capacitystatus',  'Value': 'Used',      'Type': 'TERM_MATCH'},
]
ec2_get_ondemand_prices(Filters=flt)