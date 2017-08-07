""" Find IP """
import re


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


def main():
    """ Main function"""
    log_file = r'C:\Users\ikurbatovskiy\Desktop\access2.log'
    logs = read_log(log_file)
    print(sort_ip(search_ip(logs), logs)[:10])


if __name__ == '__main__':
    main()
