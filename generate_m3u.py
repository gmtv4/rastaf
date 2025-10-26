import yt_dlp
import concurrent.futures
import requests
import sys
import os

# Verifica se o caminho do arquivo de cookies foi passado como argumento
if len(sys.argv) != 2:
    print("Uso: python generate_m3u.py <caminho_para_cookies.txt>")
    sys.exit(1)

cookies_path = sys.argv[1]

# Verifica se o arquivo existe
if not os.path.exists(cookies_path):
    print(f"Erro: Arquivo de cookies não encontrado em '{cookies_path}'")
    sys.exit(1)

# Lista de URLs de canais do YouTube (pode adicionar mais)
globoplay_urls = [
    "https://www.youtube.com/@televisatijuanaof/live",
    "https://www.youtube.com/@TelevisaVeracruzOficial/live",
    "https://www.youtube.com/@aztecanoticias/live",
    "https://www.youtube.com/@televisamexicaliof/live",
    "https://www.youtube.com/@canal23televisaensenada97/live",
    "https://www.youtube.com/@multimedios/live",
    "https://www.youtube.com/@Nmasmty/live",
    "https://www.youtube.com/@noticiascaracol/live",
    "https://www.youtube.com/@noticias/live",
    "https://www.twitch.tv/erick_stephano0",
    "https://www.youtube.com/@France24_es/live",
    "https://www.youtube.com/@euronewses/live",
    "https://www.youtube.com/@euronewspt/live",
    "https://www.youtube.com/@televisapuebla/live",
    "https://www.youtube.com/@CarChaseChannelABC/live",
    "https://www.youtube.com/@lagranjavipmx/live",
    "https://www.youtube.com/@televisaguadalajara/live",
    "https://www.youtube.com/@ABCNews/live",
    "https://www.youtube.com/@CBSNews/live",
    "https://www.youtube.com/@NBCNews/live",
    "https://www.youtube.com/@CNNbrasil/live",
    "https://www.youtube.com/@cnnbrmoney/live",
    "https://www.youtube.com/@Laatusoficial/live",
    "https://www.youtube.com/@tcnewsoficial/live",
    "https://www.youtube.com/@ArenaTrader/live",
    "https://www.youtube.com/@ClearCorretoradeValores/live",
    "https://www.youtube.com/@CharllesNaderSHARKSSCHOOL/live",
    "https://www.youtube.com/@TOPGAIN/live",
    "https://www.youtube.com/@bandjornalismo/live",
    "https://www.youtube.com/@stories_das_celebridades/live",
    "https://www.youtube.com/@cmcapitalaovivo/live"
]

# Função que extrai título, link M3U8 e thumbnail
def extract_with_ytdlp(url):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'nocheckcertificate': True,
            'forcejson': True,
            'extract_flat': False,
            'cookiefile': cookies_path
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('uploader', 'Canal desconhecido')
            m3u8_url = info.get('url', '')
            thumbnail = info.get('thumbnail', '')

            if not thumbnail:
                for f in info.get('formats', []):
                    if f.get('format_note') == 'thumbnail' and f.get('url'):
                        thumbnail = f['url']
                        break

            if m3u8_url and '.m3u8' not in m3u8_url:
                for f in info.get('formats', []):
                    if f.get('ext') == 'mp4' and f.get('protocol') == 'm3u8':
                        m3u8_url = f.get('url')
                        break

            return title, m3u8_url, thumbnail or "https://upload.wikimedia.org/wikipedia/commons/1/1e/Globo_logo_2022.svg"
    except Exception as e:
        print(f"[✘] Erro com {url}: {e}")
        return None, None, None

# Caminho de saída do arquivo M3U
output_path = "PLAYLIST.m3u"

# Escreve o arquivo M3U
with open(output_path, "w", encoding='utf-8') as output_file:
    output_file.write("#EXTM3U\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_url = {executor.submit(extract_with_ytdlp, url): url for url in globoplay_urls}

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title, m3u8_url, thumbnail_url = future.result()
                if m3u8_url:
                    output_file.write(f'#EXTINF:-1 tvg-logo="{thumbnail_url}" group-title="NEWS WORLD",{title}\n')
                    output_file.write(f"{m3u8_url}\n")
                    print(f"[✔] Processado: {title}")
                else:
                    print(f"[!] M3U8 não encontrado para: {url}")
            except Exception as e:
                print(f"[✘] Erro ao processar {url}: {e}")
