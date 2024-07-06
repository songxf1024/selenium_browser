# selenium_browser
A generic library to control the browser based on selenium.

usage：
```python
from browser import Browser

browser = Browser()
driver = browser.open_browser(proxy='http://127.0.0.1:7890')
driver.get('https://myip.ipip.net/')
time.sleep(5)
driver.get('https://bot.sannysoft.com/')
try:
    time.sleep(5000)
finally:
    browser.quit_browser()
```
