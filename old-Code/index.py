from flask import Flask, request, render_template
from keybert import KeyBERT
from rdflib import Graph
from selenium import webdriver
from selenium.webdriver.common.by import By
import wikipedia
import pydotplus
from IPython.display import display
from rdflib.tools.rdf2dot import rdf2dot
import io
import PIL.Image as Image
import os


app = Flask(__name__)
searchInputEINS = ""
searchInputZWEI = ""


@app.route("/", methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        searchInputEINS = request.form['searchInputEINS']
        searchInputZWEI = request.form['searchInputZWEI']
        print(request.form['searchInputEINS'], request.form['searchInputZWEI'] )
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
                    "titel" : titel.text,
                    "abstract" : e.text
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

        print(final_keyWordArrayStorage)

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

        for links, keywords , summary in zip(WikipediaLink,final_keyWordArrayStorage,SummaryOfKeyword):
            LinksKeywordsAndSummary.append({
                "link": links,
                "keyword": keywords,
                "summary": summary
            })
        print(LinksKeywordsAndSummary)

        return render_template('index.html', searchInputEINS=searchInputEINS,
                               searchInputZWEI=searchInputZWEI,
                               ArticleTitles=ArticleTitles,
                               docs=docs,
                               final_keyWordArrayStorage=final_keyWordArrayStorage,
                               SummaryOfKeyword=SummaryOfKeyword, WikipediaLink=WikipediaLink,
                               titelUndArtikel=titelUndArtikel,
                               LinksKeywordsAndSummary=LinksKeywordsAndSummary)
    else:
        return render_template('index.html')



def index():
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
    titelundAbstracttogether = []

    for x in ArtikelLinks:
        driver.get(x)
        nachschauen = driver.find_elements(By.XPATH, "//html/body/div[2]/main/article/div[2]/section[1]/div/div/p ")
        titelExtrahieren = driver.find_elements(By.XPATH, "/html/body/div[2]/main/article/div[1]/header/h1")
        for titel in titelExtrahieren:
            print("TITEL")
            print(titel.text)
            ArticleTitles.append(titel.text)
        for e in nachschauen:
            print("ABSTRACT")
            print(e.text)
            docs.append(e.text)
        print(" ")

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

    print(final_keyWordArrayStorage)

    SummaryOfKeyword = []
    WikipediaLink = []
    for new in final_keyWordArrayStorage:
        try:
            print(new + ": " + wikipedia.summary(new))
            SummaryOfKeyword.append(wikipedia.summary(new))
            WikipediaLink.append(wikipedia.page(new).url)
        except:
            print(new + ": unfortunally no summary found for this word")
            pass
            continue

    print(" Array print: ", SummaryOfKeyword , WikipediaLink)

    finalArray = []

    for Keyword2RDF in final_keyWordArrayStorage:
        driver2 = webdriver.Firefox()
        driver2.get(
            "https://meshb.nlm.nih.gov/search?searchInField=termDescriptor&sort=&size=20&searchType=exactMatch&searchMethod=FullWord&q=" + Keyword2RDF)
        links2 = driver2.find_elements(By.XPATH, "/html/body/div[2]/div/div/div[1]/div/dl/dd[3]/a")
        for i in links2:
            intoString = i.get_attribute("href")
            intoString = str(intoString)
            finalArray.append(intoString)
            print(intoString)
            driver2.close()

    print(finalArray)

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

    print(neuerArray4)

    g = Graph()

    g.parse(neuerArray4[0])
    g.parse(neuerArray4[3])
    g.parse(neuerArray4[6])
    g.parse(neuerArray4[9])
    g.parse(neuerArray4[12])
    g.parse(neuerArray4[15])

    g.serialize(destination="tbl.ttl")
    datei = g.serialize(destination="tbl.ttl")

    n = len(g)
    print(f"Read {n} triples.")

    # from owlrl import DeductiveClosure, OWLRL_Semantics
    # DeductiveClosure(OWLRL_Semantics).expand(g)
    # print(f"Inferred {len(g) - n} triples, expansion ratio {(len(g) - n)/n:.3}.")

    g.serialize(destination="tbl.ttl")

    def visualize(graph):
        stream = io.StringIO()
        rdf2dot(graph, stream, opts={display})
        dg = pydotplus.graph_from_dot_data(stream.getvalue())
        png = dg.create_png()
        # display(Image(png))
        # print(png)
        # the png is generated as Bytes so we first need to convert it then save it as an image
        image = Image.open(io.BytesIO(png))
        image.save("tbl.png")
        print(image)

    visualize(g)


# f = Image.open("tbl.png").show()


if __name__ == '__main__':
        app.run(port=3200, debug=True)
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
