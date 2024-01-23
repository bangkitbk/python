import requests
from bs4 import BeautifulSoup
import json

def scrape_tribunnews(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
    response = requests.get(url, headers=headers)

    
    # Memastikan permintaan berhasil
    if response.status_code == 200:
        # Menggunakan BeautifulSoup untuk melakukan parsing HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
       # Mendapatkan Judul
        title_element = soup.find('h1', {'class': 'f50 black2 f400 crimson', 'style': 'line-height:110%', 'id': 'arttitle'})
        title = title_element.text.strip() if title_element else ''

        # Mendapatkan Link Foto
        photo_element = soup.find('img', class_='imgfull')
        photo_link = photo_element['src'] if photo_element else ''

        # Mendapatkan Konten
        content_div = soup.find('div', class_='side-article txt-article multi-fontsize')
        content_elements = content_div.find_all('p') if content_div else None

        # Inisialisasi variabel untuk menyimpan teks dari semua elemen <p>
        content_texts = []

        # Loop melalui setiap elemen <p> dan tambahkan teksnya ke dalam list
        if content_elements:
            for element in content_elements:
                content_texts.append(element.get_text(strip=True))

        # Menggabungkan teks dari semua elemen <p> menggunakan separator spasi
        content = ' '.join(content_texts) if content_texts else ''

       

        # Mendapatkan Penulis
        penulis_div = soup.find('div', {'id': 'penulis'})
        author_element = penulis_div.find('a') if penulis_div else None
        author = author_element.text.strip() if author_element else ''

        # Mendapatkan Editor
        editor_div = soup.find('div', {'id': 'editor'})
        editor_element = editor_div.find('a') if editor_div else None
        editor = editor_element.text.strip() if editor_element else ''

        # Mengonversi data ke dalam format JSON
        data = {
            "judul": title,
            "link_photo": photo_link,
            "konten": content,
            "penulis": author,
            "editor": editor
        }
        
        # Mengembalikan data dalam format JSON
        return json.dumps(data, ensure_ascii=False, indent=2)

    else:
        # Menampilkan pesan jika permintaan tidak berhasil
        print(f"Failed to retrieve data. Status Code: {response.status_code}")

# URL yang akan di-scrape
url = "https://www.tribunnews.com/superskor/2024/01/05/resmi-jadi-pelatih-persebaya-paul-munster-saya-punya-rencana-jangka-panjang"

# Menjalankan fungsi scraping
result = scrape_tribunnews(url)

# Menampilkan hasil dalam bentuk JSON
print(result)
