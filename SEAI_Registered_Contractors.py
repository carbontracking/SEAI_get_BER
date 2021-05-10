import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

link = 'https://hes.seai.ie/GrantProcess/ContractorSearch.aspx'

payload = {
    'ctl00$DefaultContent$ContractorSearch1$dfSearch$Id': '',
    'ctl00$DefaultContent$ContractorSearch1$dfSearch$CompanyName': '',
    'ctl00$DefaultContent$ContractorSearch1$dfSearch$County': '',
    'ctl00$DefaultContent$AssessorSearch$dfSearch$searchType': 'rbnDomestic',
    'ctl00$DefaultContent$AssessorSearch$dfSearch$Bottomsearch': 'Search'
}

page = 1

def get_captcha_value():
    with HTMLSession() as session:
        r = session.get(link)
        r.html.render(sleep=5)
        captcha_value = r.html.find("input[name$='$AssessorSearch$captcha']",first=True).attrs['value']
        return captcha_value

with requests.Session() as s:
    s.headers['User-Agent'] = 'Mozilla/5.0 (WindowMozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    r = s.get(link)
    soup = BeautifulSoup(r.text,"lxml")
    payload['__VIEWSTATE'] = soup.select_one("#__VIEWSTATE")['value']
    payload['__VIEWSTATEGENERATOR'] = soup.select_one("#__VIEWSTATEGENERATOR")['value']
    payload['__EVENTVALIDATION'] = soup.select_one("#__EVENTVALIDATION")['value']
    payload['ctl00$forgeryToken'] = soup.select_one("#ctl00_forgeryToken")['value']
    payload['ctl00$DefaultContent$AssessorSearch$captcha'] = get_captcha_value()
    
    while True:
        res = s.post(link,data=payload)
        soup = BeautifulSoup(res.text,"lxml")
        if not soup.select_one("table[id$='gridAssessors_gridview'] tr[class$='RowStyle']"): break
        for items in soup.select("table[id$='gridAssessors_gridview'] tr[class$='RowStyle']"):
            _name = items.select_one("td > span").get_text(strip=True)
            #print(_name)
            print(items)

        page+=1
        payload = {i['name']:i.get('value','') for i in soup.select('input[name]')}
        payload.pop('ctl00$DefaultContent$AssessorSearch$dfSearchAgain$Feedback')
        payload.pop('ctl00$DefaultContent$AssessorSearch$dfSearchAgain$Search')
        payload['__EVENTTARGET'] = 'ctl00$DefaultContent$AssessorSearch$gridAssessors$grid_pager'
        payload['__EVENTARGUMENT'] = f'1${page}'
