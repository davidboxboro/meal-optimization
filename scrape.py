# scrape recipe website for all recipes

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from tqdm import tqdm
import json


def scrape_recipe_site(num_pages=117):
    dicts = []
    # visit each page of catalog
    n_page = 0
    n_success = 0
    for i in range(1, num_pages + 1):
        print(f'\nPage {i} / {num_pages}')
        url = f'https://www.budgetbytes.com/recipe-catalog/page/{i}/'
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')
        # get iterate through each article on page
        articles = soup.find_all('article')
        for article in articles:
            recipe_url = article.find('a', href=True)['href']
            n_page += 1
            try:
                d = scrape_recipe_page(recipe_url)
                n_success += 1
            except Exception as e:
                print(e)
                continue
            dicts.append(d)
        print(f'{n_success} successes / {n_page} pages')
    return dicts


def scrape_recipe_page(recipe_url):
    recipe_page = requests.get(recipe_url)
    recipe_soup = bs(recipe_page.content, 'html.parser')
    # keep track of info
    d = {}
    # get title
    dish = recipe_soup.find('meta', attrs={'property': 'og:title'})['content']
    print(dish)
    d['dish'] = dish
    # get price
    cost = recipe_soup.find('span', class_='cost-per').text
    cost_per_serving = cost.strip('(').strip(')').split('/')[1]
    cost_per_serving = cost_per_serving.split()[0]
    assert cost_per_serving[0] == '$'
    cost_per_serving = cost_per_serving[1:]
    d['cost_per_serving'] = cost_per_serving
    # get nutrition
    nutrition_soup = recipe_soup.find('div', class_='wprm-nutrition-label-container')
    macro_soup = nutrition_soup.find_all('span', class_='wprm-nutrition-label-text-nutrition-container')
    for macro_span in macro_soup:
        macro_name = macro_span.find('span', class_='wprm-nutrition-label-text-nutrition-label').text
        macro_val = macro_span.find('span', class_='wprm-nutrition-label-text-nutrition-value').text
        macro_unit = macro_span.find('span', class_='wprm-nutrition-label-text-nutrition-unit').text
        macro_name = macro_name.strip()[:-1].lower()
        macro_val = macro_val.strip()
        macro_unit = macro_unit.strip()
        d[macro_name] = macro_val
        d[f'{macro_name}_unit'] = macro_unit
    return d


if __name__ == '__main__':
    dicts = scrape_recipe_site()
    with open('recipe_dicts.json', 'w') as f:
        json.dump(dicts, f)
