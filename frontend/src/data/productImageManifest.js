const DEFAULT_PRODUCT_IMAGE = {
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

const PRODUCT_IMAGE_ENTRIES = [
  {
    "productName": "大蒜",
    "displayName": "大蒜",
    "aliases": [
      "大蒜",
      "蒜头",
      "garlic"
    ],
    "src": "/images/products/garlic.jpg",
    "sourcePage": "https://www.pexels.com/photo/top-view-photo-of-garlic-bulbs-on-white-surface-4197447/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "大蒜图片"
  },
  {
    "productName": "大白菜",
    "displayName": "大白菜",
    "aliases": [
      "大白菜",
      "白菜",
      "cabbage"
    ],
    "src": "/images/products/napa-cabbage.jpg",
    "sourcePage": "https://www.pexels.com/photo/close-up-photo-of-brussels-sprouts-2893635/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "大白菜图片"
  },
  {
    "productName": "鸡蛋",
    "displayName": "鸡蛋",
    "aliases": [
      "鸡蛋",
      "蛋类",
      "egg"
    ],
    "src": "/images/products/egg.jpg",
    "sourcePage": "https://www.pexels.com/photo/brown-eggs-162712/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "鸡蛋图片"
  },
  {
    "productName": "富士苹果",
    "displayName": "苹果",
    "aliases": [
      "富士苹果",
      "苹果",
      "apple"
    ],
    "src": "/images/products/apple.jpg",
    "sourcePage": "https://www.pexels.com/photo/red-apples-102104/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "苹果图片"
  },
  {
    "productName": "西红柿",
    "displayName": "西红柿",
    "aliases": [
      "西红柿",
      "番茄",
      "tomato"
    ],
    "src": "/images/products/tomato.jpg",
    "sourcePage": "https://www.pexels.com/photo/close-up-photography-of-red-tomatoes-1327838/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "西红柿图片"
  },
  {
    "productName": "大豆",
    "displayName": "大豆",
    "aliases": [
      "大豆",
      "黄豆",
      "soybean"
    ],
    "src": "/images/products/soybean.jpg",
    "sourcePage": "https://www.pexels.com/photo/bowl-of-peanuts-on-brown-wooden-table-5966631/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "大豆图片"
  },
  {
    "productName": "玉米",
    "displayName": "玉米",
    "aliases": [
      "玉米",
      "苞米",
      "corn",
      "maize"
    ],
    "src": "/images/products/maize.jpg",
    "sourcePage": "https://www.pexels.com/photo/selective-focus-photography-of-corns-547263/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "玉米图片"
  },
  {
    "productName": "猪肉",
    "displayName": "猪肉",
    "aliases": [
      "猪肉",
      "生猪",
      "pork"
    ],
    "src": "/images/products/pork.jpg",
    "sourcePage": "https://www.pexels.com/photo/close-up-photograph-of-grilled-pork-1927377/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "猪肉图片"
  },
  {
    "productName": "生菜",
    "displayName": "生菜",
    "aliases": [
      "生菜",
      "lettuce"
    ],
    "src": "/images/products/lettuce.jpg",
    "sourcePage": "https://www.pexels.com/photo/green-cabbage-3757269/",
    "author": "See source page",
    "license": "Pexels License",
    "licenseUrl": "https://www.pexels.com/license/",
    "credit": "Pexels contributor",
    "attributionRequired": false,
    "alt": "生菜图片"
  }
];

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
