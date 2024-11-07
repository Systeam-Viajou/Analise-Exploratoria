import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import unicodedata
from ydata_profiling import ProfileReport


# Função para normalizar os nomes das cidades
def normalize_city_names(cities_list):
    normalized_cities = []
    for city in cities_list:
        city = city.replace(" ", "-").lower()
        city = unicodedata.normalize('NFKD', city).encode('ascii', 'ignore').decode('ascii')
        normalized_cities.append(city)
    return normalized_cities

# Configuração do navegador
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Modo headless opcional
driver = webdriver.Chrome(options=chrome_options)

# Lista para armazenar os dados
data = []

# URL do site
url = 'https://www.civitatis.com/pt/procurar?q=brasil'
driver.get(url)
time.sleep(3)

# XPath para capturar todos os nomes dos lugares
places_xpath = '/html/body/div[3]/main/section[1]/div/div/div/div/div/a/span'
places_elements = driver.find_elements(By.XPATH, places_xpath)

# Capturar e normalizar os nomes dos lugares
places = [place.text for place in places_elements]
    
places_url = normalize_city_names(places)

# Iterar por cada lugar e coletar os títulos
for i, lugar_url in enumerate(places_url):
    print("Página: ", lugar_url)
    url = f'https://www.civitatis.com/pt/{lugar_url}'
    driver.get(url)
    time.sleep(3)
    
    # Encontrar o número máximo de páginas
    pagination_elements = driver.find_elements(By.XPATH, '/html/body/div[3]/main/section/div/div/div[2]/div[1]/div/div[5]/div/nav/div[2]/a')
    if pagination_elements:
        last_page_text = pagination_elements[-1].text
        max_page_number = int(last_page_text.split()[-1])
    else:
        max_page_number = 1

    print("Quantidade de páginas no lugar", max_page_number)
    
    # Iterar por todas as páginas e coletar os títulos
    for contador in range(1, max_page_number + 1):
        url = f'https://www.civitatis.com/pt/{lugar_url}/{contador}'
        driver.get(url)
        time.sleep(5)
        
        print("Página: ", contador, "Lugar: ", places[i])
        titles_xpath = '/html/body/div[3]/main/section/div/div/div[2]/div[1]/div/div[2]/div/article/a[2]/div[2]/div[1]/h2'
        avaliation_xpath = '/html/body/div[3]/main/section/div/div/div[2]/div[1]/div/div[2]/div/article/a[2]/div[2]/div[1]/div/div[1]/span[1]'
        duration_xpath = '/html/body/div[3]/main/section/div/div/div[2]/div[1]/div/div[2]/div/article/a[2]/div[2]/div[3]/div[1]/div[1]/span[1]'
        category_xpath = '/html/body/div[3]/main/section/div/div/div[2]/div[1]/div/div[2]/div/article/a[2]/div[2]/div[3]/div[1]/div[1]/span[3]'
        price_xpath = '/html/body/div[3]/main/section/div/div/div[2]/div[1]/div/div[2]/div/article/a[2]/div[2]/div[3]/div[2]/div/span'
        
        titles_elements = driver.find_elements(By.XPATH, titles_xpath)
        avaliation_elements = driver.find_elements(By.XPATH, avaliation_xpath)
        duration_elements = driver.find_elements(By.XPATH, duration_xpath)
        category_elements = driver.find_elements(By.XPATH, category_xpath)
        price_elements = driver.find_elements(By.XPATH, price_xpath)

        # Verificar o tamanho de cada lista para evitar indexação fora do limite
        for idx in range(len(titles_elements)):
            title = titles_elements[idx].text
            avaliation = avaliation_elements[idx].text if idx < len(avaliation_elements) else None
            duration = duration_elements[idx].text if idx < len(duration_elements) else None
            category = category_elements[idx].text if idx < len(category_elements) else None
            price = price_elements[idx].text if idx < len(price_elements) else None

            if title != 'Chip eSIM Civitatis Brasil' and title.startswith("Transfers") == False:
                data.append({
                    'local': places[i], 
                    'titulo': title, 
                    'avaliacao': avaliation,
                    'duracao': duration,
                    'categoria': category,
                    'preco': price
                })

# Criar o DataFrame e salvar em um arquivo Excel
df = pd.DataFrame(data)

# Removendo linhas vazias
df.dropna(inplace=True)
df.to_excel('civitatis.xlsx', index=False)

# Fechar o navegador
driver.quit()

print("Processo concluído. Dados salvos em civitatis.xlsx")
