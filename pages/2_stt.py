#-*- coding: utf-8 -*-
from email import header
from operator import truediv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import SCORERS
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import manhattan_distances
from konlpy.tag import Okt
import re
from pykospacing import Spacing
import pandas as pd
import requests
import streamlit as st
from streamlit_lottie import st_lottie
import streamlit as st
import pickle
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from konlpy.tag import Okt
from keras.models import load_model
import speech_recognition as sr
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from konlpy.tag import Kkma
import os
from pydub import AudioSegment


def Analysis(num):
    tokenizer = Tokenizer()
    okt = Okt()
    max_len = 30

    # 불용어
    stopwords = ['은', '는', '이', '가', '하', '아', '것', '들', '의', '있', '되', '수', '보', '주', '등', '한', '줄', '를', '을', '에', '에게', '께', '한테', '더러', '에서', '에게서',
                 '한테서', '로', '으로', '와', '과', '도', '부터', '도', '만', '이나', '나', '라도', '의', '거의', '겨우', '결국', '그런데', '즉', '참', '챗', '할때', '할뿐', '함께', '해야한다', '휴']

    # PATH = '/Users/82102/Desktop/project/yt_cr/backup/'
    PATH = './model_test/'
    # PATH2 = '/Users/82102/Desktop/project/yt_cr/backup/'
    # PATH2 = './model/'

    #모델 및 토큰 불러오기
    model = load_model(PATH + 'best_model.h5')
    with open(PATH+'tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # 감정 예측
    def sentiment_predict(new_sentence, num):
        new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]', '', str(new_sentence))
        new_sentence = okt.morphs(new_sentence, stem=True)  # 토큰화
        new_sentence = [word for word in new_sentence if not word in stopwords]  # 불용어 제거
        encoded = tokenizer.texts_to_sequences([new_sentence])  # 정수 인코딩
        pad_new = pad_sequences(encoded, maxlen=max_len)  # 패딩
        score = float(model.predict(pad_new))  # 예측

        
        # 마이크 입력
        if num == 0:
            if(score > 0.7):
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_positive_1()
                st.success("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 강한 긍정의 문장입니다.\n".format(score * 100))
                st.balloons()
                emotion = 1
                detail(0, emotion)
            elif(0.7> score > 0.6):
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_positive_2()
                st.success("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 긍정적인 문장입니다.\n".format(score * 100))
                emotion = 1
                st.balloons()
                detail(0, emotion)
            elif(0.6> score > 0.4):
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_neutrality()
                st.warning("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 중립적인 문장입니다.\n".format(score * 100))
                st.balloons()
                emotion = 3
                detail(0, emotion)
            elif(0.4> score > 0.3):
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_negative_1()
                st.error("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 부정적인 문장입니다.\n".format(score * 100))
                st.snow()
                emotion = 0
                detail(0, emotion)
            else:
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_negative_2()
                st.error("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 강한 부정의 문장입니다.\n".format(score * 100))
                st.snow()
                emotion = 0
                detail(0, emotion)
        
        # 파일 업로드
        if num == 1:
            if(score > 0.6):
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_positive_1()
                st.success("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 강한 긍정의 문장입니다.\n".format(score * 100))
                st.balloons()
                detail(1)
            elif(0.6> score > 0.5):
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_positive_2()
                st.success("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 긍정적인 문장입니다.\n".format(score * 100))
                st.balloons()
                detail(1)
            elif(0.5> score > 0.4):
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_neutrality()
                st.warning("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 중립적인 문장입니다.\n".format(score * 100))
                st.balloons()
                detail(1)
            elif(0.4> score > 0.3):
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_negative_1()
                st.error("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 부정적인 문장입니다.\n".format(score* 100))
                detail(1)
            else:
                st.markdown("<h2 style='text-align: center; '>분석 결과</h2>", unsafe_allow_html=True)
                streamlit_negative_2()
                st.error("전체 문장의 분석 결과, 감정 점수 {:.2f}점 으로 강한 부정의 문장입니다.\n".format(score* 100))
                detail(1)

    # num = 0 이면 실시간 녹음 or 텍스트
    if num == 0:
        sentiment_predict(user_input, num)
        
    
    # num = 1 이면 파일 업로드
    if num == 1:
        sentiment_predict(wb_text, num)
        

 #리스트 문자열로 변환
