from urllib import request
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np


def func_brand():
    """
    車のブランドのURLを取得

    Returns
    -------
    brand_url_list : list
        車のブランドのURLのリスト
    """
    url = "https://www.carsensor.net/"
    html = request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    brand_urls = soup.select("ul.makerNav__list")[0].select("a")

    brand_url_list = list()
    for i in range(len(brand_urls)):
        brand_url = url + brand_urls[i].get("href")[1:]
        brand_url_list.append(brand_url)

    return brand_url_list


def func_car_list(brand_url_list, threshold):
    """
    車種のURLのリストを取得する

    Parameters
    ----------
    brand_url_list : list
        func_brand関数で取得したブランドURLのリスト
    threshold : int
        この値以上登録がある車種のみ取得する

    Returns
    -------
    car_url_list : list
        車種のURLのリスト
    """
    url = "https://www.carsensor.net/"
    car_url_list = list()
    for i in range(len(brand_url_list)):
        html = request.urlopen(brand_url_list[i])
        soup = BeautifulSoup(html, "html.parser")
        brand_cars = soup.select(".shashuList__category__item > label > a")
        for j in range(len(brand_cars)):
            car_num = int(brand_cars[j].select("span")[0].text[1:-1])
            if car_num >= threshold:
                brand_car_url = url + brand_cars[j].get("href")[1:].replace("map/", "")
                car_url_list.append(brand_car_url)
    return car_url_list


def func_scraping(cars, i):
    """
    車一台分の詳細情報を取得する

    Parameters
    ----------
    cars : bs4.element.ResultSet
        車の詳細情報のhtmlデータのリスト
    i : int
        carsの要素番号

    Returns
    -------
    car_info : list
        車の詳細情報のリスト
    """
    try:
        brand = cars[i].select(".casetMedia__body__maker")[0].text
    except:
        brand = "-"

    try:
        title = cars[i].select(".casetMedia__body__title")[0].text.split()[0]
    except:
        title = "-"

    try:
        body_type = cars[i].select(".casetMedia__body__spec > p")[0].text
    except:
        body_type = "-"

    try:
        year = cars[i].select(".specWrap__box__num")[0].text
    except:
        year = "-"

    try:
        running = cars[i].select(".specWrap__box")[1].select("p")
        distance = running[1].text + running[2].text 
    except:
        distance = "-"

    try:
        displacement = cars[i].select(".specWrap__box__num")[2].text
    except:
        displacement = "-"

    try:
        inspection = ''.join(cars[i].select(".specWrap__box")[3].text.split()[1:])
    except:
        inspection = "-"

    try:
        repair = cars[i].select(".specWrap__box")[4].text.split()[1]
    except:
        repair = "-"

    try:
        color = cars[i].select(".casetMedia__body__spec")[0].text.split()[2]
    except:
        color = "-"

    try:
        price = cars[i].select(".basePrice__price")[0].text.split()[0]
    except:
        price = "-"

    try:
        payment = cars[i].select(".totalPrice__price")[0].text.split()[0]
    except:
        payment = "-"

    try:
        location = cars[i].select(".casetSub__area > p")[0].text
    except:
        location = "-"

    try:
        evaluation = cars[i].select(".casetSub__review__score.js_shop > a > span")
        score = evaluation[0].text
        number = evaluation[1].text
    except:
        score = "-"
        number = "-"
        
    car_info = [brand, title, body_type, year, distance, displacement,
                inspection, repair, color, price, payment, location, score, number]

    return car_info


def func_detail(car_url, DETAIL_LIST):
    """
    func_scraping関数を再起的に実行して、1ページ分の詳細情報を取得する
    次のページに進む

    Parameters
    ----------
    car_url : str
        車種情報のURL
    DETAIL_LIST : list
        詳細情報のリスト

    Returns
    -------
    car_url : str
        (次のページの)車種情報のURL
    DETAIL_LIST : list
        詳細情報のリスト(情報追加済み)
    """
    url = "https://www.carsensor.net/"
    html = request.urlopen(car_url)
    soup = BeautifulSoup(html, "html.parser")
    cars = soup.select(".caset.js_listTableCassette")

    for i in range(len(cars)):
        car_info = func_scraping(cars, i)
        DETAIL_LIST.append(car_info)

    try:
        next_url = soup.select(".btnFunc.pager__btn__next")[1].get("onclick")
        pattern = "(?<=').*?(?=')"
        car_url = url + re.search(pattern, next_url).group()[1:]
    except:
        car_url = None
    
    return car_url, DETAIL_LIST


def func_detail_list(car_url, DETAIL_LIST):
    """
    func_detail関数を再起的に実行して、指定車種の全ての詳細データを取得
    スクレピングの進捗状況を表示
    ※必ずDETAIL_LISTを"list()"で初期化してから引数に渡すこと

    Parameters
    ----------
    car_url : str
        車種情報のURL
    DETAIL_LIST : list
        詳細情報のリスト

    Returns
    -------
    title : str
        車種の名前
    DETAIL_LIST : list
        詳細情報のリスト
    """
    try:
        html = request.urlopen(car_url)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.select(".casetMedia__body__title > a")[0].text.split()[0]
        all_num = int(soup.select(".resultBar__result > p")[0].text[:-1].replace(",", ""))
        pro_bar = (" " * 30)
        print('\r{0} [{1}] {2}/{3}'.format(title, pro_bar, 0, all_num), end='')
    except:
        pass

    while car_url is not None:
        car_url, DETAIL_LIST = func_detail(car_url, DETAIL_LIST)
        try:
            now_num = len(DETAIL_LIST)
            progress = int((now_num / all_num) * 30)
            pro_bar = ("=" * progress) + (" " * (30 - progress))
            print('\r{0} [{1}] {2}/{3}'.format(title, pro_bar, now_num, all_num), end='')
        except:
            pass
    print('\r{0} [{1}] {2}/{3}'.format(title, pro_bar, now_num, all_num), end="\n")
    return title, DETAIL_LIST
