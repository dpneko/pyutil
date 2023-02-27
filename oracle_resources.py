import requests
import time
from statistics import mean

max_bandwidth = {}
max_energy = {}
max_bandwidth_year = {}
max_energy_year = {}
mean_bandwidth_year = {}
mean_energy_year = {}
total_bandwidths = {}
total_energys = {}
for address in ['TAoLn3VNX2zG9653jhqmF3gAU8eEBGbW7c', 'TAovhx3CJmuHjLpqfkS1Rtk7jHP7R6NsYe', 'TAoXG5TvUEV6ZGxKQPnySh5GSs4QTLTq9q', 'TAoJCXhF1815im33SiP1w1kf88wVHHN2Wo']:
    endtime = int(time.time()*1000)
    year_ago = endtime - 365 * 86400000
    bandwidths = requests.get(f"https://apilist.tronscanapi.com/api/account/analysis?address={address}&type=3&start_timestamp=1514764800000&end_timestamp={endtime}").json()['data']
    energys = requests.get(f"https://apilist.tronscanapi.com/api/account/analysis?address={address}&type=2&start_timestamp=1514764800000&end_timestamp={endtime}").json()['data']
    bandwidths = {b['day']: b['net_usage_total'] for b in bandwidths}
    energys = {e['day']: e['energy_usage_total'] for e in energys}
    max_bandwidth[address] = max(bandwidths.values())
    max_energy[address] = max(energys.values())

    bandwidths_year = requests.get(f"https://apilist.tronscanapi.com/api/account/analysis?address={address}&type=3&start_timestamp={year_ago}&end_timestamp={endtime}").json()['data']
    energys_year = requests.get(f"https://apilist.tronscanapi.com/api/account/analysis?address={address}&type=2&start_timestamp={year_ago}&end_timestamp={endtime}").json()['data']
    bandwidths_year = {b['day']: b['net_usage_total'] for b in bandwidths_year}
    energys_year = {e['day']: e['energy_usage_total'] for e in energys_year}
    max_bandwidth_year[address] = max(bandwidths_year.values())
    max_energy_year[address] = max(energys_year.values())
    mean_bandwidth_year[address] = mean(bandwidths_year.values())
    mean_energy_year[address] = mean(energys_year.values())

    account = requests.get(f"https://apilist.tronscanapi.com/api/accountv2?address={address}").json()
    total_energys[address] = account['bandwidth']['energyLimit']
    total_bandwidths[address] = account['bandwidth']['netLimit']

