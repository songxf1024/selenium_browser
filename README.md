# selenium_browser
A generic library to control the browser based on selenium.

# installation
```bash
pip install selenium webdriver_manager seleniumbase requests
```

# usage
```python
from browser import Browser

browser = Browser()
driver = browser.open_browser(start_url='http://xfxuezhang.cn', proxy='http://127.0.0.1:7890')
driver.get('https://myip.ipip.net/')
browser.wait_loading()
time.sleep(5)
driver.get('https://bot.sannysoft.com/')
browser.wait_loading()
try:
    time.sleep(600)
except Exception as e:
    print('done!')
finally:
    browser.quit_browser()
```

![image](https://github.com/songxf1024/selenium_browser/assets/111047002/2e24eda8-a140-488d-8ac6-87c88c46667c)
