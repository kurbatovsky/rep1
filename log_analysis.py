""" Find IP """
import re


OS = {}


def read_log(log_file):
    """ Read log from file"""
    with open(log_file, 'r') as file_:
        logs = file_.read()
    return logs


def search_ip(logs):
    """ Looking for IP in log"""
    ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', logs)
    return list(set(ips))


def count_ip(ip, logs):
    """ Count IP"""
    return len(re.findall(ip, logs))


def sort_ip(ips, logs):
    """ Sort by IP """
    ips.sort(key=lambda x: count_ip(x, logs), reverse=True)
    return ips


def search_all_os(logs):
    """ Search all OS"""
    logs_list = logs.splitlines()
    for x in logs_list:
        search_os(clear_log(x))


def add_key(key):
    """ Add key to dict"""
    if key not in OS:
        OS[key] = 0
        OS[key] += 1
    else:
        OS[key] += 1


def search_os(log):
    """ Looking for system """
    if re.search(r'win\w{2,4}', log.lower()) is not None:
        add_key('Windows')
    elif 'mac os' in log.lower():
        add_key('Mac OS X')
    elif 'linux' in log.lower():
        add_key('Linux')
    elif 'freebsd' in log.lower():
        add_key('FreeBSD')
    elif 'cros' in log.lower():
        add_key('CrOS')
    elif 'yahoo' in log.lower():
        add_key('Yahoo! Slurp')
    elif re.search(r'\w+[bB]ot(-Mobile)?/', log) is not None:
        add_key(re.search(r'\w+[bB]ot(-Mobile)?/', log).group()[:-1])
    elif re.search(r'\w+\s?[sS]pider', log) is not None:
        add_key(re.search(r'\w+\s?[sS]pider', log).group())
    elif re.search(r'\w+[mM]etrika', log) is not None:
        add_key(re.search(r'\w+[mM]etrika', log).group())
    elif re.search(r'W3C.+/\d', log) is not None:
        add_key(re.search(r'W3C.+/\d', log).group()[:-2])
    elif re.search(r'\w+[nN]etwork', log) is not None:
        add_key(re.search(r'\w+[nN]etwork', log).group())
    elif re.search(r'[pP]resto', log) is not None:
        add_key(re.search(r'[pP]resto', log).group())
    elif re.search(r'Add Catalog', log) is not None:
        add_key(re.search(r'Add Catalog', log).group())
    elif re.search(r'\wcoc', log) is not None:
        add_key(re.search(r'\wcoc', log).group())


def sort_OS():
    """ Sort OS"""
    sorted_OS = sorted(OS, lambda x, y: cmp(OS[x], OS[y]))
    sorted_OS.reverse()
    return sorted_OS


def clear_log(log):
    """ Clear log"""
    log = re.sub(r'HTTP/', '', log)
    log = re.sub(r'Mozilla/', '', log)
    return log


def main():
    """ Main function """
    log_file = r'access2.log'
    logs = read_log(log_file)
    print("Frequent visitors:")
    print('\n'.join(sort_ip(search_ip(logs), logs)[:10]))
    search_all_os(logs)
    print("\nFrequent systems:")
    print('\n'.join(sort_OS()[:5]))


if __name__ == '__main__':
    main()
