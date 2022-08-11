from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import requests
import re
import pandas as pd
import numpy as np
import os
import imp
import time
import pandas as pd
from googleapiclient.discovery import build
import os
import re
import streamlit as st
import pafy as pa
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from konlpy.tag import Okt
from tqdm import tqdm
from keras.preprocessing.text import Tokenizer
# from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.utils import pad_sequences
from keras.models import load_model
import pickle
import socket
import sqlite3
from selenium.webdriver.common.keys import Keys
import warnings
warnings.filterwarnings('ignore')
############################################################CSS 전용
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
import requests
import math

okt = Okt()

def title_get():
    title_url = url
    response = requests.get(title_url)
    soup = BeautifulSoup(response.text,"html.parser")
    
    title = soup.find('body').find('div', {'class':'top_summary_title__15yAr'})
    
    title_list=[]
    for tag in title:
        title_list.append(tag.text)
    
    shop_title = title_list[0]

    return shop_title

#평점 가져오기
def grade_get():
    title_url = url
    response = requests.get(title_url)
    soup = BeautifulSoup(response.text,"html.parser")
    
    grade = soup.find('body').find('div', {'class':'top_grade__3jjdl'})

    grade_list=[]
    for grade_tag in grade:
        grade_list.append(grade_tag.text)
    
    shop_grade = grade_list[1]

    return shop_grade

def Shopping():
    for a in range(4,7):
        try:
            #1. 웹사이트 불러오기
            #크롤링할 웹사이트 주소
            ns_address = url

            #크롤링한 모든리뷰 저장
            all_shoppingmall_review = "/html/body/div/div/div[2]/div[2]/div[2]/div[3]/div[%s]" % a
            shoppingmall_review="%s/ul" %all_shoppingmall_review

            #2. 쇼핑몰 리뷰 가져오기
            # header = {'User-Agent': ''}
            d = webdriver.Chrome('chromedriver.exe') # webdriver = chrome
            d.implicitly_wait(1)
            d.get(ns_address)
            req = requests.get(ns_address,verify=False) # verify = False 는 HTTPS 요청에 대한 SSL 인증서 확인 과정을 생략하겠다는 의미입니다.
            html = req.text 
            BeautifulSoup(html, "html.parser")
            sleep(0.2)

            #쇼핑몰 리뷰 보기
            d.find_element_by_xpath(shoppingmall_review).click()
            sleep(0.2)

            element = d.find_element_by_xpath(shoppingmall_review)
            d.execute_script("arguments[0].click();", element) 
            sleep(0.2)

            #3. 데이터 프레임 만들기
            def add_dataframe(reviews,stars,cnt):  #데이터 프레임에 저장
                #데이터 프레임생성
                df1=pd.DataFrame(columns=['comment','star'])
                n=1
                if (cnt>0):
                    for i in range(0,cnt-1):
                        df1.loc[n]=[reviews[i],stars[i]] #해당 행에 저장
                        i+=1
                        n+=1
                else:
                    df1.loc[n]=['null','null']
                    n+=1    
                return df1

            #5. 리뷰 가져오기
            d.find_element_by_xpath(shoppingmall_review).click() #스크롤 건드리면 안됨
            reviews=[]
            stars=[]
            cnt=1   #리뷰index
            page=1
            #중복변수 설정
            b = 30
            c = 21

            #6. 리뷰 수집하기
            while True:
                j=1
                print ("페이지", page ,"\n") 
                sleep(0.2)
                while True: #한페이지에 20개의 리뷰, 마지막 리뷰에서 error발생
                    try:
                        star=d.find_element_by_xpath('%s/ul/li[1]/div[1]/span[1]' %all_shoppingmall_review).text
                        stars.append(star)
                        review=d.find_element_by_xpath(all_shoppingmall_review + '/ul/li['+str(j)+']/div[2]/div[1]').text
                        reviews.append(review)
                        if j%2==0: #화면에 2개씩 보이도록 스크롤
                            ELEMENT = d.find_element_by_xpath(all_shoppingmall_review + '/ul/li['+str(j)+']/div[2]/div[1]')
                            d.execute_script("arguments[0].scrollIntoView(true);", ELEMENT)       
                        j+=1
                        print(cnt, review ,star, "\n")
                        cnt+=1 
                    except: break

                sleep(0.2)

                if page<10:#page10
                    try: #리뷰의 마지막 페이지에서 error발생
                        page +=1
                        d.find_element_by_xpath(all_shoppingmall_review + '/div[3]/a['+str(page)+']').click() 
    
                    except: break #리뷰의 마지막 페이지에서 process 종료

                elif 9<page<20: 
                    try: #page11부터
                        page +=1 
                        if page == 11: 
                            d.find_element_by_xpath(all_shoppingmall_review + '/div[3]/a['+str(page)+']').click() 
                        elif 11<page<20 : 
                            d.find_element_by_xpath(all_shoppingmall_review + '/div[3]/a['+str(page%10+1)+']').click()
                        elif page ==20 :
                            d.find_element_by_xpath(all_shoppingmall_review + '/div[3]/a['+str(11)+']').click()

                    except: break

                else:
                    try:
                        page +=1
                        if page == c :
                            d.find_element_by_xpath(all_shoppingmall_review + '/div[3]/a['+str(12)+']').click()
                        elif c < page < b :
                            d.find_element_by_xpath(all_shoppingmall_review + '/div[3]/a['+str(page%(b-10)+1)+']').click()
                        elif page == b :
                            d.find_element_by_xpath(all_shoppingmall_review + '/div[3]/a['+str(11)+']').click()
                            b+=10
                            c+=10

                    except: break

            df = add_dataframe(reviews,stars,cnt)
            df = df.astype(str)
            df.to_excel('./shop_xlsx/%s.xlsx' % title_get(), header=['comment', 'score'], index=None)
            path = './shop_xlsx/%s.xlsx' % (title_get())
            while os.path.exists(path) :
                df.to_excel('./shop_xlsx/%s.xlsx' % title_get(), header=['comment', 'score'], index=None)
                break
        except:
            print("다시.")



