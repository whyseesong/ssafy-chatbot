# -*- coding: utf-8 -*-
import slackbot
# import crawlAPI


if __name__ == '__main__':
    slackbot.app.run('127.0.0.1', port=5000)

    # crawl_stock.get_company_id_with_name("삼성")

    # crawl_stock.crawl_stock_with_id("005930")
    # crawl_stock.list_to_csv(crawl_stock.crawl_stock_with_id("005930"), "005930")
    # crawl_stock.get_chart_with_id("005930")
    # crawl_stock.get_similar_company_id("005930")
    # crawlAPI.get_company_name_with_id("000660")