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


def main():
    remove_results()

    counter = 0
    ua = UserAgent()

    while True:
        counter += 1
        random_sleep()
        print(f'Page: {counter}')

        # if counter == 4:
        #     break

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
            write(href=href, title=title, content=content)


if __name__ == '__main__':
    main()
