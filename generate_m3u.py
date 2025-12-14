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
    "https://www.youtube.com/watch?v=G_7kxV8jKV0",  # 6abc Philadelphia
    "https://www.youtube.com/watch?v=SDK_m1_BVJ4",  # ABC13 Houston
    "https://www.youtube.com/watch?v=5lSMFuW_51s",  # 4 News Now
    "https://www.youtube.com/watch?v=s3iVFJoxrYc",  # ABC7
    "https://www.youtube.com/watch?v=RqUZ2Fv9l8w",  # ARY News
    "https://www.youtube.com/watch?v=jaB8i8npPZc",  # CBS 42
    "https://www.youtube.com/watch?v=1rWgAIyFH4o",  # CanmoreAlberta.com
    "https://www.youtube.com/watch?v=Qr61waJ6AZg",  # CNN en Español
    "https://www.youtube.com/watch?v=tNlfkKQ6jCU",  # CNN Brasil
    "https://www.youtube.com/watch?v=6N8_r2uwLEc",  # CNN TÜRK
    "https://www.youtube.com/watch?v=w-VOdz1XSng",  # CNN-News18
    "https://www.youtube.com/watch?v=2onez39FUc0",  # Canal 12 Trenque Lauquen
    "https://www.youtube.com/watch?v=LIeND9IgRIk",  # Diputados TV
    "https://www.youtube.com/watch?v=OGKI-lcm4rs",  # Denver7
    "https://www.youtube.com/watch?v=EjIF9jS46cU",  # FOX 29 Philadelphia
    "https://www.youtube.com/watch?v=o4PB-FPEToM",  # FOX 11 Los Angeles
    "https://www.youtube.com/watch?v=KXSqZkPzxm8",  # NBC News
    "https://www.youtube.com/watch?v=FqQJmDiW0xs",  # National Geographic
    "https://www.youtube.com/watch?v=Lly8TzZXImQ",  # Newsmax
    "https://www.youtube.com/watch?v=mKvIkuSAqV8",  # TVN
    "https://www.youtube.com/watch?v=k4HCyWrXVUw",  # WPLG Local 10
    "https://www.youtube.com/watch?v=VQPQo0xAZSQ",  # Tampa Bay 28
    "https://www.youtube.com/watch?v=_VqvVJfmyfs",  # ABC7 News Bay Area
    "https://www.youtube.com/watch?v=zcWXboTnous"   # América TV
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
