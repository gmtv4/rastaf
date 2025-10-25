import requests
from bs4 import BeautifulSoup
import datetime
import time
import re
import os

# Define o nome do arquivo de saída conforme solicitado pelo usuário
OUTPUT_FILE = "portugal.m3u"
BASE_URL = "https://tviplayer.iol.pt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def get_video_details(page_number):
    """Extrai detalhes dos vídeos de uma página específica da seção 'últimos'."""
    # A URL correta é https://tviplayer.iol.pt/ultimos?page={page_number}
    url = f"{BASE_URL}/ultimos?page={page_number}"
    print(f"A processar página: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # Lança exceção para códigos de status HTTP ruins (4xx ou 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    
    # O seletor mudou. Agora os vídeos estão em <a> com a classe 'item-card'.
    video_cards = soup.find_all("a", class_="item-card")
    
    details = []
    for card in video_cards:
        try:
            # 1. Link do vídeo
            link = card.get('href')
            if not link or not link.startswith('/'):
                continue # Pular se o link não for válido

            full_link = f"{BASE_URL}{link}"

            # 2. Imagem (tvg-logo)
            # A imagem está no estilo background-image de um elemento dentro do card
            style_tag_element = card.find("div", class_="item-card-image-wrapper")
            if style_tag_element:
                style_tag = style_tag_element.get("style")
                image_match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style_tag)
                image_url = image_match.group(1) if image_match else ""
            else:
                image_url = ""

            # 3. Título e Subtítulo
            # O título principal do vídeo está em 'item-card-title'
            title_element = card.find("span", class_="item-card-title")
            title = title_element.text.strip() if title_element else "Sem Título"
            
            # O subtítulo (programa) está em 'item-card-program-title'
            subtitle_element = card.find("span", class_="item-card-program-title")
            subtitle = subtitle_element.text.strip() if subtitle_element else "Sem Programa"
            
            details.append({
                "title": title,
                "subtitle": subtitle,
                "link": full_link,
                "image_url": image_url
            })
            
        except Exception as e:
            print(f"Aviso: Não foi possível extrair todos os detalhes de um card. Erro: {e}")
            continue
            
    return details

def write_m3u_file(video_details):
    """Escreve os detalhes dos vídeos no arquivo M3U no formato EXTINF."""
    
    # O streamlink falhou consistentemente porque o TVI Player usa DRM e links temporários.
    # O link final do vídeo não pode ser obtido via streamlink.
    # Vamos gerar a playlist com uma URL informativa no lugar do link M3U8.

    with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u8_file:
        m3u8_file.write("#EXTM3U\n") # Adiciona o cabeçalho M3U
        
        count = 0
        for detail in video_details:
            # O link do vídeo é o link da página do IOL/TVI Player
            link_da_pagina = detail["link"]
            
            # URL de substituição informativa
            # O link M3U8 FINAL não pode ser obtido, então usamos o link da página
            # com um aviso.
            video_url_substituto = f"http://URL_NAO_DISPONIVEL_VIA_SCRAPING_DRM_TVI_PLAYER_VISITE_A_PAGINA:{link_da_pagina}"
            
            title_clean = detail["title"].replace(",", "").replace("\n", " ")
            subtitle_clean = detail["subtitle"].replace(",", "").replace("\n", " ")
            
            m3u8_file.write(
                f'#EXTINF:-1 group-title="TVI PLAYER" tvg-logo="{detail["image_url"]}",{subtitle_clean} - {title_clean}\n'
            )
            m3u8_file.write(f"{video_url_substituto}\n")
            m3u8_file.write("\n")
            count += 1
        
        print(f"Geração da playlist concluída. {count} vídeos adicionados. Arquivo salvo como: {OUTPUT_FILE}")
        print("ATENÇÃO: Os links de vídeo na playlist são substitutos, pois o streamlink não conseguiu extrair os links M3U8 reais devido a restrições de DRM/links temporários do TVI Player.")


def main():
    all_video_details = []
    # O usuário original estava a iterar de 1 a 5. Vamos manter a iteração para 5 páginas.
    for i in range(1, 6):
        details = get_video_details(i)
        all_video_details.extend(details)
        # Adiciona um pequeno atraso para evitar ser bloqueado
        time.sleep(1) 

    write_m3u_file(all_video_details)

if __name__ == "__main__":
    main()

