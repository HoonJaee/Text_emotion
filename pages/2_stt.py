from matplotlib.text import Text
import speech_recognition as sr
import os
import sys
import streamlit as st
import pickle
import re
import pandas as pd
import pyaudio
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from konlpy.tag import Okt
from pydub import AudioSegment
from keras.models import load_model
from operator import truediv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import manhattan_distances
from pykospacing import Spacing


#-----------------------------------------------------------------------------------


# 업로드
def upload():
    uploaded_file = st.file_uploader("Choose a file", type=(["mp3", "wav"]))
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
        global text
        text = r.recognize_google(audio, language='ko-KR')
    # mp3
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


contain = []  # 긍정 cell
contain_number = []
contain2 = []  # 부정 cell
contain2_number = []


def Analysis(sentence):
    tokenizer = Tokenizer()
    okt = Okt()
    max_len = 30

    # 불용어
    stopwords = ['은', '는', '이', '가', '하', '아', '것', '들', '의', '있', '되', '수', '보', '주', '등', '한', '줄', '를', '을', '에', '에게', '께', '한테', '더러', '에서', '에게서',
                 '한테서', '로', '으로', '와', '과', '도', '부터', '도', '만', '이나', '나', '라도', '의', '거의', '겨우', '결국', '그런데', '즉', '참', '챗', '할때', '할뿐', '함께', '해야한다', '휴']

    PATH = './model_test/'

    #모델 및 토큰 불러오기
    model = load_model(PATH + 'best_model.h5')
    with open(PATH+'tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    # 감정 예측

    def sentiment_predict(new_sentence):
        new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]', '', str(new_sentence))
        new_sentence = okt.morphs(new_sentence, stem=True)  # 토큰화
        new_sentence = [word for word in new_sentence if not word in stopwords]  # 불용어 제거
        encoded = tokenizer.texts_to_sequences([new_sentence])  # 정수 인코딩
        pad_new = pad_sequences(encoded, maxlen=max_len)  # 패딩
        score = float(model.predict(pad_new))  # 예측

        # 긍정적이라면 contain 리스트에 추가
        if(score > 0.5):
            contain.append(sentence)
            contain_number.append(score*100)

        # 부정적이라면 contain2 리스트에 추가
        else:
            contain2.append(sentence)
            contain2_number.append((1 -score)*100)

    sentiment_predict(sentence)

# 슬픔, 기쁨, 분노, 중립
s_list = []
p_list = []
n_list = []
u_list = []

