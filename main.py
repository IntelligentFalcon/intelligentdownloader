import os
import zipfile

import requests

assets_url = "https://resources.download.minecraft.net/"
version_manifest = "https://launchermeta.mojang.com/mc/game/version_manifest.json"


import argparse
import os

def parse_path(url):
    url_sp = url[url.find("://") + 3:]
    return url_sp[url_sp.find("/") + 1:]




manifest = requests.get(version_manifest).json()
paths = []


def zip_files(name, paths):
    with zipfile.ZipFile(name, "w") as z:
        for p in paths:
            z.write(p)


def download(url, path):
    print(f"Downloading {url}...")
    paths.append(path)
    if os.path.exists(path): return
    resp = requests.get(url)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w+") as f:
        f.write(resp.text)
    print(f"Saved to {path}.")


def download_assets(j):
    for k, v in j["objects"].items():
        hash = v["hash"]
        id = hash[:2]
        url = f"{assets_url}{id}/{hash}"
        path = f"resources/{id}/{hash}"
        download(url, path)


def scan_download_url(j):
    if type(j) == dict:
        keys = j.keys()
        for k in keys:
            if type(j[k]) == dict or type(j[k]) == list:
                scan_download_url(j[k])
            else:
                if k == "url":
                    url = j[k]
                    path = parse_path(url)
                    download(url, path)
                elif k == "path" and "url" not in keys:
                    urls = [
                        "https://libraries.minecraft.net/",
                        "https://maven.minecraftforge.net/",
                        "https://repo.spongepowered.org/maven/",
                    ]
                    for url in urls:
                        if requests.get(url).status_code == 200:
                            download(url, j[k])
    elif type(j) == list:
        for item in j:
            if type(item) == dict or type(item) == list:
                scan_download_url(item)


def download_version(version):
    print("Downloading version", version)
    versions: list = manifest["versions"]
    for v in versions:
        if v["id"] == version:
            version = v
    version_url = version["url"]
    version_resp = requests.get(version_url)
    version = version_resp.json()
    version_path = os.path.dirname(parse_path(version_url))
    os.makedirs(version_path, exist_ok=True)
    with open(parse_path(version_url), "w+") as f:
        f.write(version_resp.text)
        paths.append(parse_path(version_url))

    paths.append(parse_path(version_url))
    scan_download_url(version)
    assets_file = requests.get(version["assetIndex"]["url"])
    with open(parse_path(version["assetIndex"]["url"]), "w+") as f:
        f.write(assets_file.text)
    download_assets(assets_file.json())

parser = argparse.ArgumentParser()
parser.add_argument('--version', required=True, help='Version number')
args = parser.parse_args()
version = args.version
download_version(version)

print("Done!")