def listToString(str_list):
    result = ""
    for s in str_list:
        result += s + " "
    return result.strip()


def detail(num, emotion):
    if num == 0:
        text = user_input
        st.info(user_input)
    if num == 1:
        text = wb_text
        st.info(wb_text)

    text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…《\》]', '', text)
    new_sent = text.replace(" ", '') # 띄어쓰기가 없는 문장 임의로 만들기

    spacing = Spacing()
    kospacing_text = spacing(new_sent)

    
    
    ######################################################################형태소 + 불용어
    kkma = Kkma()
    ex_pos = kkma.morphs(kospacing_text) 


    good_text = " ".join(ex_pos)

    ###################################################################

    texxt = open("./data/fear.txt","r",encoding='UTF-8')
    lists = texxt.readlines()
    result_fear = listToString(lists)
    texxt.close()
    #공포
    sentence = (result_fear,good_text)

    texxt2 = open("./data/pleasure.txt","r",encoding='UTF-8')
    lists2 = texxt2.readlines()
    result_pleasure = listToString(lists2)
    texxt2.close()
    #기쁨
    sentence2 =(result_pleasure,good_text)  

    texxt3 = open("./data/anger.txt","r",encoding='UTF-8')
    lists3 = texxt3.readlines()
    result_anger = listToString(lists3)
    texxt3.close()
    #분노
    sentence3=(result_anger,good_text)
        
    texxt4 = open("./data/love.txt","r",encoding='UTF-8')
    lists4 = texxt4.readlines()
    result_love = listToString(lists4)
    texxt4.close()
    #사랑
    sentence4=(result_love,good_text)

    texxt6 = open("./data/sad.txt","r",encoding='UTF-8')
    lists6 = texxt6.readlines()
    result_sad = listToString(lists6)
    texxt6.close()
    #슬픔
    sentence6=(result_sad,good_text)

    # 객체 생성
    tfidf_vectorizer = TfidfVectorizer()
    # 문장 벡터화 진행
    tfidf_matrix = tfidf_vectorizer.fit_transform(sentence)
    tfidf_matrix2 = tfidf_vectorizer.fit_transform(sentence2)
    tfidf_matrix3 = tfidf_vectorizer.fit_transform(sentence3)
    tfidf_matrix4 = tfidf_vectorizer.fit_transform(sentence4)
    tfidf_matrix6 = tfidf_vectorizer.fit_transform(sentence6)

    # 각 단어
    text = tfidf_vectorizer.get_feature_names()
    # 각 단어의 벡터 값
    idf = tfidf_vectorizer.idf_

    manhattan_distances(tfidf_matrix[0:1], tfidf_matrix[1:2])
    manhattan_distances(tfidf_matrix2[0:1], tfidf_matrix2[1:2])
    manhattan_distances(tfidf_matrix3[0:1], tfidf_matrix3[1:2])
    manhattan_distances(tfidf_matrix4[0:1], tfidf_matrix4[1:2])
    manhattan_distances(tfidf_matrix6[0:1], tfidf_matrix6[1:2])

    tokenized_doc1 = set(sentence[0].split(' '))
    tokenized_doc2 = set(sentence[1].split(' '))
    tokenized_doc5 = set(sentence2[0].split(' '))
    tokenized_doc6 = set(sentence2[1].split(' '))
    tokenized_doc7 = set(sentence3[0].split(' '))
    tokenized_doc8 = set(sentence3[1].split(' '))
    tokenized_doc9 = set(sentence4[0].split(' '))
    tokenized_doc10 = set(sentence4[1].split(' '))
    tokenized_doc13 = set(sentence6[0].split(' '))
    tokenized_doc14 = set(sentence6[1].split(' '))


    union = set(tokenized_doc1).union(set(tokenized_doc2))
    union2 = set(tokenized_doc5).union(set(tokenized_doc6))
    union3 = set(tokenized_doc7).union(set(tokenized_doc8))
    union4 = set(tokenized_doc9).union(set(tokenized_doc10))
    union6 = set(tokenized_doc13).union(set(tokenized_doc14))


    intersection = set(tokenized_doc1).intersection(set(tokenized_doc2))
    intersection2 = set(tokenized_doc5).intersection(set(tokenized_doc6))
    intersection3 = set(tokenized_doc7).intersection(set(tokenized_doc8))
    intersection4 = set(tokenized_doc9).intersection(set(tokenized_doc10))
    intersection6 = set(tokenized_doc13).intersection(set(tokenized_doc14))


    

    Score = len(intersection)/len(union)*1000
    Score2 = len(intersection2)/len(union2)*1000
    Score3 = len(intersection3)/len(union3)*1000
    Score4 = len(intersection4)/len(union4)*1000
    Score6 = len(intersection6)/len(union6)*1000

    print(Score)
    print(Score2)
    print(Score3)
    print(Score4)
    print(Score6)


    def ORDER():
        dict_test = {
            '감정': ['공포', '기쁨', '분노', '사랑', '슬픔'],
            '유사도': [Score, Score2, Score3, Score4, Score6],
        }
        dict2_test = {
            '순위': [1,2,3,4,5]
        }

        # 감정 및 유사도
        df_test = pd.DataFrame(dict_test)
        df_test = df_test[df_test['유사도'] > 0]
        df_test = df_test.sort_values(by=['유사도'], ascending=False)
        
        # 순위
        df2_test = pd.DataFrame(dict2_test)


        df = df_test['감정']
        df_list = []


        for df_cell in df:
            df_list.append(df_cell)    

        df_finish =  pd.DataFrame({'감정' : df_list})

        result = pd.concat([df2_test, df_finish], axis=1)
        result = result[result['감정'].notna()]
        result.set_index('순위', inplace=True)


        st.markdown("<h2 style='text-align: center; '>세부 감정 분석 결과</h2>", unsafe_allow_html=True)
        
        
        st.table(result)

        # set을 문자열로
        def Set_to_String(set):
            sentence = str(set)
            sentence2 = sentence.replace("{","").replace("}","").replace("'","")
            return sentence2
        
        if emotion == 0:
            if Score > 0:
                st.warning("공포와 관련된 단어")
                st.info(Set_to_String(intersection))
            if Score3 > 0:
                st.error("분노와 관련된 단어")
                st.info(Set_to_String(intersection3))
            if Score6 > 0:
                st.warning("슬픔과 관련된 단어")
                st.info(Set_to_String(intersection6))

        if emotion == 1:
            if Score2 > 0:
                st.success("기쁨과 관련된 단어")
                st.info(Set_to_String(intersection2))
            if Score4 > 0:
                st.success("사랑과 관련된 단어")
                st.info(Set_to_String(intersection4))
                
        if emotion == 3:
            if Score2 > 0:
                st.success("기쁨과 관련된 단어")
                st.info(Set_to_String(intersection2))
            if Score4 > 0:
                st.success("사랑과 관련된 단어")
                st.info(Set_to_String(intersection4))
            if Score > 0:
                st.warning("공포와 관련된 단어")
                st.info(Set_to_String(intersection))
            if Score3 > 0:
                st.error("분노와 관련된 단어")
                st.info(Set_to_String(intersection3))
            if Score6 > 0:
                st.warning("슬픔과 관련된 단어")
                st.info(Set_to_String(intersection6))
                


    ORDER()
    

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def streamlit_title():
    lottie_url_title = "https://assets5.lottiefiles.com/private_files/lf30_XPbZB7.json"
    lottie_title = load_lottieurl(lottie_url_title)
    st_lottie(lottie_title, key="title", height=300)

