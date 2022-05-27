# This sample code uses the Appium python client v2
# pip install Appium-Python-Client
# Then you can paste this into a file and simply run with Python
from pprint import pprint

from appium import webdriver
from appium.webdriver.webdriver import ExtensionBase, WebDriver

# For W3C actions
from selenium.webdriver.common.by import By

class xCustomURLCommand(ExtensionBase):
    def method_name(self):
        return 'get_ocr_text'

    def get_ocr_text(self, argument):
        return self.execute(argument)['value']

    def add_command(self):
        return ('post', '/session/$sessionId/appium/ocr')


caps = {}
caps["appium:deviceName"] = "iPhone 13"
caps["appium:platformVersion"] = "15.2"
caps["appium:automationName"] = "XCUITest"
caps["platformName"] = "iOS"
caps["appium:app"] = "/Users/shinjikanai/eclipse-workspace/Tutorial/src/samples/TheApp.app"
caps["appium:noReset"] = True


driver = webdriver.Remote("http://127.0.0.1:4723", caps, extensions=[CustomURLCommand])

result = driver.get_ocr_text({})
contexts=driver.contexts
driver.switch_to.context('OCR')
sp=driver.page_source
print(sp)
element = driver.find_element(by=By.XPATH, value="//lines/item[contains(text(), 'Login Screen')]")
element.click()

driver.quit()