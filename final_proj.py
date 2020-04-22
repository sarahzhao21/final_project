#################################
##### Name: Xinyi Zhao ##########
##### Uniqname:  xinyiz #########
#################################
##### For submission    #########
################################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3

CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

def load_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    
    Parameters
    ----------
    url: string
        The basic URL of the website
    cache: dict
        A dictionary where the url_text saved
    
    Returns
    -------
    url_text
        the result of the query as a url_text get from the website
    '''
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

 
def get_booksite_dic(base_url):
    ''' Web scraping and crawling on New York Time Best Seller home page and get the web url of each book category
    
    Parameters
    ----------
    base_url: str
        the basic url of New York Time Best Seller home page
    
    Returns
    -------
    booksite_dic: dict
        a dictionary with each book category as the key and it's url as the value
    '''
    url_text = make_url_request_using_cache(base_url, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')
    booksite_dic = {}
    bookgroup = soup.find('div', itemtype="http://schema.org/ItemList")
    booksites = bookgroup.find_all('div', class_="css-v2kl5d")
    for booksite in booksites:
        path = booksite.find('h2').find('a')['href']
        site_url = 'https://www.nytimes.com' + path
        key = booksite.find('h2')['id']
        booksite_dic[key] = site_url
    return booksite_dic

def get_bookinfo_list(booksite_dic):
    ''' Web scraping and crawling on the webpages of the books in each category, get the detailed information of each book
    
    Parameters
    ----------
    booksite_dic: dict
        the dictionary with the url of each book category
    
    Returns
    -------
    book_list: list
        a nested list with the information of the books, the information of each book is saved as a list
    '''
    book_list = []
    i = 1
    for key,value in booksite_dic.items():
        url_text = make_url_request_using_cache(value, CACHE_DICT)
        soup = BeautifulSoup(url_text, 'html.parser')
        booksoup = soup.find('ol', itemtype="http://schema.org/ItemList")
        booklist = booksoup.find_all('li', class_="css-13y32ub")
        j = 1
        for book in booklist:
            book_row = []
            # bookinfo = book.find('div', class_="css-xe4cfy")
            category = key
            title = book.find('h3', itemprop="name").text.strip()
            author = book.find('p', itemprop="author").text.strip()
            publisher = book.find('p', itemprop="publisher").text.strip()
            description = book.find('p', itemprop="description").text.strip()
            rank = j
            # rank = bookinfo.find('div', class_="css-1dv1knv").text.strip()
            weektext = book.find('p', class_="css-1o26r9v").text.strip()
            week = weektext.split()[0]
            retailers = book.find('ul', class_="css-6mwynb")
            apple_url = retailers.find_all('li')[1].find('a')['href']
            # bookId = str(i)
            # book_row.append(bookId)
            book_row.append(title)
            book_row.append(category)
            book_row.append(author[3:])
            book_row.append(publisher)
            book_row.append(rank)
            if week == 'New':
                week = 0
            book_row.append(int(week))
            book_row.append(description)
            book_row.append(apple_url)
            book_key = 'book' + str(i)
            book_list.append(book_row)
            i += 1
            j += 1
    return book_list
            
def build_date(date1, date2):
    ''' Turn the date information into a nice string 
    
    Parameters
    ----------
    date1: str
        the original year information 
    date2: str
        the original month and day information
        
    Returns
    -------
    date_string: str
        a new form of date look like'yyyy_mm_dd'
    '''
    m = date2.split(' ')[0]
    d = date2.split(' ')[1]
    if m == 'January':
        month = '01'
    elif m == 'February':
        month = '02'
    elif m == 'March':
        month = '03'
    elif m == 'April':
        month = '04'
    elif m == 'May':
        month = '05'
    elif m == 'June':
        month = '06'
    elif m == 'July':
        month = '07'
    elif m == 'August':
        month = '08'
    elif m == 'September':
        month = '09'
    elif m == 'October':
        month = '10'
    elif m == 'November':
        month = '11'
    else:
        month = '12'
    
    if len(d) == 1:
        date = '0' + d
    else:
        date = d
    date_string = date1 + '_' + month + '_' + date
    return date_string
      

def get_applebook_list(book_list):
    ''' by the "Apple Books' url of each book, do web scraping on 'Apple Books' for each book from book_list, 
    get the detailed information of each book on 'Apple Books'
    
    Parameters
    ----------
    book_list: list
        the nested list with the information of each book
    
    Returns
    -------
    apple_list: list
        a nested list with the information of the books on 'Apple Books', the information of each book is saved as a single list
    '''
    apple_urls = []
    apple_list = []
    for book in book_list:
        apple_urls.append(book[-1])

    i = 1
    for url in apple_urls:
        apple_row = []
        url_text = make_url_request_using_cache(url, CACHE_DICT)
        soup = BeautifulSoup(url_text, 'html.parser')
        try:
            title = soup.find('h1', class_="product-header__title book-header__title").text.strip()
        except:
            title = None
        try:
            rating = soup.find('figcaption', class_='we-rating-count star-rating__count').text.strip().split(',')[0]
        except:
            rating = None
        try:
            price = soup.find('li', class_="inline-list__item inline-list__item--slashed").find('span').text.strip()
        except:
            price = None

        section = soup.find('section', class_="l-content-width l-row l-row--peek section section--book-infobar ember-view")
        try:
            figure = section.find_all('figure')
        except:
            figure = None
        if figure is None:
            genre = None
            release_date = None
            language = None
            length = None
            seller = None
            size = None
        else:
            genre = figure[0].find('div', class_="book-badge__caption").text.strip()
            release_date1 = figure[1].find('div', class_="book-badge__value").text.strip()
            release_date2 = figure[1].find('div', class_="book-badge__caption").text.strip()
            release_date = build_date(release_date1, release_date2)
            language = figure[2].find('div', class_="book-badge__caption").text.strip()
            try:
                length = figure[3].find('div', class_="book-badge__value").text.strip()
            except:
                length = None
            try:
                seller = figure[5].find('div', class_="book-badge__caption").text.strip()
            except:
                seller = None
            try:
                size = figure[6].find('div', class_="book-badge__value").text.strip()
            except:
                size = None
        # appleId = str(i)
        apple_key = 'apple' + str(i)
        # apple_row.append(appleId)
        apple_row.append(title)
        if rating:
            apple_row.append(float(rating))
        else:
            apple_row.append(rating)
        if price:
            apple_row.append(float(price[1:]))
        else:
            apple_row.append(price)
        apple_row.append(genre)
        apple_row.append(release_date)
        apple_row.append(language)
        if length:
            apple_row.append(int(length))
        else:
            apple_row.append(length)
        apple_row.append(seller)
        if size:
            apple_row.append(float(size))
        else:
            apple_row.append(size)
        apple_list.append(apple_row)
        i += 1
    return apple_list

def creat_book_table(list1, list2):
    ''' Based on the information of two lists, create a sqlite file with two tables in it
    
    Parameters
    ----------
    list1: list
        the information of the books from New York Time Best Sellers
    list2: list
        the informaiton of the books from 'Apple Books'

    Returns
    -------
        None
    '''
    conn = sqlite3.connect("best_seller_books.sqlite")
    cur = conn.cursor()
    drop_bestseller = '''
        DROP TABLE IF EXISTS "Best_seller";
    '''
    create_bestseller = '''
        CREATE TABLE IF NOT EXISTS "Best_seller" (
            "Id"        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Title"  TEXT NOT NULL,
            "Category" TEXT NOT NULL,
            "Author"  TEXT NOT NULL,
            "Publisher"    TEXT NOT NULL,
            "Rank" INTEGER NOT NULL,
            "Weeks_on_the_list" INTEGER NOT NULL,
            "Description" TEXT NOT NULL,
            "Apple_url" TEXT NOT NULL
        );
    '''

    drop_apple = '''
        DROP TABLE IF EXISTS 'Apple_book'
    '''
    create_apple = '''
        CREATE TABLE 'Apple_book' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Title' TEXT,
        'Rating' REAL,
        'Price' REAL,
        'Genre' TEXT,
        'Released_date' TEXT,
        'Language' TEXT,
        'Length' INTEGER,
        'Seller' TEXT,
        'Size' REAL
        ); 
    '''
    cur.execute(drop_bestseller)
    cur.execute(create_bestseller)
    cur.execute(drop_apple)
    cur.execute(create_apple)
    conn.commit()

    
    insert_bestseller = '''
        INSERT INTO Best_seller
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    for book in list1:
        cur.execute(insert_bestseller, book)
        conn.commit()
    
    insert_apple = '''
        INSERT INTO Apple_book
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    for apple in list2:
        cur.execute(insert_apple, apple)
        conn.commit()


if __name__ == "__main__":
    CACHE_DICT = load_cache()
    booksite_dic = get_booksite_dic('https://www.nytimes.com/books/best-sellers/')
    book_list = get_bookinfo_list(booksite_dic)
    apple_list = get_applebook_list(book_list)
    creat_book_table(book_list, apple_list)
    