def streamlit_analysis():
    lottie_url_title = "https://assets5.lottiefiles.com/private_files/lf30_XPbZB7.json"
    lottie_title = load_lottieurl(lottie_url_title)
    st_lottie(lottie_title, key="title", height=300)

def streamlit_positive_1():
    lottie_url_positive_1 = "https://assets3.lottiefiles.com/packages/lf20_wml3ec.json"
    lottie_positive_1 = load_lottieurl(lottie_url_positive_1)
    st_lottie(lottie_positive_1, key="analysis", height=300)

def streamlit_positive_2():
    lottie_url_positive_2 = "https://assets3.lottiefiles.com/packages/lf20_lopDQz.json"
    lottie_positive_2 = load_lottieurl(lottie_url_positive_2)
    st_lottie(lottie_positive_2, key="analysis", height=300)

def streamlit_neutrality():
    lottie_url_neutrality = "https://assets3.lottiefiles.com/packages/lf20_VR4DyP.json"
    lottie_neutrality = load_lottieurl(lottie_url_neutrality)
    st_lottie(lottie_neutrality, key="analysis", height=300)

def streamlit_negative_1():
    lottie_url_negative_1 = "https://assets3.lottiefiles.com/packages/lf20_7DnubQ.json"
    lottie_negative_1 = load_lottieurl(lottie_url_negative_1)
    st_lottie(lottie_negative_1, key="analysis", height=300)

