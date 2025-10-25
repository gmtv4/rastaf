import requests
from bs4 import BeautifulSoup
import time
import os

# Nome do arquivo de saída
OUTPUT_FILE = "portugal.m3u"
BASE_URL = "https://tviplayer.iol.pt/ultimos"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}

def get_video_details(page_number=1):
    """Extrai detalhes dos vídeos da página 'Últimos'."""
    url = f"{BASE_URL}/ultimos?page={page_number}"
    print(f"➡️ A processar página: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao aceder {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("li", class_="item")

    if not items:
        print("⚠️ Nenhum item encontrado na página.")
        return []

    details = []
    for li in items:
        try:
            # Extrai o link
            a_tag = li.find("a", href=True)
            if not a_tag:
                continue
            link = a_tag["href"]
            if not link.startswith("http"):
                link = BASE_URL + link

            # Extrai imagem
            img_tag = li.find("img")
            image_url = img_tag["src"] if img_tag else ""

            # Extrai título e nome do programa
            program_name = li.find("span", class_="item--name")
            title = li.find("span", class_="item--title")
            duration = li.find("span", class_="item--duration")

            program = program_name.text.strip() if program_name else "Sem Programa"
            title_text = title.text.strip() if title else "Sem Título"
            duration_text = duration.text.strip() if duration else ""

            details.append({
                "title": title_text,
                "program": program,
                "duration": duration_text,
                "link": link,
                "image_url": image_url
            })

        except Exception as e:
            print(f"⚠️ Erro ao processar item: {e}")
            continue

    return details

def write_m3u_file(video_details):
    """Cria um arquivo M3U com os detalhes obtidos."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for v in video_details:
            fake_url = f"http://DRM_PROTEGIDO_VISITE:{v['link']}"
            f.write(
                f'#EXTINF:-1 group-title="TVI PLAYER" tvg-logo="{v["image_url"]}",{v["program"]} - {v["title"]} ({v["duration"]})\n'
            )
            f.write(fake_url + "\n\n")

    print(f"✅ Playlist M3U criada com {len(video_details)} vídeos → {OUTPUT_FILE}")
    print("⚠️ Os links reais de stream não podem ser obtidos (DRM ativo).")

def main():
    all_videos = []
    # Podes ajustar o número de páginas aqui
    for page in range(1, 6):
        videos = get_video_details(page)
        all_videos.extend(videos)
        time.sleep(1)
    write_m3u_file(all_videos)

if __name__ == "__main__":
    main()
