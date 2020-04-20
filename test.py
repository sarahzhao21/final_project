
# from bs4 import BeautifulSoup
# import requests

# def get_booksite_dic(base_url):
#     url_text = requests.get(base_url).text
#     soup = BeautifulSoup(url_text, 'html.parser')
#     booksite_dic = {}
#     bookgroup = soup.find('div', itemtype="http://schema.org/ItemList")
#     booksites = bookgroup.find_all('div', class_="css-v2kl5d")
#     for booksite in booksites:
#         path = booksite.find('h2').find('a')['href']
#         site_url = 'https://www.nytimes.com' + path
#         key = booksite.find('h2')['id']
#         booksite_dic[key] = site_url
#     return booksite_dic

# booksite_dic = get_booksite_dic('https://www.nytimes.com/books/best-sellers/')
# keys = []
# for key,value in booksite_dic.items():
#     keys.append(key)

# print(keys)
# url = 'https://books.apple.com/us/book/six-shorts-2017/id1218201429'

apple = '$1.99'
print(apple[1:])