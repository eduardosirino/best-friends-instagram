from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException,
    WebDriverException
)
from time import sleep
import random
import logging
import credenciais
from typing import List, Optional


class InstagramCloseFriendsBot:
    def __init__(self, headless: bool = False, window_size: tuple = (1024, 768), speed_mode: str = "fast"):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.headless = headless
        self.window_size = window_size
        self.speed_mode = speed_mode  # "fast", "normal", "slow"
        self.running = True
        self.log_callback = None
        self.stats_callback = None  
        self.email = ""
        self.password = ""
        
        # Configurar delays baseado no modo de velocidade
        if speed_mode == "fast":
            self.click_delay = (0.1, 0.3)
            self.batch_delay = (0.3, 0.6)
            self.batch_size = 8
        elif speed_mode == "normal":
            self.click_delay = (0.3, 0.8)
            self.batch_delay = (0.5, 1.0)
            self.batch_size = 5
        else:  # slow
            self.click_delay = (0.5, 1.2)
            self.batch_delay = (1.0, 2.0)
            self.batch_size = 3
    
    def _log(self, message, level="INFO"):
        self._log(message)
        if self.log_callback:
            self.log_callback(message, level)

    def _update_stats(self, processed, total, success, failed):
        if self.stats_callback:
            self.stats_callback(processed, total, success, failed)
                    
    def setup_driver(self) -> bool:
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Otimizações de performance
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # Não carregar imagens para maior velocidade
            chrome_options.add_argument('--aggressive-cache-discard')
            chrome_options.add_argument('--memory-pressure-off')
            
            if self.headless:
                chrome_options.add_argument('--headless')
                
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_window_size(*self.window_size)
            
            # Timeouts otimizados
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(2)
            self.wait = WebDriverWait(self.driver, 8)
            
            self._log("Driver configurado com sucesso")
            return True
            
        except WebDriverException as e:
            self.logger.error(f"Erro ao configurar driver: {e}")
            return False
            
    def random_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        delay = random.uniform(min_delay, max_delay)
        sleep(delay)
        
    def login(self) -> bool:
        try:
            login_url = 'https://www.instagram.com/accounts/login/'
            self.driver.get(login_url)
            self.random_delay(3, 5)
            
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.clear()
            username_field.send_keys(self.email)
            self.random_delay(0.2, 0.5)
            
            password_field.clear()
            password_field.send_keys(self.password)
            self.random_delay(0.5, 1.0)
            
            password_field.send_keys(Keys.ENTER)
            
            self.wait.until(
                EC.any_of(
                    EC.url_contains("/accounts/onetap/"),
                    EC.url_contains("/"),
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
            )
            
            self._log("Login realizado com sucesso")
            return True
            
        except TimeoutException:
            self.logger.error("Timeout durante o login")
            return False
        except NoSuchElementException as e:
            self.logger.error(f"Elemento não encontrado durante login: {e}")
            return False
            
    def dismiss_notifications(self):
        try:
            not_now_buttons = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Agora não')]",
                "//button[contains(text(), 'Not now')]"
            ]
            
            for xpath in not_now_buttons:
                try:
                    button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    button.click()
                    self._log("Popup de notificação dispensado")
                    break
                except TimeoutException:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Nenhum popup encontrado: {e}")
            
    def navigate_to_close_friends_page(self) -> bool:
        try:
            url = 'https://www.instagram.com/accounts/close_friends/'
            self.driver.get(url)
            self.random_delay(3, 5)
            
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//main")),
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
            )
            
            self._log("Navegou para página de melhores amigos")
            return True
            
        except TimeoutException:
            self.logger.error("Timeout ao navegar para página de melhores amigos")
            return False
            
    def find_followers_to_add(self) -> List:
        try:
            # Aguardar página carregar completamente antes de buscar elementos
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            # Usar o seletor original que funcionava
            followers = self.driver.find_elements(
                By.XPATH, 
                '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div[2]/div[2]/div/div[2]/div/div'
            )
            
            if followers:
                self._log(f"Encontrados {len(followers)} seguidores para adicionar")
                
                # Verificar se todos os elementos são válidos
                valid_followers = []
                for follower in followers:
                    try:
                        # Teste rápido para ver se o elemento tem a estrutura esperada
                        divs = follower.find_element(By.TAG_NAME, 'div').find_elements(By.TAG_NAME, 'div')
                        if divs:  # Se tem divs filhos, provavelmente é válido
                            valid_followers.append(follower)
                    except:
                        continue
                
                self._log(f"{len(valid_followers)} seguidores válidos encontrados")
                return valid_followers
            else:
                self.logger.warning("Nenhum seguidor encontrado com o seletor principal")
                return []
                
        except Exception as e:
            self.logger.error(f"Erro ao encontrar seguidores: {e}")
            return []
        
    def add_follower_to_close_friends(self, follower_element) -> bool:
        try:
            # Scroll otimizado - apenas se necessário
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'auto', block: 'nearest'});", 
                follower_element
            )
            
            # Encontrar botão de forma mais rápida
            button = follower_element.find_element(By.TAG_NAME, 'div').find_elements(By.TAG_NAME, 'div')[-1]
            
            # Wait otimizado com timeout menor
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(button))
            
            button.click()
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar seguidor aos melhores amigos: {e}")
            return False
            
    def process_all_followers(self) -> int:
        followers = self.find_followers_to_add()
        
        if not followers:
            self.logger.warning("Nenhum seguidor encontrado para adicionar")
            try:
                page_source_preview = self.driver.page_source[:500]
                self.logger.debug(f"Amostra do HTML da página: {page_source_preview}")
            except:
                pass
            return 0
            
        added_count = 0
        failed_count = 0
        max_consecutive_failures = 5
        
        self._log(f"Iniciando processamento de {len(followers)} seguidores em lotes de {self.batch_size} (modo: {self.speed_mode})")
        
        # Processar em batches para otimizar performance
        for batch_start in range(0, len(followers), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(followers))
            batch = followers[batch_start:batch_end]
            
            # Scroll para o primeiro elemento do batch
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'auto', block: 'start'});", 
                    batch[0]
                )
            except:
                pass
            
            # Processar batch
            for i, follower in enumerate(batch):
                global_index = batch_start + i + 1
                try:
                    if self.add_follower_to_close_friends(follower):
                        added_count += 1
                        failed_count = 0
                        
                        if added_count % 10 == 0 or global_index == len(followers):
                            self._log(f"Progresso: {added_count}/{len(followers)} seguidores adicionados")
                    else:
                        failed_count += 1
                        if failed_count >= max_consecutive_failures:
                            self.logger.warning(f"Muitas falhas consecutivas. Pausando...")
                            sleep(1.5)
                            failed_count = 0
                    
                    # Delay configurável entre clicks no mesmo batch
                    if i < len(batch) - 1:
                        self.random_delay(*self.click_delay)
                    
                except Exception as e:
                    self.logger.error(f"Erro ao processar seguidor {global_index}: {e}")
                    failed_count += 1
                    continue
            
            # Delay configurável entre batches
            if batch_end < len(followers):
                self.random_delay(*self.batch_delay)
                
        return added_count
        
    def adicionar_melhores_amigos(self) -> bool:
        try:
            if not self.setup_driver():
                return False
                
            if not self.login():
                return False
                
            self.dismiss_notifications()
            
            if not self.navigate_to_close_friends_page():
                return False
                
            added_count = self.process_all_followers()
            self._log(f"Processo concluído. {added_count} seguidores adicionados aos melhores amigos")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro durante execução: {e}")
            return False
        finally:
            self.cleanup()
            
    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                self._log("Driver fechado com sucesso")
            except:
                pass
                
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False