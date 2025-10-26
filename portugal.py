import requests
from bs4 import BeautifulSoup
import re
import os

OUTPUT_FILE = "portugal.m3u"
BASE_URL = "https://tviplayer.iol.pt"
HTML_FILE = "rendered_page.html"

def extract_video_details_from_html(html_content):
    """Extrai detalhes dos vídeos do HTML renderizado."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Encontrar todos os cards de vídeo na seção 'list-items' (últimos vídeos)
    list_items_div = soup.find("div", class_="list-items")
    if not list_items_div:
        print("Erro: Não foi possível encontrar a div 'list-items'.")
        return []

    video_cards = list_items_div.find_all("a", class_="item-card")
    
    details = []
    for card in video_cards:
        try:
            # 1. Link do vídeo
            link = card.get('href')
            if not link or not link.startswith('/'):
                continue

            full_link = f"{BASE_URL}{link}"

            # 2. Imagem (tvg-logo)
            image_url = ""
            style_tag_element = card.find("div", class_="item-card-image-wrapper")
            if style_tag_element:
                style_tag = style_tag_element.get("style")
                image_match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style_tag)
                image_url = image_match.group(1) if image_match else ""

            # 3. Título e Subtítulo
            title_element = card.find("span", class_="item-card-title")
            title = title_element.text.strip() if title_element else "Sem Título"
            
            subtitle_element = card.find("span", class_="item-card-program-title")
            subtitle = subtitle_element.text.strip() if subtitle_element else "Sem Programa"
            
            if title != "Sem Título" or subtitle != "Sem Programa":
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
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u8_file:
        m3u8_file.write("#EXTM3U\n")
        
        count = 0
        for detail in video_details:
            link_da_pagina = detail["link"]
            
            # URL de substituição informativa, pois o link M3U8 real não pode ser obtido
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
        print("ATENÇÃO: Os links de vídeo na playlist são substitutos, pois o link M3U8 real não pode ser extraído devido a restrições de DRM/links temporários do TVI Player.")


def main():
    if not os.path.exists(HTML_FILE):
        print(f"Erro: Arquivo {HTML_FILE} não encontrado. Por favor, execute a extração do HTML primeiro.")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    video_details = extract_video_details_from_html(html_content)
    write_m3u_file(video_details)

if __name__ == "__main__":
    main()

