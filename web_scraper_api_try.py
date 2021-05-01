from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg.query.api import get_etexts
from gutenberg.query.api import get_metadata
from gutenberg.query import list_supported_metadatas
import re
import os
import io
import time

listOfGenres = ['science fiction', 'Horror', 'Adventure', 'Humor', 'Western', 'Mystery Fiction', 'Gothic Fiction']
# if any(chosenGenre in str(genre) for chosenGenre in listOfGenres):
# 1519, 7103, 9262, 10415, 10816, 11313-11314,12910, 13746, 14284, 17957, 18042, 19359, 20575

def main():
    if not os.path.isdir('books'):
        os.makedirs('books')
    print(list_supported_metadatas())
    for i in range(19363, 100000):
        try:
            print(i, get_metadata('title', i))
            if len(get_metadata('title', i)) > 0:
                want = False
                for lang in get_metadata('language', i):
                    language = lang
                if language.lower() == 'en':
                    categories = ""
                    for genre in get_metadata('subject', i):
                        for category in genre.split("--"):
                            categories += "_" + category.strip().lower().replace("-", " ").replace(".", " ")\
                                .replace(",", " ").strip().replace("  ", " ").replace(" ", "-")\
                                .replace("(", "").replace(")", "").replace("'", "")
                        if re.search('science fiction', genre.lower()):
                            want = True
                        elif re.search('horror', genre.lower()):
                            want = True
                        elif re.search('adventure', genre.lower()):
                            want = True
                        elif re.search('humor', genre.lower()):
                            want = True
                        elif re.search('western', genre.lower()):
                            want = True
                        elif re.search('mystery fiction', genre.lower()):
                            want = True
                        elif re.search('gothic fiction', genre.lower()):
                            want = True
                        else:
                            want = False
                    if want is True:
                        text = str(strip_headers(load_etext(i)).strip())
                        title = " "
                        title = str(i) + categories
                        print('writing to file %s' % title)
                        f = open("books/%s.txt" % title, "wb")
                        f.write(text.encode('utf8'))

        except Exception as e:
            print(e)
            pass


if __name__ == "__main__":
    main()