def streamlit_negative_2():
    lottie_url_negative_2 = "https://assets3.lottiefiles.com/packages/lf20_CZ5mts.json"
    lottie_negative_2 = load_lottieurl(lottie_url_negative_2)
    st_lottie(lottie_negative_2, key="analysis", height=300)




##############################################################

# 마이크 입력

def Audio():
    # microphone에서 auido source를 생성합니다
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.success("음성녹음 시작")
        audio = r.listen(source)

        st.error("음성녹음 종료")

    global user_input
    user_input = r.recognize_google(audio, language='ko')

def start():
    if st.form_submit_button("마이크 ON"):
        #음성녹음 시작
        Audio()

        #감정 시작
        if st.form_submit_button and user_input:
            st.markdown("<h1 style='text-align: center; '>작성 내용</h1>", unsafe_allow_html=True)
            st.info(user_input)
            # 기능에 따라 분류하기 위함
            Analysis(0)
##############################################################

# 파일 업로드

def upload():
    uploaded_file = st.file_uploader("파일을 선택해주세요", type=(["mp3", "wav"]))
    if uploaded_file is not None:
        #bytes_data = 오디오 파일
        global bytes_data
        bytes_data = uploaded_file.name
        st.success('파일을 업로드 했습니다. : {} '.format(bytes_data))


# 음성 파일 불러와서 텍스트로 전환
def STT():
    r = sr.Recognizer()
    # 파일명과 확장자 분리
    global name
    name, ext = os.path.splitext(filename)

    # wav
    if ext == ".wav":
        harvard_audio = sr.AudioFile(filepath)
        with harvard_audio as source:
            audio = r.record(source)
        global wb_text
        wb_text = r.recognize_google(audio, language='ko-KR')
    # mp3. 업로드시 wav로 변환
    elif ext == '.mp3':
        mp3_sound = AudioSegment.from_mp3(filepath)
        wav_sound = mp3_sound.export("{0}.wav".format(name), format="wav")
        harvard_audio = sr.AudioFile(wav_sound)
        with harvard_audio as source:
            audio = r.record(source, duration=150)
        text = r.recognize_google(audio, language='ko-KR')
    # 나머지..
    else:
        st.write("wav 와 mp3 형식만 호환됩니다.")

def sub(list):
    for cell in list:
        detail(str(cell))

def file_upload():
    path = '/Users/82102/Desktop/project/yt_cr/audio/'
    upload()
    global filename, filepath
    filename = bytes_data
    filepath = path + bytes_data
    STT()
    Analysis(1)



##############################################################


st.markdown("<h1 style='text-align: center; '>Speech To Text</h1>", unsafe_allow_html=True)

streamlit_title()

option = st.sidebar.selectbox("선택", ('MIC', 'Upload'))

if option == 'MIC':
    with st.form('stt', clear_on_submit=True):
        st.success("아래에 마이크를 입력해주세요")
        start()

if option == 'Upload':
    try:
        file_upload()
    except:
        # 오류 메세지 없애는 쓰레기 코드
        a=1


