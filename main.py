import random
import os
from time import sleep
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def random_sleep():
    sleep(random.randint(1, 5))


def remove_results():
    try:
        os.remove('./results.txt')
    except FileNotFoundError:
        pass


def write_to_file(**kwargs):
    # current date and time
    with open('./results.txt', 'a') as file:
        row = ', '.join(
            f'{key}: {value}' for key, value in kwargs.items()
        )
        file.write(row + '\n')


def write(_format='file', **kwargs):
    if _format == 'file':
        write_to_file(**kwargs)


# additional function
def safe_next(body, times):
    for i in range(times):
        body = getattr(body, 'next') if body is not None else None
    return body


def cleen(string):
    if string is None:
        return None
    elements = [
        '  ',
        '\n',
        '\u202f',
        '\u2009',
    ]
    for element in elements:
        if element in string:
            string = string.replace(element, '')
    return string


def parse_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_block = soup.find('div', {'class': 'card wordwrap'})
    # salary and company blocks
    salary_block = main_block.find('p', {'class': 'text-indent text-muted add-top-sm'})
    # salary num
    if salary_block is not None:
        salary = salary_block.find('b', {'class': 'text-black'})
        salary = salary.text if salary is not None else None
        # salary type
        salary_type = salary_block.find('span', {'class': 'text-muted'})
    else:
        salary, salary_type = None, None
    for _ in range(3):
        salary_type = salary_type.next if salary_type is not None else None
    # company // all time
    company = main_block.find('a', href=True, title=True).find('b').next
    # company type // all time
    company_type = main_block.find('span', {'class': 'add-top-xs'}).next
    # company size // all time
    company_size = company_type.next.next  # if company_type.next is not None else None
    # address
    address = main_block.find(
        'span', {'class': 'glyphicon glyphicon-map-marker text-black glyphicon-large', 'title': 'Адреса роботи'}
    )
    address = safe_next(address, 1)
    # recruiter
    recruiter = main_block.find(
        'span', {'class': 'glyphicon glyphicon-phone text-black glyphicon-large', 'title': 'Контакти'}
    )
    recruiter = safe_next(recruiter, 1)
    # work_type
    work_type = main_block.find(
        'span', {'class': 'glyphicon glyphicon-tick text-black glyphicon-large', 'title': 'Умови й вимоги'}
    )
    work_type = safe_next(work_type, 1)
    # cleen data
    data = [cleen(i) for i in (salary, salary_type, company, company_type, company_size, address, recruiter, work_type)]
    keys = ('salary', 'salary_type', 'company', 'company_type', 'company_size', 'address', 'recruiter', 'work_type')
    D = dict(zip(keys, data))
    return D


def main():
    remove_results()

    counter = 0
    ua = UserAgent()

    while True:
        counter += 1
        random_sleep()
        print(f'Page: {counter}')

        if counter == 10:
            break

        headers = {
            'User-Agent': ua.random,
        }
        query_params = {
            'page': counter,
        }
        url = 'https://www.work.ua/jobs/'
        response = requests.get(url, params=query_params, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        job_list = soup.find('div', {'id': 'pjax-job-list'})

        # if not job_list:
        if job_list is None:
            break

        job_set = job_list.find_all('h2')

        for job in job_set:
            a_tag = job.find('a', href=True)
            href = a_tag['href']
            title = a_tag['title']
            content = a_tag.text
            # parse_details(url + href)
            ditail_data = parse_details('https://www.work.ua' + href)
            write(href=href, title=title, content=content, **ditail_data)


if __name__ == '__main__':
    main()
