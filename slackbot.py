# -*- coding: utf-8 -*-
import re
import crawlAPI
import stock_RNN

from bs4 import BeautifulSoup

from flask import Flask
from slack import WebClient
from slack.web.classes.blocks import *
from slackeventsapi import SlackEventAdapter

SLACK_TOKEN = "xoxb-683354964401-691851652390-EOccutmwPJjdx8sX3d3JU7Yu"
SLACK_SIGNING_SECRET = "9f85bc48ba471139e4abd015c8cae890"

app = Flask(__name__)

# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)

_company_id = ''
_company_name = ''
_stock_price = 0

def _chatbot_main(textin):
    answer = ""
    textin = textin.replace("<@ULBR1K6BG> ", "")

    # 챗봇 시작
    if textin == "개미야!":
        answer = "안녕하세요! 주식 정보를 알려주는 '개미의 꿈'입니다! \n어떤 회사의 정보를 원하시나요?"
    


    # 종가예측
    # elif textin[-4:] == "종가예측":
    #     inputdata = textin.split()
    #     cname = inputdata[0]
    #     cid = crawlAPI.get_company_id_with_name(cname)
    #     print("=================================================")
    #     print(cid)
    #     print(cname)
    #     predict = str(stock_RNN.pridict_stock_price(cid))
    #     # answer = "RNN의 LSTM 모델로 예측 결과 " + cname +"의 내일 종가는 " + predict + "원이 될 예정입니다."
    #     answer = "\n 빨리 파세요!/사세요!"
    #     imgurl = "./img/predict/" + cid + ".png"
    #     block1 = SectionBlock(
    #         text = answer
    #     )
    #     block2 = ImageBlock(
    #         image_url = imgurl,
    #         alt_text="~그래프를 보여드리고 싶은데 알 수 없는 오류가 발생했어요....~"
    #     )
    #     my_blocks = [block1, block2]
    #     return my_blocks



    # 동종업종
    elif textin[-4:] == "동종업종":
        inputdata = textin.split()
        cname = inputdata[0]
        cid = crawlAPI.get_company_id_with_name(cname)
        
        my_blocks = []
        company_id_list = crawlAPI.get_similar_company_id(cid)
        company_name_list = []
        for company in company_id_list:
            nm = crawlAPI.get_company_name_with_id(company)
            print("======================================")
            print(company_id_list)
            print(nm)
            company_name_list.append(nm)
        index = 0
        for company_id in company_id_list:
            data = crawlAPI.crawl_stock_with_id(company_id)
            crawlAPI.list_to_csv(data, company_id)

            answer = str(index+1) + '. 동종업종 중 [' + company_name_list[index] + ', ' + company_id + ']' + "의 현재 주식 현황은 다음과 같습니다.\n"
            answer += "시가 : "
            answer += "{:,}".format(data[0][1])
            answer += "\t\t고가 : "
            answer += "{:,}".format(data[0][2])
            answer += "\t저가 : "
            answer += "{:,}".format(data[0][3])
            answer += "\n거래량 : "
            answer += "{:,}".format(data[0][4])
            answer += "\t종가 : "
            answer += "{:,}".format(data[0][5])
            answer += "\t전일비 : "
            answer += "{:,}".format(data[0][6])
            
            block1 = SectionBlock(
                text = answer
            )
            block2 = ImageBlock(
                image_url = crawlAPI.get_chart_with_id(company_id),
                alt_text="~그래프를 보여드리고 싶은데 알 수 없는 오류가 발생했어요....~"
            )

            my_blocks.append(block1)
            my_blocks.append(block2)
            index += 1


        return my_blocks


    
    # 회사명으로 주가정보 출력
    else:
        cid = crawlAPI.get_company_id_with_name(textin)
        _company_name = textin
        _company_id = cid
        if cid:
            data = crawlAPI.crawl_stock_with_id(cid)
            crawlAPI.list_to_csv(data, cid)

            answer = '[' + textin + ', ' + cid + ']' + "의 현재 주식 현황은 다음과 같습니다.\n"
            answer += "시가 : "
            answer += "{:,}".format(data[0][1])
            answer += "\t\t고가 : "
            answer += "{:,}".format(data[0][2])
            answer += "\t저가 : "
            answer += "{:,}".format(data[0][3])
            answer += "\n거래량 : "
            answer += "{:,}".format(data[0][4])
            answer += "\t종가 : "
            answer += "{:,}".format(data[0][5])
            answer += "\t전일비 : "
            answer += "{:,}".format(data[0][6])
            
            block1 = SectionBlock(
                text = answer
            )
            block2 = ImageBlock(
                image_url = crawlAPI.get_chart_with_id(cid),
                alt_text="~그래프를 보여드리고 싶은데 알 수 없는 오류가 발생했어요....~"
            )
            block3 = SectionBlock(
                text = textin + "의 현황 외에도 다양한 정보를 알 수 있어요!\n 1. 동종업종 추천 회사의 정보를 보고 싶다면 *"
                    + textin + " 동종업종*을, \n 2. 내일 " 
                    + textin + "의 종가를 저, 개미의 꿈으로 엿보고 싶다면 *"
                    + textin + " 종가예측*을 입력해 주세요!"
            )
            my_blocks = [block1, block2, block3]
            
            return my_blocks

        else:
            answer = text + "가 무슨 말씀인지 모르겠어요... 알아듣기 쉽게 말씀해주시면 좋겠어요..."
            return answer
        

    return answer



# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]

    # 답변 
    keywords = _chatbot_main(text)
    print(keywords)
    
    if(isinstance(keywords, str)):
        slack_web_client.chat_postMessage(
            channel=channel,
            text=keywords
        )
    else:
        slack_web_client.chat_postMessage(
            channel=channel,
            blocks=extract_json(keywords)
        )


# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    
    return "<h1>Server is ready.</h1>"