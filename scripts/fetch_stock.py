import json
import requests
from bs4 import BeautifulSoup
import os


login_url = "https://www.riampa-auto.com/auto-amine/admin/auth/login"
url = "https://www.riampa-auto.com/auto-amine/admin/login"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.riampa-auto.com",
    "Referer": "https://www.riampa-auto.com/auto-amine/admin/login",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
def read_products_file():
    print("reading products file")
    with open("products.json", "r", encoding="utf-8") as f:
        for l in f:
            print(l)

USR = os.getenv("USR")
PSSWRD = os.getenv("PSSWRD")

session = requests.Session()
login_page = session.get(url, headers=headers)
soup = BeautifulSoup(login_page.text, "html.parser")
token_input = soup.find("input", {"name": "token"})["value"]

payload = {
    "token":token_input,
    "identity": USR,
    "password":PSSWRD

}
login_response = session.post(login_url,headers=headers,data=payload)


print("Login Status:", login_response.status_code)
print("Redirect:", login_response.headers.get("Location"))
print("Session cookies:", session.cookies.get_dict())
print(login_response.headers)


# Corps de la requête (identique au PowerShell)
payload = "sEcho=6&iColumns=14&sColumns=&iDisplayStart=0&iDisplayLength=-1&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&mDataProp_8=8&mDataProp_9=9&mDataProp_10=10&mDataProp_11=11&mDataProp_12=12&mDataProp_13=13&sSearch=BATTERIE&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&sSearch_4=&bRegex_4=false&bSearchable_4=true&sSearch_5=&bRegex_5=false&bSearchable_5=true&sSearch_6=&bRegex_6=false&bSearchable_6=true&sSearch_7=&bRegex_7=false&bSearchable_7=true&sSearch_8=&bRegex_8=false&bSearchable_8=true&sSearch_9=&bRegex_9=false&bSearchable_9=true&sSearch_10=&bRegex_10=false&bSearchable_10=true&sSearch_11=&bRegex_11=false&bSearchable_11=true&sSearch_12=&bRegex_12=false&bSearchable_12=true&sSearch_13=&bRegex_13=false&bSearchable_13=true&iSortCol_0=2&sSortDir_0=asc&iSortCol_1=3&sSortDir_1=asc&iSortingCols=2&bSortable_0=false&bSortable_1=false&bSortable_2=true&bSortable_3=true&bSortable_4=true&bSortable_5=true&bSortable_6=true&bSortable_7=true&bSortable_8=true&bSortable_9=true&bSortable_10=true&bSortable_11=true&bSortable_12=true&bSortable_13=false&token="+token_input

response = session.post(
    "https://www.riampa-auto.com/auto-amine/admin/products/getProducts",
    headers=headers,
    data=payload,
)
data_json = response.json()
read_products_file()
# Étape 3 : Nettoyage et structuration
def extraire_infos_produit(row):
    produit = {
        "id": row[0],
        "image": row[1],
        "code": row[2],
        "nom": row[3].strip(),
        "reference": row[4],
        "categorie": row[6],
        "prix_achat": float(row[7]) if row[7] else None,
        "prix_vente": float(row[8]) if row[8] else None,
        "stock": float(row[9]) if row[9] else None,
        "unite": row[10],
    
    }
    if produit["reference"][:4] == "0000" or produit["reference"] == "":
        print(f"produit non pris en compte reference: %s",produit["reference"])
        return

    soup = BeautifulSoup(row[13], "html.parser")
    liens = soup.find_all("a")
    for a in liens:
        texte = a.get_text(strip=True).lower()
        href = a.get("href")
        if "détails du produit" in texte:
            produit["lien_details"] = href
        elif "voir image" in texte:
            produit["lien_image"] = href

    return produit

produits_nets = [extraire_infos_produit(row) for row in data_json["aaData"]]

produits_filtré = [p for p in produits_nets if p]
for p in produits_filtré:
    p["marge"] = str((p["prix_vente"] - p["prix_achat"])*100 / p["prix_achat"])[:4] + "%"

# Étape 4 : Sauvegarde dans un fichier JSON
with open("products.json", "w", encoding="utf-8") as f:
    json.dump(produits_filtré, f, indent=2, ensure_ascii=False)

print(f"{len(produits_nets)} produits exportés vers 'products.json'")

