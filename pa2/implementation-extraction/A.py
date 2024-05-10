import re
import json
from bs4 import BeautifulSoup


def extractRegex(pages):
    results = []

    for page in pages:
        item_id = 1
        with open(page, "r") as file:
            parsed_page = str(BeautifulSoup(file.read(), 'html.parser'))

        if 'overstock' in parsed_page:
            regex = r'<b>([0-9].+)<\/b>.*\n.*\n.*<s>([\$0-9,.]+).*\n.*<b>([\$0-9.]+).*\n.*>([\$0-9.,]+)\s.([0-9]+%)' \
                    r'.*\n.*\n.*<span class=\"normal\">(.*|.*\n.*\n.*|.*\n.*\n.*\n.*)<br\/><a'
            params = ['Title', 'ListPrice', 'Price',
                      'Saving', 'SavingPercent', 'Content']
        elif 'rtvslo' in parsed_page:
            regex = r"<h1>(.*)<\/h1>[\s\S]+<div class=\"subtitle\">(.*)<\/div>[\s\S]+<p class=\"lead\">(.*)<\/p>[\s\S]+<div class=\"author-name\">(.*)<\/div>[\s\S]+\"publish-meta\">[\n\W]+(.*)<br\/>[\s\S]+<\/div>[\n]*<\/figure>[\n]*<p([\s\S]*.*)<div class=\"gallery\">"
            params = ['Title', 'Subtitle', 'Lead',
                      'Author', 'PublishTime', 'Content']
        else:
            # regex = r"<title>(.*?)<\/title>[\s\S]+?<meta content='(.*?)' name=\"description\"\/>[\s\S]+?<div class='(.*?)' \"price\"[^>]*>(.*?)<\/div>"
            regex = r"<title>(.*?)<\/title>[\s\S]+?<meta content='(.*?)' name=\"description\"\/>"
            # params = ['Title', 'Description', 'Price']
            params = ['Title', 'Description']

        if 'overstock' in parsed_page or 'rtvslo' in parsed_page:
            matches = re.finditer(regex, parsed_page)
        else:
            matches = re.finditer(regex, parsed_page, re.DOTALL)

        for match in matches:
            result = {}
            for i, param in enumerate(params):

                if param == 'Content' and 'rtvslo' in parsed_page:
                    content = '\n'.join(line.strip() for line in BeautifulSoup(match.group(
                        i+1), 'html.parser').get_text(separator='\n').split('\n') if line.strip())
                    result[param] = content
                else:
                    result[param] = match.group(i+1)
            numbered_result = {str(item_id): result}
            results.append(numbered_result)
            item_id += 1

    with open("result/Aoutput.json", "w") as outfile:
        json.dump(results, outfile, indent=4)
