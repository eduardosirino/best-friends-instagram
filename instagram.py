from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import random
import credenciais


def seguir():
    url = 'https://www.instagram.com/accounts/close_friends/'
    login = 'https://www.instagram.com/accounts/login/'
    
    #setup para usar webdriver
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    #driver
    driver = webdriver.Chrome(options=chrome_options)
    #aqui estou deixando o tamanho do navegador (tamanho da janela)padronizado :)
    driver.set_window_size(1024, 768)

    driver.get(login)
    sleep(5)
    #Encontra tela de login

    user_ig = driver.find_element(
        "xpath", '//*[@id="loginForm"]/div/div[1]/div/label/input')
    password_ig = driver.find_element(
        "xpath", '//*[@id="loginForm"]/div/div[2]/div/label/input')

    sleep(1)
    user_ig.clear()
    user_ig.send_keys(credenciais.email_instagram)
    sleep(0.3)
    password_ig.clear()
    password_ig.send_keys(credenciais.password_instagram)
    sleep(1)
    password_ig.send_keys(Keys.ENTER)
    sleep(5)

    #Inicio:
    driver.get(url)

    sleep(5)
    accounts = driver.find_elements(By.XPATH, '''/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div[2]/div[2]/div/div[2]/div/div''')
    
    x = 1
    for account in accounts:
        print(x)
        button = account.find_element(By.TAG_NAME, 'div').find_elements(By.TAG_NAME, 'div')[-1]

        # timeSleep = random.randint(0, 5)
        # sleep(timeSleep)

        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button))

        # sleep(0.2)

        button.click()
        x += 1
            
    return
        
if __name__ == "__main__":
    seguir()
