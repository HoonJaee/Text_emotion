from genericpath import exists
from logging import exception
import time
import pandas as pd
from googleapiclient.discovery import build
import os
import re
from requests import request
import scipy as sp
from sqlalchemy import true
import streamlit as st
import pafy as pa
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from pykospacing import Spacing
from collections import Counter
from konlpy.tag import Okt
from tqdm import tqdm
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from keras.models import load_model
from sklearn.metrics.pairwise import manhattan_distances
from PIL import Image
import pickle
import sqlite3 as sq
############################################################CSS 전용
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
import requests

okt = Okt()

# 주소 뒤 시간이 있다면..
def num_re():
    # range(int) -> int는 시간값
    for i in range(10000000):
        # &t= 코드는 고정
        if my_str.find("&t="):
            # 찾았다면 repplace
            temp ="&t=%ss" %i
            str = my_str.replace(temp, "")
            
            # find 결과가 false면 -1 리턴. 변환 후엔 당연히 false가 반환
            if str.find("&t=")==-1:
                return str
            else:
                # 쓰레기 값. if문을 쓰기 위함
                a=1
        else:
            # 시간 안적혀 있으면 그대로 리턴
            return str 
    return str
  


#썸네일 출력
def get_thumbnail(url):
    id = url
    img = 'https://img.youtube.com/vi/{}/0.jpg'.format(id)
    return img    

# 제목 가져와서 변환 후 변환 값 return
def title_get():
    videoinfo = pa.new(url)
    video_title = videoinfo.title

    #제목 특수기호 있으면 공백으로 치환
    rp_video_title = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…《\》]', '', video_title)
    return rp_video_title

# 댓글 크롤링하여 xlsx 형태로 video_xlsx 폴더에 저장
def Crawling():
    #api키 입력
    api_key = 'AIzaSyBwKI6s7TsyJ1yNNvRcJ50SuhiLyNqHdSs'
    comments = list()
    api_obj = build('youtube', 'v3', developerKey=api_key)
    response = api_obj.commentThreads().list(part='snippet,replies', videoId=my_str2, maxResults=100).execute()
    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append([comment['textDisplay'], comment['authorDisplayName'], comment['publishedAt'], comment['likeCount']])
        if 'nextPageToken' in response:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=my_str2, pageToken=response['nextPageToken'], maxResults=100).execute()
        else:
            break
    df = pd.DataFrame(comments)
    df = df.astype(str)
    df.to_excel('./video_xlsx/%s.xlsx' % (title_get()), header=['comment', 'author', 'date', 'num_likes'], index=None)
    path = './video_xlxs/%s.xlsx' % (title_get())
    while os.path.exists(path) :
        df.to_excel('./video_xlsx/%s.xlsx' % (title_get()), header=['comment', 'author', 'date', 'num_likes'], index=None)
        break
       
contain = []            #긍정 cell
contain_number =[]      #긍정 확률
contain2 = []           #부정 cell
contain2_number = []    #부정 확률
contain3 = []           #중립
contain3_number = []    #중립 확률
pos_emotion = []        #감정 분류
neg_emotion = []

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
        
        # 긍정적이라면 contain 리스트에 추가
        if(score > 0.7):
            contain.append(list)
            contain_number.append(score * 100)
        # 중립이라면 contain3 리스트에 추가
        elif 0.5 < score < 0.7:
            contain3.append(list)
            contain3_number.append(score*100)
        # 부정적이라면 contain2 리스트에 추가
        else:
            contain2.append(list)
            contain2_number.append( (1 - score) * 100)


    # 다른 함수에서도 쓰기 위해 global(전역변수) 선언
    global filename, sheet
    filename = pd.read_excel('./video_xlsx/%s.xlsx' % title_get())
    sheet = filename['comment']

    # comment 칼럼의 각각의 데이터를 읽기
    for cell in sheet:
        list = []
        output_sentence = str(cell)
        
        # 댓글에 html 코드가 존재한다면...
        if "</a>" in output_sentence:
            split = output_sentence.split('</a>')

            # 단순 시간만 적혀있었다면 split은 공백값이 남음. split의 1번째 index에 '' <<(이름 모를 공백값, NULL값 아님)이 있다면 출력에서 제외
            if split[1] == '':
                continue
            # 없으면 list에 저장
            else:
                for c in split:
                    split2 = re.sub('(<([^>]+)>)','', c)
                list.append(split2)
            
        # 아무것도 해당 안되면 바로 list에 추가
        else:
            split = re.sub('(<([^>]+)>)','', output_sentence)
            list.append(split)

        # 감정 예측
        sentiment_predict(list)

