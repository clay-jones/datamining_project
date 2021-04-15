import csv
import os

import requests
from bs4 import BeautifulSoup as Soup
from time import sleep
import re

class GenreTitleAndUrl:
  def __init__(self, title, url):
    self.title = title
    self.url = url

def getGenreUrls(response):
    soup = Soup(response, 'lxml')
    results = soup.find('ul', class_='results')
    genreTitleAndUrlList = []
    for genre in results.findAll('li'):
        soupGenreItem = Soup(str(genre), 'lxml')
        genreTitle = soupGenreItem.find('span', class_='title')
        genreTitle = Soup(str(genreTitle), 'lxml').getText()
        if any(chosenGenre.lower() == genreTitle.lower() for chosenGenre in listOfGenres):
            genreUrl = soupGenreItem.find('a')['href']
        else:
            continue
        genreTitleAndUrlList.append(GenreTitleAndUrl(genreTitle, genreUrl))
    return genreTitleAndUrlList

def printListOfGenresTitleAndUrl(listOfGenresTitleAndUrl):
    for genreTitleAndUrl in listOfGenresTitleAndUrl:
        print(genreTitleAndUrl.title)
        print(genreTitleAndUrl.url)
        print("===================")

def getGenrePageUrl(genreTitleAndUrl):
    requestUrl = baseUrl + genreTitleAndUrl.url
    response = delayedGetRequest(requestUrl)
    print(response)
    return response

def writeHtmlToFile(fileName, response):
    f = open(fileName, "w")
    f.write(response)
    f.close()

def getListOfBooksUrlsForGenreInPage(response):
    soup = Soup(response, 'lxml')
    results = soup.find('ul', class_='results')
    booksInPageUrlList = []
    for book in results.findAll('li', class_="booklink"):
        try:
            bookItem = Soup(str(book), 'lxml')
            bookUrl = bookItem.find('a')['href']
            booksInPageUrlList.append(bookUrl)
        except:
            continue
    return booksInPageUrlList

def getNextPageUrlIfAvailable(genreResponse):
    soup = Soup(genreResponse, 'lxml')
    statusLine = soup.find('li', class_='statusline')
    allNavUrls = statusLine.findAll('a')
    for navUrl in allNavUrls:
        if "Next" in str(navUrl):
            return navUrl['href']
    return ""

def downloadBookText(bookDownloadUrl, bookMetaData, outputPath):
    downloadUrl = baseUrl + bookDownloadUrl
    bookTextResponse = delayedGetRequest(downloadUrl)
    soup = Soup(bookTextResponse)
    bookText = soup.find('body').getText()
    bookOutputPath = outputPath + "/" + "{0}.txt".format(bookMetaData['Title'])
    f = open(bookOutputPath, "w")
    f.write(bookText)
    f.close()

    # write book meta data
    bookMetaDataOutputPath = outputPath + "/" + "{0}_Meta_Data.csv".format(bookMetaData['Title'])
    w = csv.writer(open(bookMetaDataOutputPath, "w"))
    for key, val in bookMetaData.items():
        w.writerow([key, val])

# <td property="dcterms:format" content="text/plain" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/ebooks/23172.txt.utf-8" type="text/plain" class="link" title="Download">Plain Text UTF-8</a></td>
# <td property="dcterms:format" content="text/plain; charset=utf-8" datatype="dcterms:IMT" class="unpadded icon_save"><a href="/files/5200/5200-0.txt" type="text/plain; charset=utf-8" class="link" title="Download">Plain Text UTF-8</a></td>
def getBookDownloadUrl(bookItemPageResponse):
    try:
        soup = Soup(bookItemPageResponse, 'lxml')
        downloadDiv = soup.find(id='download')
        divSoup = Soup(str(downloadDiv), 'lxml')
        #textDownloadUrl = divSoup.find('a', type='text/plain; charset=utf-8', class_='link', title='Download')['href']
        textDownloadUrl = divSoup.find('a', type=re.compile("text/plain"), class_='link', title='Download')['href']
        return textDownloadUrl
    except:
        return ""

def getBookItemMetaData(bookItemPageResponse):
    soup = Soup(bookItemPageResponse, 'lxml')
    table = soup.find('table', class_='bibrec')
    tableSoup = Soup(str(table), 'lxml')
    rows = tableSoup.findAll('tr')
    bookMetaData = {}
    for row in rows:
        try:
            rowSoup = Soup(str(row), 'lxml')
            rowKey = rowSoup.find('th').getText().strip()
            rowValue = rowSoup.find('td').getText().strip()
            if rowKey in bookMetaData.keys():
                bookMetaData[rowKey] = bookMetaData[rowKey] + ", " + rowValue
            else:
                bookMetaData[rowKey] = rowValue
        except:
            continue
    return bookMetaData

def downloadBooksInPage(pageResponse, listOfBookTitles):
    listOfBooksInPage = getListOfBooksUrlsForGenreInPage(pageResponse)
    for bookUrl in listOfBooksInPage:
        try:
            fullBookUrl = baseUrl + bookUrl
            bookResponsePage = delayedGetRequest(fullBookUrl)
            bookDownloadUrl = getBookDownloadUrl(bookResponsePage)
            if bookDownloadUrl == "":
                continue

            bookMetaData = getBookItemMetaData(bookResponsePage)

            if 'Title' not in bookMetaData.keys() | 'Language' not in bookMetaData.keys():
                continue

            if bookMetaData['Language'] != "English":
                continue

            outputFolder = genreUrl.title
            # write this to a file to help with parsing
            listOfBookTitles.append(bookMetaData['Title'])

            # create path if it does not exist
            if not os.path.exists(outputFolder):
                os.makedirs(outputFolder)

            # download book
            downloadBookText(bookDownloadUrl, bookMetaData, outputFolder)
        except:
            continue

def writeListToFile(list, fileName):
    with open(fileName, 'w') as f:
        for item in list:
            f.write("%s\n" % item)
    f.close()

baseUrl = "https://www.gutenberg.org"
initialUrl = "https://www.gutenberg.org/ebooks/bookshelves/search/?query=fiction%7Cadventure%7Cfantasy%7Chumor%7Chorror%7Cwestern"
listOfGenres = ['Gothic Fiction', 'Science fiction', 'Horror', 'Adventure', 'Humor', 'Western', 'Mystery Fiction']

# used to avoid getting IP address blocked
# since website does not allow scraping
def delayedGetRequest(url):
    sleep(0.100)
    return requests.get(url).text

# Get initial page response
initialPageRespnse = delayedGetRequest(initialUrl)
listOfGenreURLs = getGenreUrls(initialPageRespnse)

# Loop over Genre URL's and download all the books in each one
for genreUrl in listOfGenreURLs:
    fullGenreUrl = baseUrl + genreUrl.url
    genrePageResponse = delayedGetRequest(fullGenreUrl)
    listOfBookTitles = []
    downloadBooksInPage(genrePageResponse, listOfBookTitles)
    nextPageUrl = getNextPageUrlIfAvailable(genrePageResponse)
    while nextPageUrl != "":
        try:
            fullNextUrl = baseUrl + nextPageUrl
            pageResponse = delayedGetRequest(fullNextUrl)
            downloadBooksInPage(pageResponse, listOfBookTitles)
            nextPageUrl = getNextPageUrlIfAvailable(pageResponse)
        except:
            continue

    try:
        # write list of book titles into a text file
        outputFile = genreUrl.title + "/" + "booksInGenre.txt"
        writeListToFile(listOfBookTitles, outputFile)
    except:
        continue
