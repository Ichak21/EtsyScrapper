from bs4 import BeautifulSoup
import requests
import pandas as pd

MA_RECHERCHE = ""
MAX_PAGE = 0

def est_nombre(chaine):
    try:
        int(chaine)  # Tente de convertir la chaîne en nombre flottant
        return True
    except ValueError:
        return False

def do_etsy_request(research:str, page:int):
    url = 'https://www.etsy.com/fr/search?q='
    research = research.replace(' ', '%20')
    url = url + research + '&page='+ str(page)
    return url

def page_loader(url:str):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.etsy.com/',  # Referer spécifique à Etsy
    'Cache-Control': 'max-age=0',
    'DNT': '1',  # Do Not Track
    'Upgrade-Insecure-Requests': '1'
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text,'html.parser')
    return soup, page.status_code

def scrapp(reseach:str, maxpage:int):

    column = ["Lien image","Nom du produit","Note","Nombre de votes","Nom de la boutique","Prix","Symbol","Lien vers le produit"]
    column_page= ["Num_page", "URL", "Status_HTTP", "Nb Retry", "Nb_Products"]
    rows=[]
    pages=[]
    nb_page_found = 0
    nb_page_ignore = 0
    nb_product_find = 0
    nb_product_ignore =0

    for page in range(1, maxpage + 1):
        page_data=[]
        url = do_etsy_request(reseach, page)

        for retry in range(1, 15):
            soup, status = page_loader(url=url)
            if status == 200 :
                # print(str(page) + " | "+ url + " -- " + str(status) + "---> [" + str(retry) + "]")
                page_data.append(page)
                page_data.append(url)
                page_data.append(status)
                page_data.append(retry)
                nb_page_found += 1
                break

        if status == 200:
            search_results = soup.find('div', attrs={'data-search-results':True})
            elements = search_results.find_all('li')
            product_find = 0

            for el in elements:
                if not el.find('img', class_='wt-width-full') == None:
                    if 'style' not in el.attrs:
                        nb_product_find += 1
                        row = []

                        # Lien vers l'image
                        img_link = el.find('img', class_='wt-width-full').get('src', '')
                    
                        # Nom du produit
                        product_name = el.find('h3', class_='v2-listing-card__title').text.strip()
                    
                        # Note et votes
                        if not el.find('div', class_='wt-align-items-center wt-max-height-full wt-display-flex-xs flex-direction-row-xs wt-text-title-small wt-no-wrap') == None:
                            note = el.find('div', class_='wt-align-items-center wt-max-height-full wt-display-flex-xs flex-direction-row-xs wt-text-title-small wt-no-wrap').text.strip()
                            note,_ , votes = note.split('\n')
                        else : 
                            note = "NA"
                            votes = "NA"
                    
                        # Nom de la boutique
                        all_span = el.find_all('p')[1].find_all("span")
                        if len(all_span) > 3:
                            shop_name = all_span[3].text.strip()
                        else:
                            shop_name="Not Found"
                    
                        # Prix
                        price_value = el.find('span', class_='currency-value').text.strip()
                        price_symbol = el.find('span', class_='currency-symbol').text.strip()

                        # Lien vers le produit
                        product_link = el.find('a', class_='listing-link').get('href', '')

                        # Afficher les informations
                        # print(f"Lien vers l'image : {img_link}")
                        row.append(img_link)
                        # print(f"Nom du produit : {product_name}")
                        row.append(product_name)
                        # print(f"Note : {note}")
                        row.append(note)
                        # print(f"Nombre de votes : {votes}")
                        row.append(votes)
                        # print(f"Nom de la boutique : {shop_name}")
                        row.append(shop_name)
                        # print(f"Prix : {price_value} {price_symbol}")
                        row.append(price_value)
                        row.append(price_symbol)
                        # print(f"Lien vers le produit : {product_link}")
                        row.append(product_link)
                        # print('-' * 50)  # Pour séparer les informations de différents produits
                        product_find += 1
                        rows.append(row)
                    else:
                        nb_product_ignore += 1
                        # pass
                else:
                    pass
        else:
            nb_page_ignore += 1
            # pass

        percent = round((page/maxpage)*100,0)
        print(f'%{percent} | {page} pages done on {(maxpage)} pages ')
        page_data.append(product_find)
        pages.append(page_data)

    output = pd.DataFrame(rows, columns=column)
    output_page = pd.DataFrame(pages, columns=column_page)
    kpi = {
    "page_found": nb_page_found,
    "page_ignore": nb_page_ignore,
    "product_find": nb_product_find,
    "product_ignore": nb_product_ignore
    }
    # print(f"RESULTAT SCRAPPER | Nb page found [{nb_page_found}]| Nb page ignored [{nb_page_ignore}]| Nb products found [{nb_product_find}]| Nb product ignored [{nb_product_ignore}]")
    return output, output_page, kpi

def main():
    while(True):
        MA_RECHERCHE = input("Saisie la recherche : ")
        if type(MA_RECHERCHE) == str and MA_RECHERCHE != "" :
            # print(type(MA_RECHERCHE))
            break

    while(True):
        MAX_PAGE = input("Saisie le nombre de page : ")
        if est_nombre(MAX_PAGE) and int(MAX_PAGE) > 0 :
            # print(type(int(MAX_PAGE)))
            break

    print(f'REQUETE : {MA_RECHERCHE} sur {MAX_PAGE} pages <=====')
    print(f'====================================================')

    data_file = "./data/etsy_data_" + MA_RECHERCHE.replace(' ','_') + '.csv'
    page_file = "./page/etsy_page_" + MA_RECHERCHE.replace(' ','_') + '.csv'

    print(f'Les fichier de sortie :')
    print(f'=> Pour la liste des page traité : {page_file}')
    print(f'=> Pour les données recolté : {data_file}')

    ma_data, page_data, kpi = scrapp(MA_RECHERCHE, int(MAX_PAGE))

    ma_data.to_csv(data_file, sep=";",encoding="utf-8-sig",index=False)
    page_data.to_csv(page_file, sep=";",encoding="utf-8-sig",index=False)

    print(kpi)


if __name__ == "__main__":
    main()