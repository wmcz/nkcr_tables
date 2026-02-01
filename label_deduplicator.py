import requests
import simplejson
from wikibaseintegrator import wbi_helpers, WikibaseIntegrator, wbi_login
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator.wbi_exceptions import ModificationFailed

wbi_config['USER_AGENT'] = 'Frettiebot/1.0 (https://www.wikidata.org/wiki/User:Frettiebot)'
wbi_config['SPARQL_ENDPOINT_URL'] = 'https://qlever.cs.uni-freiburg.de/api/wikidata'
login_instance = wbi_login.Login(user='Frettiebot', password='wikibaseintegrator@g3roop93tdhq0gdvku1d079j2pd51ah5')
wbi = WikibaseIntegrator(login=login_instance, is_bot=True)


def get_data():
    url = "https://qlever.cs.uni-freiburg.de/api/wikidata?query=PREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX+wdt%3A+%3Chttp%3A%2F%2Fwww.wikidata.org%2Fprop%2Fdirect%2F%3E%0Aselect+%3Fitem+%3Flabel+%3Fname1+%3Fname2+where+%7B%0A++%0A+++%3Fitem+wdt%3AP691+%5B%5D+.%0A+++%3Fitem+rdfs%3Alabel+%3Flabel+filter%28lang%28%3Flabel%29%3D%22cs%22+%26%26+regex%28%3Flabel%2C%22%5E%5B%5E+%5D%2B+%5B%5E+%5D%2B%24%22%29+%29+.%0A+++BIND%28REPLACE%28STR%28%3Flabel%29%2C+%22%5E%5B%5E+%5D%2B+%22%2C+%22%22%29+AS+%3Fname1%29+%0A+++BIND%28REPLACE%28STR%28%3Flabel%29%2C+%22+%5B%5E+%5D%2B%24%22%2C+%22%22%29+AS+%3Fname2%29%0A+++FILTER%28%3Fname1+%3D+%3Fname2%29%0A%7D"
    try:
        response = requests.get(url)
        data = response.json()
    except (simplejson.errors.JSONDecodeError, requests.exceptions.ConnectionError) as e:
        print(e)
        return

    count = 0
    for item in data['results']['bindings']:
        count += 1
        if count % 10 == 0:
            print(count)
        qid = item['item']['value'].replace('http://www.wikidata.org/entity/', '')
        obj = wbi.item.get(qid)
        label_cs = str(obj.labels.get('cs').value)
        try:
            label_en = str(obj.labels.get('en').value)
        except (TypeError, AttributeError):
            label_en = ""
        splitted = label_cs.split(' ')
        obj.labels.set('cs', splitted[0])
        try:
            if label_en != label_cs and len(splitted) == 2:
                obj.write(summary='clean cs label (deduplicate)')
                print('writed')
                print(qid)
        except ModificationFailed as e:
            print(e)
            print(qid)


if __name__ == '__main__':
    get_data()
