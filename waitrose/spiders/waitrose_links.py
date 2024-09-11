import os.path

import scrapy
from unidecode import unidecode
from scrapy.cmdline import execute
import json
import pymysql
import waitrose.db_config as db
from waitrose.items import WaitroselinkItems


class WaitroseLinksSpider(scrapy.Spider):
    name = "waitrose_links"
    allowed_domains = ["www.waitrose.com"]
    # start_urls = ["https://www.waitrose.com"]
    start_urls = ["https://www.waitrose.com/api/graphql-prod/graph/live"]

    def __init__(self):
        super().__init__()
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password)
        self.cursor = self.con.cursor()
        self.PAGE_SAVE_PATH = f"/home/vrusahbh/PycharmProjects/pythonProject/scrapyprojects/waitrose"
        self.headers = {
        'authority': 'www.waitrose.com',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': 'Bearer unauthenticated',
        'breadcrumb': 'browse-fe',
        'content-type': 'application/json',
        # 'cookie': 'mt.v=2.193581503.1686935016989; wtr_cookie_consent=1; wtr_cookies_advertising=1; wtr_cookies_analytics=1; wtr_cookies_functional=1; IR_gbd=waitrose.com; _gcl_au=1.1.986493802.1686935020; _gid=GA1.2.957314991.1686935020; _cs_c=1; unbxd.userId=uid-1686935020423-8490; _fbp=fb.1.1686935020814.794166170; _pin_unauth=dWlkPU1UWTBOVEExTWpjdFl6Z3daaTAwTkRVM0xUZ3haRFF0T0RVM05qZG1Oell5Wmpjdw; eds=INS-vi42-303388996:265076283-1686935020^709016667-1686935020; BVImplecom=17263_2_0; BVBRANDID=8bd7c772-ce2b-490b-844d-281bbc0d2401; _hjSessionUser_1434770=eyJpZCI6IjBlNWRlODQzLWUzMDctNWM5Ni1hZjg2LTVmZmQ2NmVlNGMxOSIsImNyZWF0ZWQiOjE2ODY5MzUwMjA2MDEsImV4aXN0aW5nIjp0cnVlfQ==; _hjHasCachedUserAttributes=true; _abck=25D4399309397C4EF466DFF5BE409BB7~0~YAAQPHxBF5f1oKSIAQAAkffTyAr2OT5vt1a1Dx9+NXVJR/A71fm7/WybXgnR3tpAFlLu/krfc8tZM1yiuKYHbgU9sYXcd8CyOLkVHhoMFXd6Zq7+JJOfmGvDYrxswlNflg5RqAYP2wupLa9jCvJ9D96i7bBk3kTf3RLWM92E8IC/XJvM/G5DqIOW9yuZmC8R++xyyUJF3Ll1J/JAmD8/yCRMISNALLw2USowxHlC4KmtrqBMb/hQLDkP3f3UXxyBDisPaffG4xdzJUJFtbapp3HspDsiCVtFc69OddTPJecFPqLb5k8BFJprJnE4q6sN8B48cCdsOJRCmW6nf3OCcbbOzZgHBf9me5DbidCt38QaW1JL5J7vsZ0p8JVuA0+SFYSUQ0usggMCgmCO4Gq5MEQSyQ9rKURYlA==~-1~-1~-1; bm_sz=197E47AE04E14725EA59D80662F964CE~YAAQPHxBF5j1oKSIAQAAkffTyBS/XXxHATsoBrz3jShkFoZLcnwbATADHIbY2vcV9C31YLENFh9AwYQrbj/a20x17NljqkVO0g92ogWUEpDtiGmMOv9oDzIMIajCc4TFRSK2ucdGPAdiM5wsA25fzyk2yxJ2tJd++yRc9T9FxFL2klJzG/MPT7R+OGexAg7rZsVXi4vfUXifOlzt7pGoP4ROqpxunVcfQ4L81udglt3V9Pyab7RkQsOzNibb1yrUT5nCN8sef41lJYQYraJa30RLQ+56DZWDxYenh8q+01nCmhzcQQ==~3294772~3356466; mt.sc=%7B%22i%22%3A1686997686938%2C%22d%22%3A%5B%22cs%3Bdirect%22%5D%7D; website_csat_session=2023-06-17:7974296367; ak_bmsc=E41C5C15BC325180E5992875DE3BAED0~000000000000000000000000000000~YAAQPHxBF3JloqSIAQAAzdzlyBT1s1V4i5mkDJGZqf28THY5K1xiJefe7zT6D74aNVt5u879R45jvepOvEHvhjBN5yF9ldo+8mC5wnzb8ZENoggr6QOtQvaLxq/soEMsplH/EIPK8Ry2lqfFVHdJCSoByhpYMwsK6utUR5PbCH41OwtCZJebtyOMj7FnZe089jHq9IookZQ4p1TG8C2Q64TmHvY+aR7qfRKaCahb+L9gpoObzM18y2Sv0ajEm5thIKguPiC0g912bsAGG9lfW2h/gTO1Wj3m6baIqzA/zTRMcc2oS9krIoqCfmx/7wJAmSZg+LT/hnXqSCITYpHpTp/CyRNFDkGpiU14DWAgqe/YOsLCt4D3ImVy0bB3GfOiJgbDvkztYrmbju6i7Effr5IraWmjXydNtU87LXLt8DyUikHhMz0M6JFpNiQp9ww6/aOjEwIXr+KXUizNYjhMbh2fKbTRchKCBEwNHAhSi5+hcqG4a7LLuFvTvFATuA==; unbxd.visitId=visitId-1686997687780-64914; _cs_mk_ga=376840719_1686997688039; _hjSession_1434770=eyJpZCI6ImZhMWJlNDNhLWMxYzMtNDBkNC04OWEyLTQzOWUyOGJjNTJlZiIsImNyZWF0ZWQiOjE2ODY5OTc2ODgyMDQsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample_1434770=0; PIM-SESSION-ID=X9KfOwrPtAdPpOtm; unbxd.visit=repeat; IR_12163=1687001869110%7C0%7C1687001869110%7C%7C; _ga_5NQ8P4PPP7=GS1.1.1686997688.5.1.1687001870.0.0.0; _ga=GA1.2.2.193581503.1686935016989; _gat_UA-34398547-2=1; _ga_DZJD4TQPGV=GS1.1.1686997687.4.1.1687002571.0.0.0; ecos.dt=1687002575171; _ga_8YN3DG5SKT=GS1.1.1686997687.5.1.1687002575.53.0.0; _cs_id=1e335946-b3c1-a2df-c3ad-d38152ad83fa.1686935020.13.1687002575.1686999373.1.1721099020396; _cs_s=46.0.0.1687004375573; bm_sv=5CB2F9E14D58B14E83CB00F55D3D7D42~YAAQPHxBFxVGqKSIAQAAQ3QwyRQhqwj6iQKYwLVArKgQDwkXETUCJf5F769kJqtQxFioiUeBiY2AG4cWQN9w6lfUQSSj2pS9zIsNGWK2MpFksmgbzJOgyw6jaQz5m72PLTrzpN7LrRLSc4v/XcIqhT60D039slVbKs7HbJ55YetXtHD0oYSLA/MLoNIKJG3tgsNGm0pfnTtJPsnEGdIPRJGboeAIdQ8Xjtvixl0g9hm27jLMiHciEj5lzQLn3wZFspzsbw==~1',
        'features': 'samosa,enAppleWallet',
        'graphflags': '{}',
        'origin': 'https://www.waitrose.com',
        # 'referer': 'https://www.waitrose.com/ecom/shop/browse/groceries/beer_wine_and_spirits/spirits_and_liqueurs/vodka',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        # 'traceparent': '00-72f8eca0b7dc67cd23c3ea5243244527-bcfd639f7202db95-01',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    def start_requests(self):
        categoryIds = ["300506", "300508", "300509", "300510", "300511", "300512", "300513", "300514", "300516"]
        for category in categoryIds:
            start = 0
            json_data = json.dumps({
                'query': 'fragment ProductFragment on Product {\n  availableDays\n  barCodes\n  conflicts {\n    lineNumber\n    messages\n    nextSlotDate\n    outOfStock\n    priority\n    productId\n    prohibitedActions\n    resolutionActions\n    slotOptionDates {\n      type\n      date\n    }\n  }\n  containsAlcohol\n  lineNumber\n  images {\n    extraLarge\n    large\n    medium\n    small\n  }\n  id\n  productType\n  size\n  brand\n  thumbnail\n  name\n  leadTime\n  reviews {\n    averageRating\n    total\n  }\n  customerProductDetails {\n    customerFavourite\n    customerPyo\n  }\n  currentSaleUnitPrice {\n    quantity {\n      amount\n      uom\n    }\n    price {\n      amount\n      currencyCode\n    }\n  }\n  defaultQuantity {\n    amount\n    uom\n  }\n  depositCharge {\n    amount\n    currencyCode\n  }\n  pricing {\n    displayPrice\n    displayUOMPrice\n    displayPriceQualifier\n    displayPriceEstimated\n    currentSaleUnitRetailPrice {\n      price {\n        amount\n        currencyCode\n      }\n      quantity {\n        amount\n        uom\n      }\n    }\n    promotions {\n      groups {\n        threshold\n        name\n        lineNumbers\n      }\n      promotionDescription\n      promotionExpiryDate\n      promotionId\n      pyoPromotion\n      myWaitrosePromotion\n      wasDisplayPrice\n      promotionType\n    }\n  }\n  persistDefault\n  markedForDelete\n  substitutionsProhibited\n  displayPrice\n  displayPriceEstimated\n  displayPriceQualifier\n  leadTime\n  productShelfLife\n  maxPersonalisedMessageLength\n  summary\n  supplierOrder\n  restriction {\n    availableDates {\n      restrictionId\n      startDate\n      endDate\n      cutOffDate\n    }\n  }\n  weights {\n    pricePerUomQualifier\n    defaultQuantity {\n      amount\n      uom\n    }\n    servings {\n      min\n      max\n    }\n    sizeDescription\n    uoms\n    formattedWeightRange\n  }\n  categories {\n    id\n    name\n    urlName\n  }\n  productTags {\n    name\n  }\n  marketingBadges {\n    name\n  }\n}\nfragment ProductPod on Product {\n              brand,\n              categories {\n                  name,\n                  urlName,\n                  id\n              },\n              cqResponsive {\n                deviceBreakpoints {\n                  name\n                  visible\n                  width\n                }\n              },\n              currentSaleUnitPrice {\n                price {\n                  amount\n                  currencyCode\n                }\n                quantity {\n                  amount\n                  uom\n                }\n              },\n              customerProductDetails {\n                customerInTrolleyQuantity {\n                  amount\n                  uom\n                }\n                customerPyo\n              },\n              defaultQuantity {\n                  uom\n              },\n              depositCharge {\n                amount,\n                currencyCode\n              },\n              displayPrice,\n              displayPriceEstimated,\n              displayPriceQualifier,\n              id,\n              leadTime,\n              lineNumber\n              maxPersonalisedMessageLength,\n              name,\n              markedForDelete,\n              persistDefault,\n              productImageUrls {\n                  extraLarge,\n                  large,\n                  medium,\n                  small\n              }\n              productType,\n              promotion {\n                groups {\n                  threshold\n                  name\n                  lineNumbers\n                }\n                myWaitrosePromotion\n                promotionDescription\n                promotionId\n                promotionTypeCode\n                wasDisplayPrice\n              },\n              promotions {\n                groups {\n                  threshold\n                  name\n                  lineNumbers\n                }\n                myWaitrosePromotion\n                promotionDescription\n                promotionId\n                promotionTypeCode\n                wasDisplayPrice\n              },\n              restriction {\n                  availableDates {\n                      restrictionId,\n                      startDate,\n                      endDate,\n                      cutOffDate\n                  },\n              },\n              resultType,\n              reviews {\n                averageRating\n                reviewCount\n              },\n              size,\n              sponsored,\n              substitutionsProhibited,\n              thumbnail\n              typicalWeight {\n                amount\n                uom\n              }\n              weights {\n                  uoms ,\n                  pricePerUomQualifier,\n                  perUomQualifier,\n                  defaultQuantity {\n                      amount,\n                      uom\n                  },\n                  servings {\n                      max,\n                      min\n                  },\n                  sizeDescription\n              },\n              productTags {\n                name\n              },\n              marketingBadges {\n                name\n              },\n            }query(\n  $customerId: String!\n  $withRecommendations: Boolean!\n  $size: Int\n  $start: Int\n  $category: String\n  $filterTags: [filterTag]\n  $recommendationsSize: Int\n  $recommendationsStart: Int\n  $sortBy: String\n  $trolleyId: String\n  $withFallback: Boolean\n) {\n  getProductListPage(\n    category: $category\n    customerId: $customerId\n    filterTags: $filterTags\n    recommendationsSize: $recommendationsSize\n    recommendationsStart: $recommendationsStart\n    size: $size\n    start: $start\n    sortBy: $sortBy\n    trolleyId: $trolleyId\n    withFallback: $withFallback\n  ) {\n  productGridData {\n      failures{\n          field\n          message\n          type\n      }\n      componentsAndProducts {\n        __typename\n        ... on GridProduct {\n          searchProduct {\n            ...ProductPod\n          }\n        }\n        ... on GridCmsComponent {\n          aemComponent\n        }\n      }\n      conflicts {\n        messages\n        outOfStock\n        priority\n        productId\n        prohibitedActions\n        resolutionActions\n        nextSlotDate\n    }\n      criteria {\n        alternative\n        sortBy\n        filters {\n          group\n          filters {\n            applied\n            filterTag {\n              count\n              group\n              id\n              text\n              value\n            }\n          }\n        }\n        searchTags {\n          group\n          text\n          value\n        }\n        suggestedSearchTags {\n          group\n          text\n          value\n        }\n      }\n      locations {\n        header\n        masthead\n      }\n      metaData {\n        description\n        title\n        keywords\n        turnOffIndexing\n        pageTitle\n      }\n      productsInResultset\n      relevancyWeightings\n      searchTime\n      showPageTitle\n      totalMatches\n      totalTime\n    }\n    recommendedProducts @include(if: $withRecommendations) {\n      failures{\n        field\n        message\n        type\n      }\n      fallbackRecommendations\n      products {\n        ...ProductFragment\n        metadata {\n          recToken\n          monetateId\n        }\n      }\n      totalResults\n    }\n  }\n}\n',
                'variables': {
                    'start': start,
                    'size': 100,
                    'sortBy': 'MOST_POPULAR',
                    'trolleyId': '0',
                    'recommendationsSize': 0,
                    'withRecommendations': False,
                    'withFallback': True,
                    'category': category,
                    'customerId': '-1',
                    # 'filterTags': [],
                },
            })

            yield scrapy.Request(url=self.start_urls[0], headers=self.headers, method="POST", body=json_data,
                                     callback=self.parse, meta={"start": start, "category": category})

    def parse(self, response):
        start = response.meta["start"] + 100
        category = response.meta["category"]
        all_data = json.loads(response.text)
        all_listing = all_data["data"]["getProductListPage"]["productGridData"]["componentsAndProducts"]
        if all_listing:
            for a in all_listing:
                item = WaitroselinkItem()
                try:
                    searchId = a["searchProduct"]["id"]
                except:
                    searchId = ""

                if not searchId:
                    continue
                filepath = self.PAGE_SAVE_PATH + f'/link_pages'
                if not os.path.exists(filepath):
                    os.mkdir(filepath)
                with open(filepath + f'/{searchId.replace("-", "_")}.txt', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                    f.close()

                try:
                    name = a["searchProduct"]["name"].replace(" ", "-").replace("'", "").lower().strip()
                except:
                    name = ""

                url = f"https://www.waitrose.com/ecom/products/{name}/{searchId}"

                item["Product_URL"] = unidecode(url)
                item["Category_Id"] = category
                item["Status"] = 'Pending'

                print(item)
                yield item

            json_data = json.dumps({
                'query': 'fragment ProductFragment on Product {\n  availableDays\n  barCodes\n  conflicts {\n    lineNumber\n    messages\n    nextSlotDate\n    outOfStock\n    priority\n    productId\n    prohibitedActions\n    resolutionActions\n    slotOptionDates {\n      type\n      date\n    }\n  }\n  containsAlcohol\n  lineNumber\n  images {\n    extraLarge\n    large\n    medium\n    small\n  }\n  id\n  productType\n  size\n  brand\n  thumbnail\n  name\n  leadTime\n  reviews {\n    averageRating\n    total\n  }\n  customerProductDetails {\n    customerFavourite\n    customerPyo\n  }\n  currentSaleUnitPrice {\n    quantity {\n      amount\n      uom\n    }\n    price {\n      amount\n      currencyCode\n    }\n  }\n  defaultQuantity {\n    amount\n    uom\n  }\n  depositCharge {\n    amount\n    currencyCode\n  }\n  pricing {\n    displayPrice\n    displayUOMPrice\n    displayPriceQualifier\n    displayPriceEstimated\n    currentSaleUnitRetailPrice {\n      price {\n        amount\n        currencyCode\n      }\n      quantity {\n        amount\n        uom\n      }\n    }\n    promotions {\n      groups {\n        threshold\n        name\n        lineNumbers\n      }\n      promotionDescription\n      promotionExpiryDate\n      promotionId\n      pyoPromotion\n      myWaitrosePromotion\n      wasDisplayPrice\n      promotionType\n    }\n  }\n  persistDefault\n  markedForDelete\n  substitutionsProhibited\n  displayPrice\n  displayPriceEstimated\n  displayPriceQualifier\n  leadTime\n  productShelfLife\n  maxPersonalisedMessageLength\n  summary\n  supplierOrder\n  restriction {\n    availableDates {\n      restrictionId\n      startDate\n      endDate\n      cutOffDate\n    }\n  }\n  weights {\n    pricePerUomQualifier\n    defaultQuantity {\n      amount\n      uom\n    }\n    servings {\n      min\n      max\n    }\n    sizeDescription\n    uoms\n    formattedWeightRange\n  }\n  categories {\n    id\n    name\n    urlName\n  }\n  productTags {\n    name\n  }\n  marketingBadges {\n    name\n  }\n}\nfragment ProductPod on Product {\n              brand,\n              categories {\n                  name,\n                  urlName,\n                  id\n              },\n              cqResponsive {\n                deviceBreakpoints {\n                  name\n                  visible\n                  width\n                }\n              },\n              currentSaleUnitPrice {\n                price {\n                  amount\n                  currencyCode\n                }\n                quantity {\n                  amount\n                  uom\n                }\n              },\n              customerProductDetails {\n                customerInTrolleyQuantity {\n                  amount\n                  uom\n                }\n                customerPyo\n              },\n              defaultQuantity {\n                  uom\n              },\n              depositCharge {\n                amount,\n                currencyCode\n              },\n              displayPrice,\n              displayPriceEstimated,\n              displayPriceQualifier,\n              id,\n              leadTime,\n              lineNumber\n              maxPersonalisedMessageLength,\n              name,\n              markedForDelete,\n              persistDefault,\n              productImageUrls {\n                  extraLarge,\n                  large,\n                  medium,\n                  small\n              }\n              productType,\n              promotion {\n                groups {\n                  threshold\n                  name\n                  lineNumbers\n                }\n                myWaitrosePromotion\n                promotionDescription\n                promotionId\n                promotionTypeCode\n                wasDisplayPrice\n              },\n              promotions {\n                groups {\n                  threshold\n                  name\n                  lineNumbers\n                }\n                myWaitrosePromotion\n                promotionDescription\n                promotionId\n                promotionTypeCode\n                wasDisplayPrice\n              },\n              restriction {\n                  availableDates {\n                      restrictionId,\n                      startDate,\n                      endDate,\n                      cutOffDate\n                  },\n              },\n              resultType,\n              reviews {\n                averageRating\n                reviewCount\n              },\n              size,\n              sponsored,\n              substitutionsProhibited,\n              thumbnail\n              typicalWeight {\n                amount\n                uom\n              }\n              weights {\n                  uoms ,\n                  pricePerUomQualifier,\n                  perUomQualifier,\n                  defaultQuantity {\n                      amount,\n                      uom\n                  },\n                  servings {\n                      max,\n                      min\n                  },\n                  sizeDescription\n              },\n              productTags {\n                name\n              },\n              marketingBadges {\n                name\n              },\n            }query(\n  $customerId: String!\n  $withRecommendations: Boolean!\n  $size: Int\n  $start: Int\n  $category: String\n  $filterTags: [filterTag]\n  $recommendationsSize: Int\n  $recommendationsStart: Int\n  $sortBy: String\n  $trolleyId: String\n  $withFallback: Boolean\n) {\n  getProductListPage(\n    category: $category\n    customerId: $customerId\n    filterTags: $filterTags\n    recommendationsSize: $recommendationsSize\n    recommendationsStart: $recommendationsStart\n    size: $size\n    start: $start\n    sortBy: $sortBy\n    trolleyId: $trolleyId\n    withFallback: $withFallback\n  ) {\n  productGridData {\n      failures{\n          field\n          message\n          type\n      }\n      componentsAndProducts {\n        __typename\n        ... on GridProduct {\n          searchProduct {\n            ...ProductPod\n          }\n        }\n        ... on GridCmsComponent {\n          aemComponent\n        }\n      }\n      conflicts {\n        messages\n        outOfStock\n        priority\n        productId\n        prohibitedActions\n        resolutionActions\n        nextSlotDate\n    }\n      criteria {\n        alternative\n        sortBy\n        filters {\n          group\n          filters {\n            applied\n            filterTag {\n              count\n              group\n              id\n              text\n              value\n            }\n          }\n        }\n        searchTags {\n          group\n          text\n          value\n        }\n        suggestedSearchTags {\n          group\n          text\n          value\n        }\n      }\n      locations {\n        header\n        masthead\n      }\n      metaData {\n        description\n        title\n        keywords\n        turnOffIndexing\n        pageTitle\n      }\n      productsInResultset\n      relevancyWeightings\n      searchTime\n      showPageTitle\n      totalMatches\n      totalTime\n    }\n    recommendedProducts @include(if: $withRecommendations) {\n      failures{\n        field\n        message\n        type\n      }\n      fallbackRecommendations\n      products {\n        ...ProductFragment\n        metadata {\n          recToken\n          monetateId\n        }\n      }\n      totalResults\n    }\n  }\n}\n',
                'variables': {
                    'start': start,
                    'size': 100,
                    'sortBy': 'MOST_POPULAR',
                    'trolleyId': '0',
                    'recommendationsSize': 0,
                    'withRecommendations': False,
                    'withFallback': True,
                    'category': category,
                    'customerId': '-1',
                    # 'filterTags': [],
                },
            })
            yield scrapy.Request(url=self.start_urls[0], headers=self.headers, method="POST", body=json_data,
                             callback=self.parse, meta={"start": start, "category": category})


# execute("scrapy crawl waitrose_links".split())