# 리스트를 문자열 형태로 변환
def list_to_str(list):
    # 결과를 담을 공백 리스트 생성
    data_list = []
    # 인자로 받아온 리스트를 for문으로 돌린 후 data_list에 저장
    for i in list:
        data_list.append(i)
    # 저장된 data_list를 str(문자열) 형태로 변환 후 return
    return str(data_list)

# 긍정 워드 클라우드
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
    pwc = WordCloud(font_path='malgun', width=400, height=400, scale=2.0, max_font_size=250)
    
    pg = pwc.generate_from_frequencies(pc)
    pfig = plt.figure()
    
    plt.imshow(pg, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('./result_wc/%s_positive.png' % title_get())
    plt.show()

    st.success("긍정")
    st.pyplot(pfig)
    
# 부정 워드 클라우드
def Create_nword():
    neg = ''.join([str(n) for n in contain2])
    # neg = list_to_str(contain2)
    
    nn = okt.nouns(neg)
    nw = [n for n in nn if len(n) > 1]
    nc = Counter(nw)
    nwc = WordCloud(font_path='malgun', width=400, height=400, scale=2.0, max_font_size=250)
    
    ng = nwc.generate_from_frequencies(nc)
    nfig = plt.figure()
    
    plt.imshow(ng, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('./result_wc/%s_negative.png' % title_get())
    plt.show()
    
    st.error("부정")
    st.pyplot(nfig)
   
# 중립 워드 클라우드
def Create_aword():
    neu = ''.join([str(n) for n in contain3])
    # neg = list_to_str(contain2)
    
    nn = okt.nouns(neu)
    nw = [n for n in nn if len(n) > 1]
    nc = Counter(nw)
    nwc = WordCloud(font_path='malgun', width=400, height=400, scale=2.0, max_font_size=250)
    
    ng = nwc.generate_from_frequencies(nc)
    nfig = plt.figure()
    
    plt.imshow(ng, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('./result_wc/%s_neutral.png' % title_get())
    plt.show()
    
    st.warning("중립")
    st.pyplot(nfig)   

# 원형 차트 생성
# 1. 저장된 엑셀 파일의 comments 길이를 계산
# 2. 긍정, 부정으로 저장된 comments의 길이를 계산, 이를 활용해 비율을 계산
# 3. 이를 토대로 원형 차트 출력 
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

# 데이터 베이스 경로 저장
def save_db():
    # db 생성
        conn = sq.connect('test.db', isolation_level=None, )
        print('db 연동에 성공했습니다.')

        # 커서 획득
        c = conn.cursor()
        print('커서 획득에 성공했습니다.')

        # 경로 지정
        pex = './result_video/%s_positive.xlsx' % title_get()
        nex = './result_video/%s_negative.xlsx' % title_get()
        cpath = './result_image/%s_chart.png' % title_get()
        ppath = './result_wc/%s_positive.png' % title_get()
        npath = './result_wc/%s_negative.png' % title_get()
        
        print('파일 반환에 성공했습니다.')

        # id 테이블 저장
        c.execute('CREATE TABLE IF NOT EXISTS ipList \
            (id integer primary key AUTOINCREMENT, vid text);')
        c.execute('INSERT INTO ipList(vid) VALUES (?);', (title_get(),))
        print('IP주소가 할당되었습니다.')

        # data 테이블 저장
        c.execute("CREATE TABLE IF NOT EXISTS edata \
            (id integer primary key AUTOINCREMENT, vid text , pex text, nex text, chart text, pwc text, nwc text);")
        print('테이블이 생성되었습니다.')

        c.execute('INSERT INTO edata(vid, pex, nex, chart, pwc, nwc) VALUES (?,?,?,?,?,?);', (title_get(), pex, nex , cpath, ppath, npath))
        print('데이터를 저장했습니다.')# 테이블 생성
        
        
        
        # ipList 테이블에서 id값 가져오기
        c.execute('SELECT id FROM ipList;')
        all_id = c.fetchall()
        
        def search_history():
            for row in all_id:
                # idList 테이블의 id값에 접근, id값이 5 이상일 경우 초기화
                # id값은 검색 기록 버튼을 할당하기 위한 값. 
                print(row)
                int_row = int(''.join(map(str, row))) 
                if int_row > 3:
                    c.execute('DROP TABLE ipList;')
                    c.execute('DROP TABLE edata;')
                    print("데이터 삭제 완료")
                    st.sidebar.write("검색 기록이 초기화 됐습니다.")
                    conn.commit()
                         
        
        search_history()
        
        conn.commit()
        conn.close()

# 버튼 클릭시 기록 호출            
if st.sidebar.button('1'):
    try:
        conn = sq.connect('test.db', isolation_level=None, )
        c = conn.cursor()
        c.execute('SELECT pex, nex, chart, pwc, nwc FROM edata WHERE id == 1;')

        # 테이블의 0,1....4번째 index 값 가져오기
        all = c.fetchone()
        pex = all[0]
        nex = all[1]
        chart = all[2]
        pwc = all[3]
        nwc = all[4]
        print("데이터 베이스에서 경로를 가져오는데 성공했습니다.")

        # 오픈
        open_pex = pd.read_excel(pex)
        open_nex = pd.read_excel(nex)
        open_chart =  Image.open(chart)
        open_pwc =  Image.open(pwc)
        open_nwc =  Image.open(nwc)

        # 출력
        st.write(open_pex)
        st.write(open_nex)
        st.image(open_chart)
        st.image(open_pwc)
        st.image(open_nwc)
    
    except:
        st.error("저장된 기록이 존재하지 않습니다.")
    
if st.sidebar.button('2'):
    try:
        conn = sq.connect('test.db', isolation_level=None, )
        c = conn.cursor()
        c.execute('SELECT pex, nex, chart, pwc, nwc FROM edata WHERE id == 2;')

        # 테이블의 0,1....4번째 index 값 가져오기
        all = c.fetchone()
        pex = all[0]
        nex = all[1]
        chart = all[2]
        pwc = all[3]
        nwc = all[4]
        print("데이터 베이스에서 경로를 가져오는데 성공했습니다.")

        # 오픈
        open_pex = pd.read_excel(pex)
        open_nex = pd.read_excel(nex)
        open_chart =  Image.open(chart)
        open_pwc =  Image.open(pwc)
        open_nwc =  Image.open(nwc)

        # 출력
        st.write(open_pex)
        st.write(open_nex)
        st.image(open_chart)
        st.image(open_pwc)
        st.image(open_nwc)
    except:
        st.error("저장된 기록이 존재하지 않습니다.")

if st.sidebar.button('3'):
    try:
        conn = sq.connect('test.db', isolation_level=None, )
        c = conn.cursor()
        c.execute('SELECT pex, nex, chart, pwc, nwc FROM edata WHERE id == 3;')

        # 테이블의 0,1....4번째 index 값 가져오기
        all = c.fetchone()
        pex = all[0]
        nex = all[1]
        chart = all[2]
        pwc = all[3]
        nwc = all[4]
        print("데이터 베이스에서 경로를 가져오는데 성공했습니다.")

        # 오픈
        open_pex = pd.read_excel(pex)
        open_nex = pd.read_excel(nex)
        open_chart =  Image.open(chart)
        open_pwc =  Image.open(pwc)
        open_nwc =  Image.open(nwc)

        # 출력
        st.write(open_pex)
        st.write(open_nex)
        st.image(open_chart)
        st.image(open_pwc)
        st.image(open_nwc)
    
    except:
        st.write("저장된 기록이 존재하지 않습니다.")

def detail(senetence, num):
        text = senetence
        
        text = re.sub('[-=+,#/\:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…《\》br]', '', text)
        new_sent = text.replace(" ", '') # 띄어쓰기가 없는 문장 임의로 만들기
        new_sent = text.replace("ㅋ",' ㅋ').replace("ㅜ",' ㅜ').replace("ㅠ",' ㅠ').replace("?",' ?').replace("ㅎ",' ㅎ')
        
        
        
        spacing = Spacing()
        kospacing_text = spacing(new_sent)
    
    
        texxt = open("./data/sad.txt","r",encoding='UTF-8')
        lists = texxt.readlines()
        result_sad = list_to_str(lists)
        texxt.close()
        #슬픔

        sentence = (result_sad,kospacing_text)

    
        
        texxt1 = open("./data/happy.txt","r",encoding='UTF-8')
        lists1 = texxt1.readlines()
        result_happy = list_to_str(lists1)
        texxt1.close()
        #기쁨
        
        sentence1 =(result_happy,kospacing_text)
            

        texxt2 = open("./data/anger.txt","r",encoding='UTF-8')
        lists2 = texxt2.readlines()
        result_anger = list_to_str(lists2)
        texxt2.close()
        #분노

        sentence2 =(result_anger,kospacing_text)        
        
        texxt3 = open("./data/surprised.txt","r",encoding='UTF-8')
        lists3 = texxt3.readlines()
        result_surprised = list_to_str(lists3)
        texxt3.close()
        #놀람
        sentence3=(result_surprised,kospacing_text)


        # 객체 생성
        tfidf_vectorizer = TfidfVectorizer()
        
        # 문장 벡터화 진행
        tfidf_matrix = tfidf_vectorizer.fit_transform(sentence)
        tfidf_matrix1 = tfidf_vectorizer.fit_transform(sentence1)
        tfidf_matrix2 = tfidf_vectorizer.fit_transform(sentence2)
        tfidf_matrix3 = tfidf_vectorizer.fit_transform(sentence3)
        

        # 각 단어
        text = tfidf_vectorizer.get_feature_names()
        
        

        # 각 단어의 벡터 값
        # idf = tfidf_vectorizer.idf_
        

        manhattan_distances(tfidf_matrix[0:1], tfidf_matrix[1:2])
        manhattan_distances(tfidf_matrix1[0:1], tfidf_matrix1[1:2])
        manhattan_distances(tfidf_matrix2[0:1], tfidf_matrix2[1:2])
        manhattan_distances(tfidf_matrix3[0:1], tfidf_matrix3[1:2])




        tokenized_doc1 = set(sentence[0].split(' '))
        tokenized_doc2 = set(sentence[1].split(' '))

        tokenized_doc3 = set(sentence1[0].split(' '))
        tokenized_doc4 = set(sentence1[1].split(' '))

        tokenized_doc5 = set(sentence2[0].split(' '))
        tokenized_doc6 = set(sentence2[1].split(' '))
        tokenized_doc7 = set(sentence3[0].split(' '))
        tokenized_doc8 = set(sentence3[1].split(' '))
        


        union = set(tokenized_doc1).union(set(tokenized_doc2))
        union1 = set(tokenized_doc3).union(set(tokenized_doc4))
        union2 = set(tokenized_doc5).union(set(tokenized_doc6))
        union3 = set(tokenized_doc7).union(set(tokenized_doc8))
        


        intersection = set(tokenized_doc1).intersection(set(tokenized_doc2))
        intersection1 = set(tokenized_doc3).intersection(set(tokenized_doc4))
        intersection2 = set(tokenized_doc5).intersection(set(tokenized_doc6))
        intersection3 = set(tokenized_doc7).intersection(set(tokenized_doc8))
        
        
        Score = len(intersection)/len(union)
        Score1 = len(intersection1)/len(union1)
        Score2 = len(intersection2)/len(union2)
        Score3 = len(intersection3)/len(union3)
        

        
        

        def ORDER():
            dict_test = {
                '감정': ['슬픔', '기쁨', '분노', '놀람'],
                '유사도': [Score, Score1, Score2, Score3],
            }

            df_test = pd.DataFrame(dict_test)
            df_test = df_test.sort_values(by=['유사도'], ascending=False)

            df = df_test['감정']
            df_list = []
            

            for df_cell in df:
                df_list.append(df_cell)   

            df_finish =  pd.DataFrame({'감정' : df_list})

            first = df_finish['감정']
            list_first = first[0]

            if num == 1:
                pos_emotion.append(list_first)
            elif num == 0:
                neg_emotion.append(list_first)
            else:
                print('감정 저장 실패')

        
        ORDER()

def em(list, num):
    for cell in list:
        detail(str(cell), num)

# 댓글 분석 눌렀을때...
def Youtube_Comments_Analysis():
# Search 버튼 클릭 시....
    # Search 버튼 클릭 시....

    st.success("검색을 완료하였습니다. 댓글 개수가 많아질수록, 분석 시간도 증가합니다.")


    # 결과(입력 주소) 출력
    st.info("입력하신 주소는 %s 입니다." % input_url)
    
    # 썸네일 출력
    st.markdown("<h3 style='text-align: center; '>YouTube 영상 썸네일</h3>", unsafe_allow_html=True)
    st.image(get_thumbnail(my_str2), width=700)
    st.balloons()


    # 댓글 크롤링
    Crawling()
    st.info("")
    st.markdown("<h2 style='text-align: center; '>감정 분석</h2>", unsafe_allow_html=True)
    st.info("")
    with st_lottie_spinner(lottie_analysis, key="analysis", height=900, speed=1.2):
        st_lottie_spinner(Analysis())

    #감정 세분화
    em(contain, 1)
    em(contain2, 0)

    #긍정 감정 리스트
    pd_pos_emotion = pd.DataFrame({'감정' : pos_emotion})
    
    #부정 감정 리스트
    pd_neg_emotion = pd.DataFrame({'감정' : neg_emotion})
    # 긍정 댓글, 확률
    global pd_contain, pd_contain2, pd_contain3, pos_result, neg_result, neu_result
    pd_contain = pd.DataFrame({'긍정 댓글' : contain})
    pd_contain_number = pd.DataFrame({'확률': contain_number})
    pos_result = pd.concat([pd_contain, pd_contain_number], axis=1)     #엑셀 저장용
    pos_result2 = pd.concat([pos_result, pd_pos_emotion], axis=1)       #streamlit 출력용
    
    
    # 부정 댓글, 확률
    pd_contain2 = pd.DataFrame({'부정 댓글' : contain2})
    pd_contain_number2 = pd.DataFrame({'확률': contain2_number})
    neg_result = pd.concat([pd_contain2, pd_contain_number2], axis=1)   #엑셀 저장용
    neg_result2 = pd.concat([neg_result, pd_neg_emotion], axis=1)       #streamlit 출력용
    
    # 중립 댓글, 확률
    pd_contain3 = pd.DataFrame({'중립 댓글' : contain3})
    pd_contain_number3 = pd.DataFrame({'확률': contain3_number})
    neu_result = pd.concat([pd_contain3, pd_contain_number3], axis=1)
    
    
    # 결과 저장
    pos_result.to_excel('./result_video/%s_positive.xlsx' % title_get(), header=['comments', 'Probability'])
    neg_result.to_excel('./result_video/%s_negative.xlsx' % title_get(), header=['comments', 'Probability'])
    neu_result.to_excel('./result_video/%s_neutral.xlsx' % title_get(), header=['comments', 'Probability'])
    # 원형 차트 출력
    st.markdown("<h3 style='text-align: center; color: green; '>원형 차트</h3>", unsafe_allow_html=True)
    Create_plot()
    
    
    # 데이터 프레임
    st.success("긍정(개수 : %s)" % poslen)
    st.dataframe(pos_result2)
    
    st.error("부정(개수 : %s)" % neglen)
    st.dataframe(neg_result2)
    
    st.info("중립(개수 : %s)" % neulen)
    st.dataframe(neu_result)
    
    
    # 워드 클라우드 출력
    st.markdown("<h3 style='text-align: center; color: skyblue; '>워드 클라우드</h3>", unsafe_allow_html=True)
    Create_pword()
    Create_nword()
    Create_aword()
    
    save_db()
        
###################################################################CSS 함수
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def streamlit_title():
    lottie_url_title = "https://assets1.lottiefiles.com/packages/lf20_xtuje6sh.json"
    lottie_title = load_lottieurl(lottie_url_title)
    st_lottie(lottie_title, key="title", height=300)

################################################################크롤링 검색시 사용
lottie_url_search = "https://assets1.lottiefiles.com/packages/lf20_7cdnmkzr.json"
lottie_search = load_lottieurl(lottie_url_search)

################################################################분석시 사용
lottie_url_analysis = "https://assets1.lottiefiles.com/datafiles/XvkAoqzOt84tzDQ/data.json"
lottie_analysis = load_lottieurl(lottie_url_analysis)


###################################################################

# 웹 제목
streamlit_title()
st.markdown("<h1 style='text-align: center; color: red;'>YouTube</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; '>댓글 분석</h3>", unsafe_allow_html=True)


# 주소 입력
with st.form('main', clear_on_submit=True):
    input_url = st.text_input(label="URL", value="")
    url=input_url
    my_str = url.replace("https://www.youtube.com/watch?v=","")
    st.form_submit_button('분석')


if st.form_submit_button and my_str:
    with st_lottie_spinner(lottie_search, key="search", height=300):
        time.sleep(2)
    my_str2 = num_re()
    Youtube_Comments_Analysis()