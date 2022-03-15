import os
import time
import wikipedia
from flask import Flask, request, render_template
from keybert import KeyBERT
from rdflib import Graph
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

app = Flask(__name__)
searchInputEINS = ""
searchInputZWEI = ""



def put(repository, data, context, auth=None):

    url = '{respository}/statements?context=<{context}>'.format(respository=repository, context=context)

    headers = {
        'Content-Type': 'application/x-turtle;charset=UTF-8, */*;q=0.5'
    }

    r = requests.put(url, data=data, headers=headers, auth=auth)

    if r.status_code != 204:
        raise requests.RequestException(r.text)


@app.route("/", methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        searchInputEINS = request.form['searchInputEINS']
        searchInputZWEI = request.form['searchInputZWEI']
        print(request.form['searchInputEINS'], request.form['searchInputZWEI'])
        driver = webdriver.Firefox()
        # single word search:
        # driver.get("https://www.nature.com/search?q=" + searchInputEINS + "&journal=")

        driver.get("https://www.nature.com/search?q=" + searchInputEINS + "%20" + searchInputZWEI + "&order=relevance")
        links = driver.find_elements(By.CLASS_NAME, "c-card__link")

        ArtikelLinks = []

        for i in links:
            intoString = i.get_attribute("href")
            # print(i.get_attribute("href"))
            intoString = str(intoString)
            ArtikelLinks.append(intoString)
            # driver.get(intoString)

        print(links)
        print(ArtikelLinks)
        print(len(ArtikelLinks))

        docs = []
        ArticleTitles = []
        titelUndArtikel = []

        for x in ArtikelLinks:
            driver.get(x)
            nachschauen = driver.find_elements(By.XPATH, "//html/body/div[2]/main/article/div[2]/section[1]/div/div/p ")
            titelExtrahieren = driver.find_elements(By.XPATH, "/html/body/div[2]/main/article/div[1]/header/h1")
            for titel, e in zip(titelExtrahieren, nachschauen):
                print("TITEL")
                print(titel.text)
                ArticleTitles.append(titel.text)
                print("ABSTRACT")
                print(e.text)
                docs.append(e.text)
                titelUndArtikel.append({
                    "titel": titel.text,
                    "abstract": e.text
                })
            print(" ")
            print(titelUndArtikel)

        print(len(docs))

        # XPath : /html/body/div[2]/main/article/div[2]/section[1]/div/div/p ||
        # /html/body/div[2]/main/article/div[2]/section[1]/div/div/p/text()[1]

        print(ArticleTitles)

        print(len(ArticleTitles))

        kw_model = KeyBERT()
        keywords = []
        manyKeywords = []

        for i in docs:
            keywords.append(kw_model.extract_keywords(i))
            # print(i)
            manyKeywords.append(kw_model.extract_keywords(i, keyphrase_ngram_range=(1, 1)))

        print(manyKeywords)

        keyWordArrayStorage = []

        for x in manyKeywords:
            for y in x:
                output, certain = y
                keyWordArrayStorage.append(output)

        print(keyWordArrayStorage)

        final_keyWordArrayStorage = list(dict.fromkeys(keyWordArrayStorage))

        print("final_keyWordArrayStorage", final_keyWordArrayStorage)

        SummaryOfKeyword = []
        WikipediaLink = []
        LinksKeywordsAndSummary = []
        for new in final_keyWordArrayStorage:
            try:
                print(new + ": " + wikipedia.summary(new))
                SummaryOfKeyword.append(wikipedia.summary(new))
                WikipediaLink.append(wikipedia.page(new).url)
            except:
                print(new + ": unfortunally no summary found for this word")
                pass
                continue

        print(" Array print: ", SummaryOfKeyword, WikipediaLink)

        for links, keywords, summary in zip(WikipediaLink, final_keyWordArrayStorage, SummaryOfKeyword):
            LinksKeywordsAndSummary.append({
                "link": links,
                "keyword": keywords,
                "summary": summary
            })
        print("LinksKeywordsAndSummary" , LinksKeywordsAndSummary)

        finalArray = []

        for Keyword2RDF in final_keyWordArrayStorage:
            driver2 = webdriver.Firefox()
            driver2.get(
                "https://meshb.nlm.nih.gov/search?searchInField=termDescriptor&sort=&size=20&searchType=exactMatch&searchMethod=FullWord&q=" + Keyword2RDF)
            driver2.find_element(By.ID, "exactMatch").click()
            time.sleep(4)
            links2 = driver2.find_elements(By.XPATH, "/html/body/div[2]/div/div[1]/dl/dd[4]/a")
            # //*[@id="exactMatch"]
            print(links2)
            # print(tags)
            for i in links2:
                checkForNoEmpty = str(i.get_attribute("href"))
                if (checkForNoEmpty != 'None'):
                    print(i)
                    intoString = i.get_attribute("href")
                    intoString = str(intoString)
                    finalArray.append(intoString)
                    print(intoString)
            driver2.close()

        print("finalArray", finalArray)

        neuerArray4 = []

        for getRDFPage in finalArray:
            driver3 = webdriver.Firefox()
            driver3.get(getRDFPage)
            links3 = driver3.find_elements(By.XPATH, "/html/body/div[3]/div/div/div[2]/div/div[3]/span/a")
            for i in links3:
                intoString = i.get_attribute("href")
                # print(i.get_attribute("href"))
                intoString = str(intoString)
                neuerArray4.append(intoString)
                # driver.get(intoString)
            driver3.close()

        print("neuerArray4", neuerArray4)

        g = Graph()

        g.parse(neuerArray4[0])
        g.parse(neuerArray4[3])
        g.parse(neuerArray4[6])
        g.parse(neuerArray4[9])
        g.parse(neuerArray4[12])
        g.parse(neuerArray4[15])


        g.serialize(destination="static/images/tbl.ttl")
        datei = g.serialize(destination="tbl.ttl")

        n = len(g)
        print(f"Read {n} triples.")

        repository = 'http://141.100.220.46:7200/repositories/isy_clara'
        auth = ('student', 'student01')

        data = open("static/images/tbl.ttl", "r")

        context = 'http://data/Intelligente_Systeme_16_02_2022.ttl'

        put(repository, data, context, auth=auth)

        return render_template('index.html', searchInputEINS=searchInputEINS,
                               searchInputZWEI=searchInputZWEI,
                               ArticleTitles=ArticleTitles,
                               docs=docs,
                               final_keyWordArrayStorage=final_keyWordArrayStorage,
                               SummaryOfKeyword=SummaryOfKeyword, WikipediaLink=WikipediaLink,
                               titelUndArtikel=titelUndArtikel,
                               LinksKeywordsAndSummary=LinksKeywordsAndSummary,
                               RDF_Mesh_Links=neuerArray4)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(port=3000, debug=True)
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
