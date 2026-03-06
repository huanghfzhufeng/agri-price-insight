from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
ROOT_DIR = Path(__file__).resolve().parents[2]
IMAGE_DIR = ROOT_DIR / "frontend" / "public" / "images" / "products"
MANIFEST_PATH = ROOT_DIR / "frontend" / "src" / "data" / "productImageManifest.js"
PEXELS_LICENSE_URL = "https://www.pexels.com/license/"

PRODUCT_IMAGE_SPECS = [
    {
        "product_name": "大蒜",
        "display_name": "大蒜",
        "aliases": ["大蒜", "蒜头", "garlic"],
        "file_name": "garlic.jpg",
        "image_url": "https://images.pexels.com/photos/4197447/pexels-photo-4197447.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/top-view-photo-of-garlic-bulbs-on-white-surface-4197447/",
    },
    {
        "product_name": "大白菜",
        "display_name": "大白菜",
        "aliases": ["大白菜", "白菜", "cabbage"],
        "file_name": "napa-cabbage.jpg",
        "image_url": "https://images.pexels.com/photos/2893635/pexels-photo-2893635.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/close-up-photo-of-brussels-sprouts-2893635/",
    },
    {
        "product_name": "鸡蛋",
        "display_name": "鸡蛋",
        "aliases": ["鸡蛋", "蛋类", "egg"],
        "file_name": "egg.jpg",
        "image_url": "https://images.pexels.com/photos/162712/egg-white-food-protein-162712.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/brown-eggs-162712/",
    },
    {
        "product_name": "富士苹果",
        "display_name": "苹果",
        "aliases": ["富士苹果", "苹果", "apple"],
        "file_name": "apple.jpg",
        "image_url": "https://images.pexels.com/photos/102104/pexels-photo-102104.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/red-apples-102104/",
    },
    {
        "product_name": "西红柿",
        "display_name": "西红柿",
        "aliases": ["西红柿", "番茄", "tomato"],
        "file_name": "tomato.jpg",
        "image_url": "https://images.pexels.com/photos/1327838/pexels-photo-1327838.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/close-up-photography-of-red-tomatoes-1327838/",
    },
    {
        "product_name": "大豆",
        "display_name": "大豆",
        "aliases": ["大豆", "黄豆", "soybean"],
        "file_name": "soybean.jpg",
        "image_url": "https://images.pexels.com/photos/5966631/pexels-photo-5966631.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/bowl-of-peanuts-on-brown-wooden-table-5966631/",
    },
    {
        "product_name": "玉米",
        "display_name": "玉米",
        "aliases": ["玉米", "苞米", "corn", "maize"],
        "file_name": "maize.jpg",
        "image_url": "https://images.pexels.com/photos/547263/pexels-photo-547263.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/selective-focus-photography-of-corns-547263/",
    },
    {
        "product_name": "猪肉",
        "display_name": "猪肉",
        "aliases": ["猪肉", "生猪", "pork"],
        "file_name": "pork.jpg",
        "image_url": "https://images.pexels.com/photos/1927377/pexels-photo-1927377.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/close-up-photograph-of-grilled-pork-1927377/",
    },
    {
        "product_name": "生菜",
        "display_name": "生菜",
        "aliases": ["生菜", "lettuce"],
        "file_name": "lettuce.jpg",
        "image_url": "https://images.pexels.com/photos/3757269/pexels-photo-3757269.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=200&w=280",
        "source_page": "https://www.pexels.com/photo/green-cabbage-3757269/",
    },
]


def download_image(url: str, destination: Path) -> None:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    destination.write_bytes(response.content)


def build_manifest_entry(spec: dict) -> dict:
    return {
        "productName": spec["product_name"],
        "displayName": spec["display_name"],
        "aliases": spec["aliases"],
        "src": f"/images/products/{spec['file_name']}",
        "sourcePage": spec["source_page"],
        "author": "See source page",
        "license": "Pexels License",
        "licenseUrl": PEXELS_LICENSE_URL,
        "credit": "Pexels contributor",
        "attributionRequired": False,
        "alt": f"{spec['display_name']}图片",
    }


def write_manifest(entries: list[dict]) -> None:
    content = """const DEFAULT_PRODUCT_IMAGE = {
  productName: "默认图片",
  displayName: "默认图片",
  aliases: [],
  src: "/images/products/default-product.svg",
  sourcePage: "",
  author: "",
  license: "",
  licenseUrl: "",
  credit: "",
  attributionRequired: false,
  alt: "农产品默认占位图",
};

const PRODUCT_IMAGE_ENTRIES = __ENTRIES__;

const aliasMap = new Map();
for (const entry of PRODUCT_IMAGE_ENTRIES) {
  aliasMap.set(entry.productName, entry);
  for (const alias of entry.aliases) {
    aliasMap.set(alias, entry);
  }
}

export function resolveProductImage(productName) {
  if (!productName) {
    return DEFAULT_PRODUCT_IMAGE;
  }
  return aliasMap.get(productName) || DEFAULT_PRODUCT_IMAGE;
}

export { DEFAULT_PRODUCT_IMAGE, PRODUCT_IMAGE_ENTRIES };
"""
    MANIFEST_PATH.write_text(
        content.replace("__ENTRIES__", json.dumps(entries, ensure_ascii=False, indent=2)),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="下载农产品展示图片并生成前端图片清单。")
    parser.parse_args()

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for spec in PRODUCT_IMAGE_SPECS:
        download_image(spec["image_url"], IMAGE_DIR / spec["file_name"])
        entries.append(build_manifest_entry(spec))

    write_manifest(entries)
    print(f"downloaded_images={len(entries)} manifest={MANIFEST_PATH}")


if __name__ == "__main__":
    main()