def detail(senetence):
        text = senetence
        
        text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…《\》]', '', text)
        new_sent = text.replace(" ", '') # 띄어쓰기가 없는 문장 임의로 만들기
        
    
        # print(new_sent)
        
        spacing = Spacing()
        kospacing_text = spacing(new_sent)
    
        
        #print(text)
        # print(kospacing_text)

        # 슬픔, 기쁨, 분노, 중립 리스트

        
        try:
            texxt = "진짜 입니다 개슬퍼 이별 너무 보고싶다 한번만 이라도 보고싶어 보고싶다 ㅠㅜ ㅜㅠ 눈물이 눈물이 헤어지고 와서 눈물나네요 슬퍼요 슬프다 슬프네 울고싶다 애통 원통 가슴앓이 울분 구슬프다 가슴아프다 우울하다 암울하다 복받치다 사무치다 울상 낙심 낙심하다 애처롭다 속상해 속상하다 속상 울컥 울컥하다 울컥하네요 흑흑 ㅠㅠ 속앓이 애석하다 좌절 좌절하다 찡하다 참담 참담하다 참담하네요 글썽 글썽이다 죄책 죄책감 외롭다 외로워 눈물 눈물겹다 울적하다 울적 절망 서럽다 서러워 상실감 상실 침울 ㅜ ㅜㅜ ㅠ ㅠㅠ ㅠㅠㅠ 슬퍼 내 친구가 학교에서 따돌림을 당하고 있어 나랑 가장 친한 친구가 질병에 걸렸어 근래에 허리가 아파서 잘 걷지도 못하겠고 한참 앉아있지도 못하니까 지인들이랑 점점 멀어지네 친구가 갑자기 뇌출혈로 입원했어 요즘 사람들한테 정말 실망했어 동맥경화로 입원까지 했는데 이곳까지 찾아오는 사람이 없구나 엄마랑 길을 가던 도중에 날 따돌림 시키던 가해자가 비웃으면서 지나갔어 슬퍼 부모님이 내 학교 폭력을 아시자마자 학교로 와서 나에게 화를 내셨어 무서워 건강 챙기려고 운동을 시작하면서 살이 빠지는 줄 알았는데 체중을 재니 별로 안 빠져 실망스러웠어 동기는 틈만 나면 클라이언트 험담을 해 내 욕도 어디선가 하고 있겠구나 싶어 슬퍼져 아내가 교통사고를 당해 크게 다쳤다는 전화를 받았어 걱정돼서 눈물이 나 친구가 친구들을 괴롭히지 않기로 나랑 약속했는데 또 학교폭력을 저질렀어 속상해 친구가 내가 괴롭힘을 당할 때면 언제든 찾아와 주겠다고 말해놓고 숨어버렸어 속상해 고등학교에서 만난 소꿉친구가 날 괴롭히는 데 앞장섰어 속상해 새 친구와 가까워졌다고 생각했는데 알고 보니 학교폭력 가해자였어 친구한테 실망했어 가족들에게 따돌림당한 걸 얘기했는데 오히려 나를 꾸짖었어 가족들에게 실망했어 돈이 없어서 계속 이사를 다녀야 하는게 골치가 아파 내 동생은 몸이 아픈데도 불구하고 도박은 꾸준히 하러 나가 오늘 은퇴했는데 아무도 나를 신경 안 쓰네 여행 준비를 모두 마쳤는데 여자 친구가 급한 일이 생겨서 못 간다고 해서 실망이야 아들이 실업계 고등학교를 가서 빨리 취업하고 싶다고 했는데 그렇게 하라고 할 걸 오랫동안 병원에 입원하니까 답답하고 우울하게 변하는 것 같아서 우울해 대기업에 입사할 줄 알았는데 적성 시험에서 탈락했어 슬퍼 지방에 있는 대학을 다니면 비웃는 친구에게 환멸이 오늘도 회사에서 점심을 혼자 먹었어 평소랑 다르게 왜 이리 서글퍼지는지 학생 때 공부를 왜 더 안 했는지 모르겠어서 슬프고 후회가 친구들과 싸움이 없는 날이 하루도 없네 이제 도움을 청할 친구 자체가 없어 애들에게 계속 당하기만 하니까 미치겠다 학교에서 계속 나를 견제하는 애들 때문에 도저히 공부에 집중할 수가 없어 내가 모든 노력을 투자한 업무가 무의미해져 버려서 슬퍼 육 개월이면 완치된다고 하지만 난 그 말 안 믿어 병이 그렇게 빨리 낫겠어? 그런 경험 있어? 아침에 일어났는데 갑자기 몸이 움직이지 않은 적 말이야 이번에 남편에게 실망했어 내 재정 점검을 해보니 암담해 내가 원하는 직업이 있는데 부모님이 반대하셔 부모님께 실망스러워 요즘 대인관계에 있어서 환멸을 느껴. 친구들이 나를 싫어하는 것 같아서 잘해보려고 하는데 그게 잘 안 되네. 나 요즘 인간관계에 대해 회의감이 느껴지고 우울해. 대인관계에 관한 부분으로 감정이 마비된 것 같아. 과장님이 매번 불러서 나만 혼내는 것 같아. 다른 팀원들에게는 그러지 않고. 젊을 때 몸 안 아끼고 밤 새우면서 열심히 일했는데 백세시대라면서 할 일도 막혔어. 갱년기 증상이 심해서 우울해! 이번에 본 면접 또 떨어졌어 어제 갑자기 올려 달라고 하네 어디서 오천만 원을 구하지? 안 좋아서 병원에 입원을 했어 ㅠㅠ 나도 다니던 직장에 이야기하고 ㅠ 며칠 휴가를 썼고 좋아하는 고백했는데 차여서 ㅜㅜ "
            #슬픔
    
            sentence = (texxt,kospacing_text)
    
            # print(kospacing_sad)
            
            texxt1="ㄷㄷ 좋아요 귀엽다 진짜 좋은 ㅋㅋㅋㅋ 잘 너무 좋아 좋다 ㅈㄴ 대박 기분이 ㅋㅋㅋ 매우 좋았어 개 웃기네 마음이 편해졌어 다행이야 다행이야 뿌듯해 정말 기대된다 편안하게 쉴 수 있어서 행복해 따뜻한 시선으로 바라보게 된 것 같아 기분이 좋아 기뻐 자랑스러워 안도했어 고마워 믿어 최고의 기쁘고 ㅋㅋㅋㅋㅋㅋ 행복했어 정말 고마웠어 웃기고 터짐ㅋㅋ 개웃기네 귀엽닼ㅋㅋ 개빵터짐열라웃었네ㅋㅋ 닷ㅋㅋ 개웃음 재밌닼ㅋㅋㅋㅋ 엌ㅋㅋㅋㅋ 엌 이겈 비록 암에 걸렸지만 나는 무조건 건강을 되찾을거야 내가 질병 때문에 오래 못 살 것 같아 동무랑 오래 걷기 승부를 했어 요즘 나이가 들었는지 몸이 안 좋았는데 내 주변 지인들이 염려해주는 걸 보니 기분이 매우 좋았어 재산 관리를 전문가에게 맡기니깐 마음이 편해졌어 앞집 사장님이 이자에 대한 부담을 주지 않고 돈을 빌려줘서 다행이야 엄마가 아끼는 화분을 떨어뜨렸는데 가까스로 붙잡았어 다행이야 은퇴 후 삶에 대한 강의를 듣고 나의 노후계획을 멋지게 만들어 보았어 맘에 들어서 뿌듯해 지금까지 모아둔 돈으로 아내와 여행을 매주 가려고 준비 중이야 정말 기대된다 내가 지금까지 열심히 살아서 은퇴하고도 돈 걱정 없이 편안하게 쉴 수 있어서 너무 행복해 아이가 생기고 세상을 좀 더 따뜻한 시선으로 바라보게 된 것 같아 퇴사해서 걱정이 많았는데 한 번에 시험에 합격해서 너무 기분이 좋아 아내에게 돈을 맡겼는데 재테크로 돈을 불려놨지 뭐야 너무 기분이 좋아 주말 출근을 하게 됐지만 월요일과 화요일에 쉬기로 해서 기뻐 잔소리하지 않아도 방을 깨끗하게 잘 치우는 아들이 너무 자랑스러워 나와 거래하는 업체는 신선한 재료를 가져다줄 것이라고 믿어 딸이 다행히 내 마음에 안 드는 남자친구와 헤어져서 안도했어 내가 보호자도 없는데 신경 써주는 간호사에게 너무 고마워 노인정 사람들이 감사하게도 내 수술비에 보태라고 돈을 주었어 나이를 많이 먹었다 보니 병원을 자주 가는데 갈 때마다 며느리가 항상 데려다줘서 편하고 고마워 요즘 기분도 안 좋았는데 산책도 하고 책에 나온 대로 따라 하니까 마음이 한결 나아진 거 같아 ㅋㅋㅋㅋㅋㅋㅋㅋ 여행 계획을 짜는데 우리 가족 모두가 내 말을 수용해주니 정말 기뻐 수학 만점을 받았다는 게 믿기지 않아 이번 시험에서 일 등급을 받아서 너무 기뻐 우리 팀은 우리 회사에서 가장 뛰어나다고 믿어 나는 이번 기회에 큰 성과를 거둘 수 있을 거라고 믿어 나는 항상 우리 팀원들과 최고의 성과를 도출해낼 것이라고 믿어 이 회사가 나의 커리어에 큰 도움이 될 것이라고 확신해 겨울에 아빠랑 시골에 갔을 때 기쁘고 행복했어 요즘 집에 있는 시간이 늘어난 것 같아 어제 지인 때문에 화가 많이 났었는데 가족들과 이야기한 후 그분을 이해할 수 있어서 정말 고마웠어 이 거래처는 한두 번도 아니고 매번 직전에 발주 내용을 바꿔 지금 너무 열 받아서 확 내지르고 싶은 심정이야 곧 은퇴하는데 내가 너무 느긋한가 싶어 아빠가 오늘 엄마랑 엄청나게 싸웠는데 싸우는 도중에 이혼 얘기까지 나왔었어 ㅋㅋ 나는 사람들과의 관계에 자신이 있어. 나 좀 기분 좋은 일이 있어 비록 몸이 젊을 때 만큼 팔팔하지는 않지만 남의 부축 없이 다닐 수 있으니 감사를 해야지 우리 집은 다른 집보다 자식들이 잘되었어. 나는 건강에 자신 있어. 얼마 전 취직한 곳에 내일 처음으로 출근하는데 너무 신이 나 결혼을 하고 나니 생활이 더 안정감 있는 것 같아서 너무 좋아 나 결정했어 면접 봤던 회사에서 합격 전화가 왔어 내년에 남편이 은퇴를 하고 그 다음 해에는 내가 은퇴를 할 예정인데 내가 힘들면 올해까지만 다닐까 싶기도 해 좋은 친구를 만났어 같이 있으면 편안한 기분이 들어 은퇴하기 전까지 열심히 벌어서 딸아이 교육하고 시집 보내고 전원 주택 지을 돈까지 마련하자고 했는데 생각보다 승진했어 너무 행복하다 ㅋㅋㅋㅋㅋㅋㅋㅋ 드디어 ㅎ"
            #기쁨
            
            sentence1 =(texxt1,kospacing_text)
                
    
            texxt2="좌절감이 들어 진짜 왜 나이먹고 잔소리가 많다고 생각하는지 모르겠네 ㅈ 같다 부담이 좋지 않아 요즘 짜증 나 ㅈ같다 싫어하는 화가나 화를 냈어 철이 없는 걸까? 싫다고 툴툴댔어 탈모가 화를 화가 났어 하소연했어 화도 나고 서럽고 너무 억울해 초조해 너무 화가 나 너무 초조해 성가셔 싫어하는 귀찮고 짜증 났어 짜증 나 화를 냈어 왜 그러는 걸까? 화가 나 욕을 축내는 않아 기분이 좋지 않아 점점 싫어지고 속상해 겠어 오늘 학교에 갔는데 갑자기 애들이 은근슬쩍 날 피하는 게 느껴졌어 화가 나 친구들한테 따돌림당하지 않고 잘 지내고 싶은 게 내 욕심일까? 너무 화가 나 걔네들이 오늘도 나를 괴롭혔어 더 이상 학교에 가기가 싫어 쉬는 시간에 선생님 몰래 같은 반 애들이 친구를 때리는 걸 봐서 화가 났어 친구가 다이어트를 시작한다는 이야기를 들었더니 너무 화가 나 팀원들이 열심히 참여를 안 해줘서 속상해! 이틀 연속 외근이라니 나한테 왜 그러는 걸까? 모두가 손해 보는 일이나 프로젝트에는 서로들 지원하지 않으려고만 해 화가 나 취업 못 하는 친구들을 비하하는 사람이 있는데 더 이상 친구로는 지낼 수 없을 것 같아 회사를 그만두어야 될 것 같아 이번 보직변경을 수용할 수 없어 ㅈ같다 지도교수님이 추천서를 써주기로 했는데 아직 연락이 없어서 조급해 나는 급한데 언제 해주신다고 확답이 없으니 답답해 여유 자금이 없어서 너무 불안해 같은 직장 동료가 나에게 거짓말을 해서 무척 노여워 대학 졸업은 했는데 취업이 안돼서 걱정이야 자꾸 툴툴대게 돼 요즘 성가신 광고 전화가 너무 와서 큰일이야 직장에 입사한 지 삼 개월이 지났는데 회사 사람들 누구와도 친해지지 못하고 있어 남자친구와 더운 날씨에 오랫동안 야외데이트를 하다 보니 짜증이 났어 노안이 와서 신문을 읽을 수가 없어 나는 요즘 친구가 무슨 말을 하기만 하면 친구에게 악의적인 비난을 퍼붓게 돼 존나 ㅅㅂ ㅄ 그 팀장은 왜 그러는 걸까? 화가 나 내가 같은 성별인 대리님을 좋아하는 이유로 욕을 먹었어 같은 반 친구가 시험 시간에 커닝을 했는데 학교에서 조치 없이 넘어가서 화가 나 가족 중 나만 돈을 안 벌고 있어 난 밥만 축내는 존재야 나 빼고 노는 친구들이랑은 기분이 나빠서 더 이상 잘 지내고 싶지 않아 친구가 나한테 성적이 낮다고 말해서 자존심이 상하고 기분이 좋지 않아 친구들이 편을 나눠서 계속 싸움을 해서 학교가 점점 싫어지고 속상해. 따돌림을 당하고 있는데 반 친구들이 너무 무서워서 어떻게 해야 할지 모르겠어 ㅈ같아 오늘 학교에 갔는데 갑자기 애들이 은근슬쩍 날 피하는 게 느껴졌어 화가 나 친구들한테 따돌림당하지 않고 잘 지내고 싶은 게 내 욕심일까? 너무 화가 나 걔네들이 오늘도 나를 ㅈㄴ 괴롭혔어 더 이상 학교에 가기가 싫어 쉬는 시간에 선생님 몰래 같은 ㅈㄹ 때리는 걸 봐서 화가 났어 ㅈ같네 이야기를 들었더니 너무 화가 나 팀원들이 열심히 참여를 안 해줘서 속상해! 이틀 연속 외근이라니 나한테 왜 그러는 걸까? 모두가 손해 보는 일이나 프로젝트에는 서로들 지원하지 않으려고만 해 화가 나 취업 못 하는 친구들을 비하하는 사람이 있는데 더 이상 친구로는 지낼 수 없을 것 같아 회사를 그만두어야 될 것 같아 이번 보직변경을 수용할 수 없어 지도교수님이 추천서를 써주기로 했는데 아직 연락이 없어서 조급해. 나는 급한데 언제 해주신다고 확답이 없으니 답답해 여유 자금이 없어서 너무 불안해 같은 직장 동료가 나에게 거짓말을 해서 무척 노여워 대학 졸업은 했는데 취업이 안돼서 걱정이야 자꾸 툴툴대게 돼 요즘 성가신 광고 전화가 너무 와서 큰일이야 직장에 입사한 지 삼 개월이 지났는데 회사 사람들 누구와도 친해지지 못하고 있어 남자친구와 더운 날씨에 오랫동안 야외데이트를 하다 보니 짜증이 났어 ㅂㅅ 신문을 읽을 수가 없어 ㅅㅂ 요즘 친구가 무슨 말을 하기만 하면 친구에게 악의적인"
            #분노
    
            sentence2 =(texxt2,kospacing_text)        
            # new_sent_happy = texxt1.replace(" ", '') # 띄어쓰기가 없는 문장 임의로 만들기
            #print(new_sent_happy)
        
        
            # spacing = Spacing()
            # kospacing_happy = spacing(new_sent_happy)
    
    
            # 객체 생성
            tfidf_vectorizer = TfidfVectorizer()
            
    
            # 문장 벡터화 진행
            tfidf_matrix = tfidf_vectorizer.fit_transform(sentence)
            tfidf_matrix1 = tfidf_vectorizer.fit_transform(sentence1)
            tfidf_matrix2 = tfidf_vectorizer.fit_transform(sentence2)
            
    
            # 각 단어
            text = tfidf_vectorizer.get_feature_names()
            
            
    
            # 각 단어의 벡터 값
            idf = tfidf_vectorizer.idf_
            
    
    
    
            # cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            # cosine_similarity(tfidf_matrix1[0:1], tfidf_matrix1[1:2])
            
            manhattan_distances(tfidf_matrix[0:1], tfidf_matrix[1:2])
            manhattan_distances(tfidf_matrix1[0:1], tfidf_matrix1[1:2])
            manhattan_distances(tfidf_matrix2[0:1], tfidf_matrix2[1:2])
    
            #print(dict(zip(text,idf)))
            #print(dict(zip(text,idf1)))
    
    
            tokenized_doc1 = set(sentence[0].split(' '))
            tokenized_doc2 = set(sentence[1].split(' '))
    
            tokenized_doc3 = set(sentence1[0].split(' '))
            tokenized_doc4 = set(sentence1[1].split(' '))
    
            tokenized_doc5 = set(sentence2[0].split(' '))
            tokenized_doc6 = set(sentence2[1].split(' '))
            
            #print("문장 1의 집합 = ", tokenized_doc1)
            #print("문장 2의 집합 = ", tokenized_doc2)
    
            union = set(tokenized_doc1).union(set(tokenized_doc2))
            union1 = set(tokenized_doc3).union(set(tokenized_doc4))
            union2 = set(tokenized_doc5).union(set(tokenized_doc6))
            
            #print("합집합 = ", union)
    
            intersection = set(tokenized_doc1).intersection(set(tokenized_doc2))
            intersection1 = set(tokenized_doc3).intersection(set(tokenized_doc4))
            intersection2 = set(tokenized_doc5).intersection(set(tokenized_doc6))
            
            print("교집합 = ", intersection)
            print("교집합 = ", intersection1)
            print("교집합 = ", intersection2)
            

            jaccardScore = len(intersection)/len(union)
            jaccardScore1 = len(intersection1)/len(union1)
            jaccardScore2 = len(intersection2)/len(union2)
            
    
            print("자카드 유사도 = ", jaccardScore)
            print("자카드 유사도 = ", jaccardScore1)
            print("자카드 유사도 = ", jaccardScore2)
            
            print('\n')
    
            #jaccardScore1 가 유난히? 높게떠서 문제시 지워도댐
            
    
            if jaccardScore>jaccardScore1 and jaccardScore>jaccardScore2 and jaccardScore>0:
                s_list.append(intersection)
                print(s_list)
                print('슬픈 ..\n')
    
            elif jaccardScore1>jaccardScore and jaccardScore1>jaccardScore2 and jaccardScore1>0:
                p_list.append(intersection1)
                print(p_list)
                print('기쁨..\n')
    
            elif jaccardScore2>jaccardScore and jaccardScore2>jaccardScore1 and jaccardScore2>0:
                n_list(intersection2)
                print(n_list)
                print('분노..\n')
    
            else:
                u_list.append(text)
                print(u_list)
                print('중립..\n')
    
    
            
        except:
            print("")
            
def sub(list):
    for cell in list:
        detail(str(cell))
#---------------------------------------------------------------------------
st.header('Speech To Text')

def file_upload():
    path = './audio/'
    upload()
    global filename, filepath
    filename = bytes_data
    filepath = path + bytes_data
    STT()
    Analysis(text)
    sub(contain)
    sub(contain2)

    st.header('기쁨')
    st.dataframe(p_list)

    st.header('슬픔')
    st.dataframe(n_list)

    st.header('분노')
    st.dataframe(n_list)

    st.header('중립')
    st.dataframe(u_list)
