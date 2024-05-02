from lxml import etree
import json
import re

def extractXpath(pages):
    results = []

    for page in pages:
        with open(page, "rb") as file:
            f = file.read()
        parser = etree.HTMLParser()
        tree = etree.fromstring(f, parser)

        data = {}
        id = 1

        if 'overstock' in page:
            objects = tree.xpath('//tbody/tr[contains(@bgcolor, "#ffffff") or contains(@bgcolor, "#dddddd")][count(td[@valign="top"]) = 2]/td[2]')
            for obj in objects:
                title = obj.xpath('string(a/b/text())')
                list_price = obj.xpath('string(.//s/text())')
                price = obj.xpath('string(.//span/b/text())')
                saving = obj.xpath('substring-before(table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text(), " ")')
                saving_percent = obj.xpath('substring(substring-after(table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text(), " "),2 ,3)')
                content = obj.xpath('string(table/tbody/tr/td[2]/span/text())')

                item = {
                    'Title': title,
                    'listPrice': list_price,
                    'price': price,
                    'saving': saving,
                    'savingPercent': saving_percent,
                    'content': content
                }
                data[id] = item
                id += 1


        elif 'rtvslo' in page:
            rootObject = tree.xpath('//div[contains(@class, "news-container")]/div')[0]
            item = {
                'Title': rootObject.xpath('string(header/h1/text())'),
                'SubTitle': rootObject.xpath('string(.//div[@class="subtitle"]/text())'),
                'Lead': rootObject.xpath('string(.//p[@class="lead"]/text())'),
                'Author': rootObject.xpath('string(.//div[@class="author-name"]/text())'),
                'PublishTime': re.sub('[^A-Za-z0-9.: ]+', '', rootObject.xpath('string(div[@class="article-meta"]/div[@class="publish-meta"]/text())')),
                'Content': "\n".join([p.xpath('string(.)') for p in rootObject.xpath('.//div[@class="article-body"]//p')])
            }

        
            data[id] = item
            id += 1
            
        results.append(data)

    with open("result/Boutput.json", "w") as outfile:
        json.dump(results, outfile, indent=4)