contain = []            #긍정 cell
contain_number =[]      #긍정 확률
contain2 = []           #부정 cell
contain2_number = []    #부정 확률
contain3 = []           
contain3_number = []
star_score = []

#감정분석
def Analysis():
    tokenizer = Tokenizer()
    okt = Okt()
    max_len = 30

    # 불용어
    stopwords = ['은','는','이','가','하','아','것','들','의','있','되','수','보','주','등','한','줄','를','을','에','에게','께','한테','더러','에서','에게서','한테서','로','으로','와','과','도','부터','도','만','이나','나','라도','의'
                 , '거의', '겨우', '결국', '그런데', '즉', '참', '챗', '할때', '할뿐', '함께', '해야한다', '휴']
    
    PATH = './model_test/'
    
    #모델 및 토큰 불러오기
    model = load_model(PATH + 'best_model.h5')
    with open(PATH+'tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)


    # 감정 예측
    def sentiment_predict(new_sentence):
        new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', str(new_sentence))
        new_sentence = okt.morphs(new_sentence, stem=True) # 토큰화
        new_sentence = [word for word in new_sentence if not word in stopwords] # 불용어 제거
        encoded = tokenizer.texts_to_sequences([new_sentence]) # 정수 인코딩
        pad_new = pad_sequences(encoded, maxlen = max_len) # 패딩
        score = float(model.predict(pad_new)) # 예측
        
        # 긍정적이라면 contain 리스트에 추가. 이후 조건문에 star_score 리스트에 별점을 추가
        if(score > 0.65):
            contain.append(list)
            contain_number.append(score * 5)
            star_score.append(round(score * 5))
        # 중립이라면 contain3 리스트에 추가
        elif 0.5 < score < 0.65:
            contain3.append(list)
            contain3_number.append(score * 5)
            star_score.append(score * 5)
        # 부정적이라면 contain2 리스트에 추가
        else:
            contain2.append(list)
            contain2_number.append(score * 5)
            star_score.append(score * 5)



    # # 다른 함수에서도 쓰기 위해 global(전역변수) 선언
    global sheet
    filename = pd.read_excel('./shop_xlsx/%s.xlsx' % title_get())
    sheet = filename['comment']


    # comment 칼럼의 각각의 데이터를 읽기
    for cell in sheet:
        list = []
        output_sentence = str(cell)
        
        split = re.sub('(<([^>]+)>)','', output_sentence)
        list.append(split)

        # 감정 예측
        sentiment_predict(list)


def Create_plot():
  global allen, poslen, neglen, neulen
  allen = len(sheet)
  poslen = len(pd_contain)
  neglen = len(pd_contain2)
  neulen = len(pd_contain3)
  
  pos_ratio = (poslen/allen) * 100
  neg_ratio = (neglen/allen) * 100
  neu_ratio = (neulen/allen) * 100
  
  labels = ['Positive', 'Negative', 'Neutral']
  ratio = pos_ratio, neg_ratio, neu_ratio
  
  fig, ax = plt.subplots()
  ax.pie(ratio, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
  ax.axis('equal')
  plt.savefig('./result_image/%s_chart.png' % title_get())
  
  st.pyplot(fig)


def Create_pword():
    # 리스트를 문자열 형태로 변환
    # 1. '(요소 사이에 넣을 문자)'.join(str(변수) for 변수 in 리스트)
    # 2. 리스트 내의 요소를 변수에 대입하고 변수를 str(문자열) 형태로 변환 
    pos = ''.join([str(n) for n in contain])
    
    # 190줄을 풀어서 설명한 코드
    # pos = list_to_str(contain)
    
    # 데이터 전처리
    pn = okt.nouns(pos)
    # 문장의 길이가 1은 제외
    pw = [n for n in pn if len(n) > 1] 
    
    pc = Counter(pw)
    pwc = WordCloud(font_path='malgun', width=400, height=400, scale=2.0, max_font_size=250, background_color='white')
    
    pg = pwc.generate_from_frequencies(pc)
    pfig = plt.figure()
    
    plt.imshow(pg, interpolation='bilinear')
    plt.axis('off')
    plt.show()

    st.success('긍정')
    st.pyplot(pfig)
    
# 부정 워드 클라우드
def Create_nword():
    neg = ''.join([str(n) for n in contain2])
    # neg = list_to_str(contain2)
    
    nn = okt.nouns(neg)
    nw = [n for n in nn if len(n) > 1]
    nc = Counter(nw)
    nwc = WordCloud(font_path='malgun', width=400, height=400, scale=2.0, max_font_size=250, background_color='white')
    
    ng = nwc.generate_from_frequencies(nc)
    nfig = plt.figure()
    
    plt.imshow(ng, interpolation='bilinear')
    plt.axis('off')
    plt.show()
    
    st.error('부정')
    st.pyplot(nfig)

# 중립 워드 클라우드
def Create_aword():
    neu = ''.join([str(n) for n in contain3])
    
    ne = okt.nouns(neu)
    nw = [n for n in ne if len(n) > 1]
    nc = Counter(nw)
    nwc = WordCloud(font_path='malgun', width=400, height=400, scale=2.0, max_font_size=250, background_color='white')
    
    ng = nwc.generate_from_frequencies(nc)
    nfig = plt.figure()
    
    plt.imshow(ng, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('./result_wc/%s_neutral.png' % title_get())
    plt.show()
    
    st.warning("중립")
    st.pyplot(nfig)   

# 실제 평점
def Real_grade():
    star_grade = int(float(grade_get()))
    
    if star_grade == 5:
        streamlit_5star()
        st.info("실제 평점 : %s" % grade_get())
        
    elif 4 <= star_grade < 5:
        streamlit_4star()
        st.info("실제 평점 : %s" % grade_get())
        
    elif 3 <= star_grade < 4:
        streamlit_3star()
        st.info("실제 평점 : %s" % grade_get())
        
    elif 2 <= star_grade < 3:
        streamlit_2star()
        st.info("실제 평점 : %s" % grade_get())
        
    elif 1 <= star_grade < 2:
        streamlit_1star()
        st.info("실제 평점 : %s" % grade_get())
        
    else:
        st.info("실제 평점 : %s" % grade_get())

# 예측 평점
def Predict_grade():
    stars = int(sum(star_score))/len(sheet)
    int_stars = int(stars)
    
    if int_stars == 5:
        predict_5star()
        st.info("예측 평점 : %.1f" % stars)
        
    elif 4 <= int_stars < 5:
        predict_4star()
        st.info("예측 평점 : %.1f" % stars)
        
    elif 3 <= int_stars < 4:
        predict_3star()
        st.info("예측 평점 : %.1f" % stars)
        
    elif 2 <= int_stars < 3:
        predict_2star()
        st.info("예측 평점 : %.1f" % stars)
        
    elif 1 <= int_stars < 2:
        predict_1star()
        st.info("예측 평점 : %.1f" % stars)
        
    else:
        st.info("실제 평점 : %.1f" % stars)


# 댓글 분석 눌렀을때...
def Naver_Shopping_Analysis():
    # Search 버튼 클릭 시....

    st.success("검색을 완료됐습니다. 댓글 개수가 많아질수록 분석 시간도 증가합니다.")

    st.info(f"입력하신 주소는 {str(input_url)} 입니다.")

    with st_lottie_spinner(lottie_Shopping, key="Shopping", height=1000, speed=1.1):
        st_lottie_spinner(Shopping())
    # 쇼핑몰 크롤링
    st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
    # 데이터 분석
    Analysis()

    # 긍정 댓글, 확률
    global pd_contain, pd_contain2, pd_contain3

    pd_contain = pd.DataFrame({'긍정 댓글' : contain})
    pd_contain_number = pd.DataFrame({'평점': contain_number})
    pos_result = pd.concat([pd_contain, pd_contain_number], axis=1)

    #부정 댓글, 확률
    pd_contain2 = pd.DataFrame({'부정 댓글' : contain2})
    pd_contain_number2 = pd.DataFrame({'평점': contain2_number})
    neg_result = pd.concat([pd_contain2, pd_contain_number2], axis=1)
    
    # 중립 댓글, 확률
    pd_contain3 = pd.DataFrame({'중립 댓글' : contain3})
    pd_contain_number3 = pd.DataFrame({'평점': contain3_number})
    neu_result = pd.concat([pd_contain3, pd_contain_number3], axis=1)

    #긍정, 부정 엑셀파일로 저장
    pos_result.to_excel('./shop_emotion/%s_positive.xlsx' % title_get())
    neg_result.to_excel('./shop_emotion/%s_negative.xlsx' % title_get())
    neu_result.to_excel('./shop_emotion/%s_neutral.xlsx' % title_get())


    #긍정, 부정 파일 불러오기
    open_pex = pd.read_excel("./shop_emotion/%s_positive.xlsx" % title_get())
    open_nex = pd.read_excel("./shop_emotion/%s_negative.xlsx" % title_get())
    open_neu = pd.read_excel("./shop_emotion/%s_neutral.xlsx" % title_get()) 


    #긍정 열 값 가져오기
    pex_text = open_pex['긍정 댓글']
    pex_percent = open_pex['평점']
    pex_list =[]

    #부정 열 값 가져오기
    nex_text = open_nex['부정 댓글']
    nex_percent = open_nex['평점']
    nex_list =[]
    
    #중립 열 값 가져오기
    neu_text = open_neu['중립 댓글']
    neu_percent = open_neu['평점']
    neu_list =[]

    #DB 긍정 댓글 중 ['']  삭제
    for cell in pex_text:
        result = re.sub('[\[\]\'n\\\]', ' ', cell)
        pex_list.append(result)

    #DB 부정 댓글 중 [''] 삭제
    for cell in nex_text:
        result2 = re.sub('[\[\]\'n\\\]', ' ', cell)
        nex_list.append(result2)
            
    #DB 중립 댓글 중 [''] 삭제
    for cell in neu_text:
        result3 = re.sub('[\[\]\'n\\\]', ' ', cell)
        neu_list.append(result3)

    f_pex_list = pd.DataFrame({'긍정 리뷰' : pex_list})
    f_nex_list = pd.DataFrame({'부정 리뷰' : nex_list})
    f_neu_list = pd.DataFrame({'중립 리뷰' : neu_list})
    

    pos_result = pd.concat([f_pex_list, pd.DataFrame(pex_percent)], axis=1)
    pos_result = pos_result.style.set_precision(1)
    
    neg_result = pd.concat([f_nex_list, pd.DataFrame(nex_percent)], axis=1)
    neg_result = neg_result.style.set_precision(1)
    
    neu_result = pd.concat([f_neu_list, pd.DataFrame(neu_percent)], axis=1)
    neu_result = neu_result.style.set_precision(1)

    
    ### 평점
    st.markdown("<h2 style='text-align: center; color: yellow; '>평점</h2>", unsafe_allow_html=True)
    Real_grade()
    Predict_grade()
    ###

    #전체 댓글
    st.info("전체 리뷰(개수 : %s)" % len(sheet))
    
    # 데이터 프레임 출력
    st.success("긍정 리뷰(개수 : %s)" % len(pd_contain))
    st.table(pos_result)
    
    st.error("부정 리뷰(개수 : %s)" % len(pd_contain2))
    st.table(neg_result)
    
    st.warning("중립 리뷰(개수 : %s)" % len(pd_contain3))
    st.table(neu_result)
    

    st.info("")
    # 원형 차트 출력 
    st.markdown("<h3 style='text-align: center; color: green; '>원형 차트</h3>", unsafe_allow_html=True)
    Create_plot()

    st.info("")
    # 워드 클라우드 출력
    st.markdown("<h3 style='text-align: center; color: skyblue; '>워드 클라우드</h3>", unsafe_allow_html=True)
    Create_pword()
    Create_nword()
    Create_aword()
    
###################################################################CSS 함수
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def streamlit_title():
    lottie_url_title = "https://assets1.lottiefiles.com/packages/lf20_5ngs2ksb.json"
    lottie_title = load_lottieurl(lottie_url_title)
    st_lottie(lottie_title, key="title", height=400)


################################################################### 평점 별 CSS
def streamlit_1star(): 
    lottie_url_1star = "https://assets3.lottiefiles.com/private_files/lf30_gjwkgweu.json"
    lottie_1star = load_lottieurl(lottie_url_1star)
    st_lottie(lottie_1star, key="1stars", height=300)
    
    
def streamlit_2star():  
    lottie_url_2star = "https://assets3.lottiefiles.com/private_files/lf30_liff4pv6.json"
    lottie_2star = load_lottieurl(lottie_url_2star)
    st_lottie(lottie_2star, key="2stars", height=300)

def streamlit_3star():
    lottie_url_3star = "https://assets3.lottiefiles.com/private_files/lf30_15cotjfi.json"
    lottie_3star = load_lottieurl(lottie_url_3star)
    st_lottie(lottie_3star, key="3stars", height=300)

def streamlit_4star(): 
    lottie_url_4star = "https://assets3.lottiefiles.com/private_files/lf30_r3usrsoq.json"
    lottie_4star = load_lottieurl(lottie_url_4star)
    st_lottie(lottie_4star, key="4stars", height=300)

def streamlit_5star(): 
    lottie_url_5star = "https://assets3.lottiefiles.com/private_files/lf30_fnh9mbud.json"
    lottie_5star = load_lottieurl(lottie_url_5star)
    st_lottie(lottie_5star, key="5stars", height=300)


########### 예측 평점 ###########

def predict_1star(): 
    lottie_url_1star = "https://assets3.lottiefiles.com/private_files/lf30_gjwkgweu.json"
    lottie_1star = load_lottieurl(lottie_url_1star)
    st_lottie(lottie_1star, key="1star", height=300)
    
    
def predict_2star():  
    lottie_url_2star = "https://assets3.lottiefiles.com/private_files/lf30_liff4pv6.json"
    lottie_2star = load_lottieurl(lottie_url_2star)
    st_lottie(lottie_2star, key="2star", height=300)

def predict_3star():
    lottie_url_3star = "https://assets3.lottiefiles.com/private_files/lf30_15cotjfi.json"
    lottie_3star = load_lottieurl(lottie_url_3star)
    st_lottie(lottie_3star, key="3star", height=300)

def predict_4star(): 
    lottie_url_4star = "https://assets3.lottiefiles.com/private_files/lf30_r3usrsoq.json"
    lottie_4star = load_lottieurl(lottie_url_4star)
    st_lottie(lottie_4star, key="4star", height=300)

def predict_5star(): 
    lottie_url_5star = "https://assets3.lottiefiles.com/private_files/lf30_fnh9mbud.json"
    lottie_5star = load_lottieurl(lottie_url_5star)
    st_lottie(lottie_5star, key="5star", height=300)
    

###################################################################

################################################################크롤링 검색시 사용
lottie_url_search = "https://assets1.lottiefiles.com/packages/lf20_7cdnmkzr.json"
lottie_search = load_lottieurl(lottie_url_search)

################################################################크롤링 진행중일때 사용
lottie_url_Shopping = "https://assets1.lottiefiles.com/datafiles/XvkAoqzOt84tzDQ/data.json"
lottie_Shopping = load_lottieurl(lottie_url_Shopping)


###################################################################

# 웹 제목
streamlit_title()
st.markdown("<h1 style='text-align: center; color: green;'>Naver</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; '>쇼핑 평점 분석</h3>", unsafe_allow_html=True)


# 주소 입력
with st.form('sub', clear_on_submit=True):
    input_url = st.text_input(label="URL", value="")
    url=input_url
    print(url)
    st.form_submit_button('분석')


if st.form_submit_button and url:
    with st_lottie_spinner(lottie_search, key="search", height=300):
        time.sleep(2)
    Naver_Shopping_Analysis()