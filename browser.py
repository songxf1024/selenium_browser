import copy
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains, ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from seleniumbase import Driver


class Browser:
    def __init__(self, browser_path=None, driver_path=None, driver=None) -> None:
        self._driver_type = 'uc' # none, uc or legacy
        # ---------------------------------------------- #
        self.verbose = True
        self.browser_path = browser_path or r'Chrome/chrome.exe'
        self.driver_path = driver_path or r'Chrome/chromedriver.exe'
        self.driver = driver
    
    # 检查是不是用的uc的driver
    def driver_type_uc(self):
        return self._driver_type == 'uc'
    
    # 自定义的调试信息输出
    def myprint(self, msg):
        if self.verbose: print(msg)
    
    # 传统Selenium方式打开浏览器
    def open_legacy_browser(self, headless=False, eager_loading=False, proxy=None):
        # proxy = "http://ip:port"
        options = Options()
        if headless: options.add_argument("--headless")
        if proxy: options.add_argument(f'--proxy-server={proxy}')
        # self.options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-site-isolation-trials')
        options.add_argument("--disable-features=WebRTC")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-full-form-autofill-ios")
        options.add_argument("--disable-autofill-keyboard-accessory-view[8]")
        options.add_argument("--disable-single-click-autofill")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-blink-features")
        options.add_argument("--incognito")
        options.add_argument("--mute-audio")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-setuid-sandbox")        
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-javascript")
        options.add_argument("--lang=en_US")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--no-first-run")
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_argument("--autoplay-policy=user-gesture-required")
        options.add_argument("--disable-features=ScriptStreaming")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--window-size=1080,1024")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
        if eager_loading: options.page_load_strategy = 'eager'
        try:
            return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=copy.deepcopy(options))
        except Exception as e:
            self.myprint(f'>> 浏览器启动失败 {e}')
        return None

    # SeleniumBase方式打开浏览器，支持隐藏指纹
    def open_uc_browser(self, headless=False, eager_loading=False, proxy=None):
        try:
            return Driver(browser="chrome", headless2=headless, proxy=proxy, undetectable=True, 
                    incognito=True, enable_3d_apis=False, do_not_track=True, 
                    binary_location=self.browser_path, driver_version=self.driver_path,
                    page_load_strategy="eager" if eager_loading else "normal",)
        except Exception as e:
            self.myprint(f'>> 浏览器启动失败 {e}')
        return None

    # 打开浏览器
    def open_browser(self, start_url=None, headless=False, eager_loading=False, proxy=None, web_driver_wait=120, implicitly_wait=30):
        self.driver = self.open_uc_browser(headless=headless, eager_loading=eager_loading, proxy=proxy)
        self._driver_type = 'uc' if self.driver else 'none'
        if not self.driver:
            self.myprint('>> 使用备选Chrome方案')
            self.driver = self.open_legacy_browser(headless=headless, eager_loading=eager_loading, proxy=proxy)
            self._driver_type = 'legacy' if self.driver else 'none'
        if not self.driver: return None
        self.driver.maximize_window()
        WebDriverWait(self.driver, web_driver_wait)
        self.driver.implicitly_wait(implicitly_wait)
        if start_url: 
            self.driver.get(start_url)
            self.wait_loading()
        return self.driver
    
    # 清空浏览器缓存
    def clean_cookies(self):
        self.driver.delete_all_cookies()
    
    # 关闭浏览器
    def quit_browser(self):
        self.clean_cookies()
        self.driver.quit()
        
    # 在标签页之间查找并切换到指定url
    def find_handle(self, target_url, goto_target=False):
        window_handles = self.driver.window_handles
        for handle in window_handles:
            self.driver.switch_to.window(handle)
            time.sleep(0.5)
            self.myprint('>> 查找目标标签页：' + self.driver.current_url)
            if target_url in self.driver.current_url:
                self.myprint('>> 找到目标标签')
                break
        time.sleep(1)
        if target_url not in self.driver.current_url and goto_target:
            try:
                self.driver.get(target_url)
            except TimeoutException:
                return False
            time.sleep(1)
            self.myprint('>> 跳转目标标签')
            return True
        return False

    # 等待页面加载完成
    def wait_loading(self, timeout=60):
        count = 0
        while self.driver.execute_script("return document.readyState") != "complete":
            time.sleep(1)
            count += 1
            if count > timeout: 
                self.myprint('>> 等待页面加载已超时')
                return False
        self.myprint('>> 页面加载完成')
        return True

    # 停止页面加载
    def stop_loading(self):
        try:
            self.driver.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')
            self.myprint('>> 停止加载成功')
        except:
            self.myprint('>> 停止失败，略过')
 
    # 更新cookie. 支持dict和str格式
    def update_cookies(self, cookies):
        self.clean_cookies()
        if isinstance(cookies, list):
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        elif isinstance(cookies, str):
            for pair in cookies.split(';'):
                if pair == '': continue
                name, value = pair.strip().split('=', 1)
                cookie = {
                    'name': name,
                    'value': value,
                    'domain': urlparse(self.driver.current_url).hostname,
                    'path': '/'
                }
                self.driver.add_cookie(cookie)
        else:
            self.myprint(f'暂不支持此格式的cookie: {type(cookies)}')
 
    # 页面截图
    def save_screenshot(self, path=None):
        path = path or f'{int(time.time())}.png'
        self.driver.save_screenshot(path)
        return path
 
 
if __name__ == '__main__':
    # demo
    browser = Browser()
    driver = browser.open_browser(proxy='http://127.0.0.1:7890')
    driver.get('https://myip.ipip.net/')
    time.sleep(5)
    driver.get('https://bot.sannysoft.com/')
    try:
        time.sleep(600)
    except Exception as e:
        print('done!')
    finally:
        browser.quit_browser()

 