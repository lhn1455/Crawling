from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import pandas as pd
import time
import os
load_dotenv()


# 데스크탑 위치 
path = os.path.join(os.path.expanduser('~'),'Desktop')

# 크롤링할 페이지
url = "https://www.jobplanet.co.kr/users/sign_in?_nav=gb"

# 크롤링할 회사
company = "위메이드"

# 로그인 정보
login = {
    "user_email" : os.environ.get("Email"),
    "user_password" : os.environ.get("Password") 
}

# 크롤링할 리뷰 페이지 수 (전체 페이지 중 보여질 페이지 수 지정)
nPage = 5


# 크롬드라이브 위치
driver = webdriver.Chrome(path + "/chromedriver")

# 페이지 get
driver.get(url)
time.sleep(2)

# 로그인
driver.find_element(By.CSS_SELECTOR,"input#user_email").send_keys(login.get("user_email"))
driver.find_element(By.CSS_SELECTOR,"input#user_password").send_keys(login.get("user_password"))
driver.find_element(By.XPATH, '//*[@id="signInSignInCon"]/div[2]/div/section[3]/fieldset/button').click()
driver.implicitly_wait(10)
time.sleep(1)

# 회사 검색
driver.find_element(By.CSS_SELECTOR,"input#search_bar_search_query").send_keys(company)
driver.find_element(By.CSS_SELECTOR,"input#search_bar_search_query").send_keys(Keys.RETURN)
driver.implicitly_wait(10)
time.sleep(1)

# 검색 결과에서 첫번째 결과값 클릭
driver.find_element(By.CSS_SELECTOR,"a.tit").click()
driver.implicitly_wait(10)
time.sleep(1)

# 팝업창 닫기
driver.find_element(By.CSS_SELECTOR,"button.btn_close_x_ty1 ").click()
driver.implicitly_wait(15)
time.sleep(1)

# 면접 탭 클릭
driver.find_element(By.CLASS_NAME,"viewInterviews").click()
driver.implicitly_wait(10)
time.sleep(1)

# 전체 면접 리뷰에 대한 페이징
interview_cnt_raw = driver.find_elements(By.CSS_SELECTOR,"span.num.notranslate")[3]
interview_cnt = int(interview_cnt_raw.text)
page = int(interview_cnt/5) + 1
driver.implicitly_wait(10)
time.sleep(1)


# 크롤링 함수 정의
def crawling(page):
    #크롤링한 정보를 담을 리스트명 정의
    list_index = []
    list_duty = []
    list_contents = []
    list_question = []
    list_answer_atmosphere= []
    
    user_info = []

 
      
    for i in range(page): 
       
        # 면접자 정보 [직무, 스펙, 일시]
        user_info = driver.find_elements(By.CSS_SELECTOR,"span.txt1")

        # 직무만 파싱
        for j in user_info:
            duty = j.text.split("  /  ")
            list_duty.append(duty[0])

        # 면접 질문, 면접 답변 혹은 면접 분위기 파싱 및 예외 처리
        review = driver.find_elements(By.CSS_SELECTOR,"dl.tc_list")
        for j in review:
            list_contents.append(j.text)
            if "면접질문" in j.text:
                rm1 = j.text.split("면접질문")
                if "면접답변 혹은 면접느낌" in rm1[1]:
                    qs = rm1[1].split("면접답변 혹은 면접느낌")
                    list_question.append(qs[0])
                    if "채용방식" in qs[1]:
                        an = qs[1].split("채용방식")
                        list_answer_atmosphere.append(an[0])
                    elif "발표시기" in qs[1]:
                        an = qs[1].split("발표시기")   
                        list_answer_atmosphere.append(an[0]) 
                    else:
                        list_answer_atmosphere.append(qs[1])  
                elif "채용방식" in rm1[1]:
                    qs = rm1[1].split("채용방식")
                    list_question.append(qs[0])
                    list_answer_atmosphere.append("-")     
                elif "발표시기" in rm1[1]:
                    qs = rm1[1].split("발표시기")
                    list_question.append(qs[0])
                    list_answer_atmosphere.append("-")   
                else:
                    list_question.append(rm1[1])
                    list_answer_atmosphere.append("-")  
            elif "면접답변 혹은 면접느낌" in j.text:
                qs = j.text.split("면접답변 혹은 면접느낌")
                list_question.append("-")
                if "채용방식" in qs[1]:
                    an = qs[1].split("채용방식")
                    list_answer_atmosphere.append(an[0])
                elif "발표시기" in qs[1]:
                    an = qs[1].split("발표시기")   
                    list_answer_atmosphere.append(an[0])  
            elif "채용방식" in j.text:
                list_question.append("-")
                an = j.text.split("채용방식")
                list_answer_atmosphere.append("-")
            elif "발표시기" in j.text:
                list_question.append("-")
                an = j.text.split("발표시기")
                list_answer_atmosphere.append("-")
            else:
                list_question.append("-")
                list_answer_atmosphere.append("-")

        #다음 페이지 클릭 후 for문 진행, 끝 페이지에서 다음 페이지 클릭 안되는 것 대비해서 예외 처리
        try:
            driver.find_element(By.CSS_SELECTOR, "a.btn_pgnext").click()
            driver.implicitly_wait(20)
            time.sleep(5)
        except:
            pass
    
    # 인덱스  
    for i in range(int(len(user_info))*page):
            i += 1
            list_index.append(i)
            
    # 라이브러리로 표 만들기
    total_data = pd.DataFrame()
    total_data['Index'] = pd.Series(list_index)
    total_data['직무'] = pd.Series(list_duty)
    total_data['내용'] = pd.Series(list_contents)
    total_data['면접질문'] = pd.Series(list_question)
    total_data['면접답변 혹은 면접느낌'] = pd.Series(list_answer_atmosphere)

    # 엑셀 형태로 저장하기
    total_data.to_excel(path + "/" + company + "_interview.xlsx", index=False)


# 실제 실행 함수
if page <= nPage: 
    crawling(page)
   
else:
    page = nPage
    crawling(page)


# step10.크롬 드라이버 종료
driver.quit()



