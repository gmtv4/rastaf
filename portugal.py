import os
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver

# ==============================
# CONFIGURAÇÕES
# ==============================
BASE_URL = "https://tviplayer.iol.pt"
URL_TVI_PLAYER = "https://tviplayer.iol.pt/programas/jornal-nacional"  # 👉 altere se quiser outro programa
OUTPUT_FILE = "portugal.m3u"
HTML_FILE = "rendered_page.html"


# ==============================
# ETAPA 1: BAIXAR HTML RENDERIZADO (via Selenium)
# ==============================
def baixar_html_renderizado(url, output_file):
    """Usa Selenium para renderizar e salvar o HTML completo do TVI Player."""
    print(f"🔄 Baixando página renderizada: {url}")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(6)  # Aguarda o carregamento do conteúdo dinâmico

    html = driver.page_source
    driver.quit()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML renderizado salvo em: {output_file}")


# ==============================
# ETAPA 2: EXTRAIR DETALHES DOS VÍDEOS
# ==============================
def extract_video_details_from_html(html_content):
    """Extrai detalhes dos vídeos do HTML renderizado."""
    soup = BeautifulSoup(html_content, "html.parser")
    details = []

    # --- FORMATO ANTIGO ---
    list_items_div = soup.find("div", class_="list-items")
    if list_items_div:
        video_cards = list_items_div.find_all("a", class_="item-card")
        for card in video_cards:
            try:
                link = card.get("href")
                if not link or not link.startswith("/"):
                    continue
                full_link = f"{BASE_URL}{link}"

                # Imagem
                image_url = ""
                style_tag_element = card.find("div", class_="item-card-image-wrapper")
                if style_tag_element:
                    style_tag = style_tag_element.get("style")
                    image_match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style_tag)
                    image_url = image_match.group(1) if image_match else ""

                title_element = card.find("span", class_="item-card-title")
                title = title_element.text.strip() if title_element else "Sem Título"

                subtitle_element = card.find("span", class_="item-card-program-title")
                subtitle = subtitle_element.text.strip() if subtitle_element else "Sem Programa"

                details.append({
                    "title": title,
                    "subtitle": subtitle,
                    "link": full_link,
                    "image_url": image_url,
                    "duration": ""
                })
            except Exception as e:
                print(f"Aviso: erro ao processar card antigo. {e}")

    # --- NOVO FORMATO (<li class="item">) ---
    li_items = soup.find_all("li", class_="item")
    for li in li_items:
        try:
            a_tag = li.find("a", href=True)
            if not a_tag:
                continue
            link = a_tag["href"]
            if not link.startswith("/"):
                continue
            full_link = f"{BASE_URL}{link}"

            # Imagem
            img_tag = li.find("img")
            image_url = img_tag["src"] if img_tag else ""

            # Título e subtítulo
            name_span = li.find("span", class_="item--name")
            title = name_span.text.strip() if name_span else "Sem Título"

            title_span = li.find("span", class_="item--title")
            subtitle = title_span.text.strip() if title_span else "Sem Programa"

            # Duração (opcional)
            duration_span = li.find("span", class_="item--duration")
            duration = duration_span.text.strip() if duration_span else ""

            details.append({
                "title": title,
                "subtitle": subtitle,
                "duration": duration,
                "link": full_link,
                "image_url": image_url
            })
        except Exception as e:
            print(f"Aviso: erro ao processar item <li>. {e}")

    return details


# ==============================
# ETAPA 3: GERAR PLAYLIST .M3U
# ==============================
def write_m3u_file(video_details):
    """Gera o arquivo M3U com as informações dos vídeos."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as m3u8_file:
        m3u8_file.write("#EXTM3U\n")

        count = 0
        for detail in video_details:
            link_da_pagina = detail["link"]
            video_url_substituto = (
                f"http://URL_NAO_DISPONIVEL_VIA_SCRAPING_TVI_PLAYER_USE_STREAMLINK:{link_da_pagina}"
            )

            title_clean = detail.get("title", "").replace(",", "").replace("\n", " ")
            subtitle_clean = detail.get("subtitle", "").replace(",", "").replace("\n", " ")
            image_url = detail.get("image_url", "")
            duration = detail.get("duration", "")

            m3u8_file.write(
                f'#EXTINF:-1 group-title="TVI PLAYER" tvg-logo="{image_url}",{subtitle_clean} - {title_clean} ({duration})\n'
            )
            m3u8_file.write(f"{video_url_substituto}\n\n")
            count += 1

        print(f"✅ Playlist gerada: {OUTPUT_FILE} ({count} vídeos adicionados)")
        print("⚠️ Os links são substitutos. Para abrir o vídeo real, use:")
        print("   streamlink 'https://tviplayer.iol.pt/programa/.../video/...' best")


# ==============================
# MAIN
# ==============================
def main():
    # Baixa o HTML automaticamente, se ainda não existir
    if not os.path.exists(HTML_FILE):
        baixar_html_renderizado(URL_TVI_PLAYER, HTML_FILE)

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    video_details = extract_video_details_from_html(html_content)
    if not video_details:
        print("❌ Nenhum vídeo encontrado no HTML.")
        return

    write_m3u_file(video_details)


if __name__ == "__main__":
    main()
