# importer/m3u_to_json.py
import re
import json
import os

def parse_m3u(relative_file_path, output_relative_path='output/movies.json'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, relative_file_path)
    output_path = os.path.join(script_dir, output_relative_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    items = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            name = re.search(r',(.+)$', line)
            title = name.group(1).strip() if name else "Unknown"

            logo = re.search(r'tvg-logo="([^"]*)"', line)
            thumbnail = logo.group(1) if logo else ""

            # استخراج البلد من tvg-country
            country_match = re.search(r'tvg-country="([^"]*)"', line)
            country = country_match.group(1) if country_match else ""

            # إذا لم يوجد، افحص group-title
            if not country:
                group_match = re.search(r'group-title="([^"]*)"', line)
                group = group_match.group(1) if group_match else ""
                group_lower = group.lower()

                if any(kw in group_lower for kw in ["السعودية", "saudi", "ksa"]):
                    country = "السعودية"
                elif any(kw in group_lower for kw in ["مصر", "egypt", "egy"]):
                    country = "مصر"
                elif any(kw in group_lower for kw in ["المغرب", "morocco", "mar"]):
                    country = "المغرب"
                elif any(kw in group_lower for kw in ["الجزائر", "algeria", "dza"]):
                    country = "الجزائر"
                elif any(kw in group_lower for kw in ["الإمارات", "emirates", "uae"]):
                    country = "الإمارات"
                # أضف المزيد حسب ملفك

            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url.startswith(('http', 'https')):
                    items.append({
                        "title": title,
                        "thumbnail": thumbnail,
                        "stream_url": url,
                        "is_public": True,
                        "is_active": True,
                        "country": country,
                        "description": "مصدر: ملف M3U"
                    })
                i += 1
        i += 1

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"✅ تم تحويل {len(items)} قناة إلى {output_path}")

if __name__ == "__main__":
    parse_m3u("samples/channels.m3u", "output/movies.json")