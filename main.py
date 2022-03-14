"""
@author: Maxime Dréan.

Github: https://github.com/maximedrn
Telegram: https://t.me/maximedrn

Copyright © 2022 Maxime Dréan. All rights reserved.
Any distribution, modification or commercial use is strictly prohibited.

Version 1.4.8 - 2022, 28 January.

Transfer as many non-fungible tokens as you want to
the OpenSea marketplace. Easy, efficient and fast,
this tool lets you make your life as an Artist of
the digital world much smoother.
"""


# Colorama module: pip install colorama
from colorama import init, Fore, Style

# Selenium module imports: pip install selenium
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.common.exceptions import TimeoutException as TE
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Python default imports.
from datetime import datetime as dt
from glob import glob
import os
import time


"""Colorama module constants."""
# This module may not work under MacOS.
init(convert=True, autoreset=True)  # Init the Colorama module.
red = Fore.RED  # Red color.
green = Fore.GREEN  # Green color.
yellow = Fore.YELLOW  # Yellow color.
reset = Style.RESET_ALL  # Reset color attribute.


""" Reader
* Reads files and extracts NFT data into a structured list.
"""
class Reader:

    """ Init
    @Params: 
    - path: The instance of the data file path
    """
    def __init__(self, path: str) -> None:

        # Get file's extension to lowercase (MacOS support).
        self.path = path  # Instance the file path.

        # Get splitted file name (['text', '.txt']) and then remove the dot.
        self.extension = os.path.splitext(self.path)[1][1:].lower()

        # Check if the extension is supported by the Reader class.
        if self.extension in ('json', 'csv', 'xlsx'):
            # Eval function: self.extract_{FILE_EXTENSION}_file()
            eval('self.extract_' + self.extension + '_file()')

        else:  # Stop running the script.
            exit('The file extension is not supported.')

    """ Extract json files
    * Saves JSON into a list of dictionaries
    """
    def extract_json_file(self) -> None:
        from json import loads 

        # Load and read the JSON file and extract "nft" part.
        self.file = loads(open(self.path, encoding='utf-8').read())['nft']
        self.lenght_file = len(self.file)  # Number of NFTs.

    """ Extract CSV files
    * Saves the CSV file into a list of dictionaries
    """
    def extract_csv_file(self) -> None:
        # Open file and splitlines (every "\n") and remove headers.
        # It gets a list of each rows.
        self.file = open(self.path, encoding='utf-8').read().splitlines()[1:]
        self.lenght_file = len(self.file)  # Number of NFTs.

    """  Extract xlxs files
    * Takes an xlxs file and saves it into a list of dictionaries
    """
    def extract_xlsx_file(self) -> None:
        from pandas import read_excel

        self.file = read_excel(self.path)
        self.lenght_file = self.file.shape[0]
        self.file = self.file.to_dict() 


""" Structure
* Converts the JSON/CSV/XLSX data lists into objects
"""
class Structure:

    """ Init
    @Params: 
    - action: The actions choosen
    """
    def __init__(self, action: list) -> None:
        self.file = reader.file.copy()  # File data copy.
        self.extension = reader.extension  # File extension copy.
        self.action = action  # 1, 2 or 1 and 2.
        self.completed = []

        if 1 in self.action and 2 not in self.action and 3 not in self.action:
            # Construct the save file
            file_path = os.path.splitext(reader.path)[0]
            self.save_file = f'{file_path}_uploaded.csv'
            
            # Check to see if the file exists first before creating it
            # This is useful if continuing an existing upload of large collections
            if not os.path.exists(self.save_file):
                with open(self.save_file, 'a+', encoding='utf-8') as file:
                    file.write('nft_url;; supply;; blockchain;; type;; price;; '
                               'method;; duration;; specific_buyer;; quantity;; name')

            # Otherwise read the existing file
            else:
                items = Reader(self.save_file).file
                self.completed = list(map(lambda item: str(item.split(';; ')[8]), items))
                print(f'You have already completed {len(self.completed)} of {len(self.file)} uploads.  If you are not continuing a prior opload please remove {self.save_file}')

    """ Get data
    * Gets the NFT data
    @Params:
    - nft_number: The nft currently in use
    """
    def get_data(self, nft_number: int) -> None:
        self.nft_number = nft_number

        # Eval function: self.structure_{FILE_EXTENSION}()
        eval('self.structure_' + self.extension + '()')

    """ Structure JSON
    * Transforms JSON dictionaries into list
    """
    def structure_json(self) -> None:
        nft_data = self.file[self.nft_number]

        # Get key's value from the NFT data.
        nft_data = [nft_data[data] for data in nft_data]

        # Take each element in the list and check it and structure it
        self.structure_data([self.dict_to_list(element) for element in nft_data])

    """ Structure CSV
    * Transforms CSV dictionaries into list
    """
    def structure_csv(self) -> None:
        # Note: each value is split every ";;", you can change the characters to others.
        self.structure_data(self.change_type(self.file[self.nft_number].split(';;')))

    """ Structure XLSX
    * Transforms XLSX dictionaries into list
    """
    def structure_xlsx(self) -> None:
        self.structure_data([
            element.replace('nan', '').strip() if isinstance(element, str) else
            element for element in self.change_type([self.file[element].get(self.nft_number) for element in self.file])])

    """ Dictionary to list
    * Transforms dictionaries to lists
    @Params:
    - element: Dictionary or string list
    @Returns: list or str
    """
    def dict_to_list(self, element: dict or str) -> list or str:
        # Transform a dictionnary into a list. - JSON file method.
        if isinstance(element, list): 
            final_list = [] 

            for item in element:
                temp_list = []  

                # If element is a dict. Each key in dict (item), get key's value.
                if isinstance(item, dict):  
                    [temp_list.append(item.get(key)) for key in item]
                else:
                    temp_list = item

                final_list.append(temp_list)

            return final_list

        else:
            return element  # Return the same element.

    """ Change type
    * Changes dictionary value types from strings
    @Params:
    - nft_data: List of NFT data
    @Returns: List of elements
    """
    def change_type(self, nft_data: list) -> list:
        from ast import literal_eval 

        list_ = []

        for data in nft_data: 
            # Remove whitespaces.
            element = str(data).strip()

            # Change type of element (str to int/float/list/bool).
            try: 
                list_.append(literal_eval(element))

            # SyntaxError or ValueError.
            except Exception: 
                list_.append(element)

        return list_

    """ Structur data
    * Structures the NFT data into a typed object
    @Params: 
    - nft_data: List of NFT data
    """
    def structure_data(self, nft_data: list) -> None:
        index = 9 if 1 not in self.action else 0
        if 1 in self.action:  # Upload part.
            self.file_path: str or list = nft_data[0]
            self.nft_name: str = str(nft_data[1])  # Set string value to
            self.link: str = str(nft_data[2])  # real string to prevent
            self.description: str = str(nft_data[3])  # different types.
            self.collection: str = str(nft_data[4])
            self.properties: list = nft_data[5]  # [[type, name], ...].
            self.levels: list = nft_data[6]  # [[name, from, to], ...].
            self.stats: list = nft_data[7]  # [[name, from, to], ...].
            self.unlockable_content: list or bool = nft_data[8]  # [bool, str].
            self.explicit_and_sensitive_content: bool = nft_data[9]
            self.supply: int = nft_data[10]
            self.blockchain: str = str(nft_data[11]).capitalize()
        if 2 in self.action:  # Sale part.
            self.type: str = str(nft_data[12 - index]).title()
            self.price: float or int = nft_data[13 - index]
            self.method: list = nft_data[14 - index]  # [method, price].
            self.duration: list or str = nft_data[15 - index]
            self.specific_buyer: list or bool = nft_data[16 - index]
            self.quantity: int = nft_data[17 - index]
        if index != 0:  # Sale only!
            self.nft_url: str = str(nft_data[0])
            self.supply: int = nft_data[1]
            self.blockchain: str = str(nft_data[2]).capitalize()

    """ Is empty
    * Checks if the dictionary is empty
    @Params:
    - element: The string value of the NFT
    - data: The data value fo the NFT
    - value: The value of the NFT
    @Returns: Whether or not it was successful
    """
    def is_empty(self, element: str, data: str, value: str = '') -> bool:
        if data != value:
            web.send_keys(element, data)
            return False

        return True

    """ Save nft
    * Saves the NFT data (Mainly the new NFT URL) as an uploaded list
    @Params:
    - url: The new NFT url
    - data: The existing NFT data
    """
    def save_nft(self, url, name) -> None:
        """Save the NFT URL, Blockchain and supply number in a file."""
        # Note: only CSV file will be created.
        with open(self.save_file, 'a+', encoding='utf-8') as file:
            file.write(f'\n{url};; {self.supply};; {self.blockchain};;'
                       f' ;; ;; ;; ;; ;; {name}')  # Complete data manually.
        print(f'{green}| Data saved!')
        # Save completed


""" Webdriveer
* A Web Driver wrapper
"""
class Webdriver:

    """ Init
    @Params: 
    - wallet: The wallet choice.  [Coingbase, Metamask]
    """
    def __init__(self, wallet: int) -> None:
        # Wallet extensions
        self.webdriver_path = os.path.abspath('assets/chromedriver.exe') if \
            os.name == 'nt' else os.path.abspath('assets/chromedriver')
        wallet_extension = ('MetaMask', 'Coinbase')[wallet == 0]
        self.extension_path = os.path.abspath('assets/{}.crx'.format(wallet_extension))
        self.driver = self.webdriver()  # Start new webdriver.

    """ Webdriver
    * Builds the web driver
    @Returns: The app webdriver
    """
    def webdriver(self) -> webdriver:
        # Configure options for Chrome since that's what we are using.
        options = webdriver.ChromeOptions()
        options.add_extension(self.extension_path)
        options.add_argument("log-level=3")  # No logs is printed.
        options.add_argument("--mute-audio")  # Audio is muted.
        # Set webdriver language to English. - 2 methods.
        options.add_argument("--lang=en-US")  
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        driver = webdriver.Chrome(service=Service(  # DeprecationWarning using
            self.webdriver_path), options=options)  # executable_path.

        # Maximize window to reach all elements.
        driver.maximize_window()  

        return driver

    """ Clickable
    * Checks for element interaction
    @Params:
    - element: The element to click
    """
    def clickable(self, element: str) -> None:
        try:
            WDW(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, element))).click()

        # Some buttons need to be visible to be clickable, JavaScript can bypass this.
        except Exception:
            self.driver.execute_script('arguments[0].click();', self.visible(element))

    """ Visible
    * Checks the visibility of an element
    @Params:
    - element: The element to click
    """
    def visible(self, element: str):
        return WDW(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, element)))

    """ Send keys
    * Send key input to elements
    @Params:
    - element: The element to send values to
    - keys: The input to send to the element
    """
    def send_keys(self, element: str, keys: str) -> None:
        try:
            self.visible(element).send_keys(keys)

        # Some elements are not visible but are present.
        except Exception:  
            WDW(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, element))).send_keys(keys)

    """ Send date
    * Send a date (DD-MM-YYYY HH:MM) to a date input by clicking on it.
    @Params:
    - element: The element to send a date to
    - keys: The input to send to the element
    """
    def send_date(self, element: str, keys: str) -> None:
        keys = keys.split('-') if '-' in keys else [keys]
        keys = [keys[1], keys[0], keys[2]] if len(keys) > 1 else keys

        for part in range(len(keys) - 1 if keys[len(keys) - 1]  # Compare years
                == str(dt.now().year) else len(keys)):  # To count clicks.
            self.clickable(element)  # Click first on the element.
            self.send_keys(element, keys[part])  # Then send it the date.

    """ Clear element
    * Clears the values of the element
    @Params:
    - element: The element to clear
    """
    def clear_text(self, element) -> None:
        self.clickable(element)

        # Note: change with 'darwin' if it's not working on MacOS.
        control = Keys.COMMAND if os.name == 'posix' else Keys.CONTROL
        webdriver.ActionChains(self.driver).key_down(control).perform()
        webdriver.ActionChains(self.driver).send_keys('a').perform()
        webdriver.ActionChains(self.driver).key_up(control).perform()

    """ Window handles
    * Checks and waits for specifit tabs
    @Params:
    - window_number: The window to move to
    """
    def window_handles(self, window_number: int) -> None:
        WDW(self.driver, 30).until(lambda _: len(self.driver.window_handles) > window_number)

        # Switch to the tab.
        self.driver.switch_to.window(self.driver.window_handles[window_number])


""" OpenSea
* The OpenSea controller
"""
class OpenSea:

    def __init__(self, wallet: int, password: str, recovery_phrase: str) -> None:
        """Get the password and the recovery_phrase from the text file."""
        self.recovery_phrase = recovery_phrase  # Get the MetaMask phrase.
        self.password = password  # Get the new/same password.
        self.login_url = 'https://opensea.io/login?referrer=%2Fasset%2Fcreate'
        self.create_url = 'https://opensea.io/asset/create'  # OpenSea URLs.

    def wallet_login(self) -> None:
        """Login to the appropriate wallet extension."""
        if wallet == 0: self.coinbase_login()
        else: self.metamask_login()

    def coinbase_login(self) -> None:
        """Login to the Coinbase extension."""
        try:  # Try to login to the Coinbase extension.
            print('Login to Coinbase.', end=' ')
            web.window_handles(0)  # Switch to the Coinbase extension tab.
            web.driver.refresh()  # Reload the page to prevent a blank page.
            # Click on the "I have a wallet" button.
            web.clickable('//*[@data-testid="btn-import-existing-wallet"]')
            # Click on the "Enter recover phrase" button.
            web.clickable('//*[@data-testid="btn-import-recovery-phrase"]')
            # Input the recovery phase
            web.send_keys('//*[@data-testid="seed-phrase-input"]', self.recovery_phrase)
            # Click on "Import wallet" button
            web.clickable('//*[@data-testid="btn-import-wallet"]')
            # Set password
            web.send_keys('//*[@data-testid="setPassword"]', self.password)
            # Verify password
            web.send_keys('//*[@data-testid="setPasswordVerify"]', self.password)
            # Agree to terms and conditions
            web.clickable('//*[@data-testid="terms-and-privacy-policy-parent"]')
            # Click on the "Submit" button
            web.clickable('//*[@data-testid="btn-password-continue"]')

        except Exception:  # Failed - a web element is not accessible.
            print(f'{red}Login to Coinbase failed, retrying...')
            self.coinbase_login()

    def metamask_login(self) -> None:
        """Login to the MetaMask extension."""
        try:  # Try to login to the MetaMask extension.
            print('Login to MetaMask.', end=' ')
            web.window_handles(0)  # Switch to the MetaMask extension tab.
            web.driver.refresh()  # Reload the page to prevent a blank page.
            # Click on the "Start" button.
            web.clickable('//*[@class="welcome-page"]/button')
            # Click on the "Import wallet" button.
            web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            # Click on the "I agree" button.
            web.clickable('//footer/button[2]')
            # Input the recovery phrase.
            web.send_keys('//input[position()=1]', self.recovery_phrase)
            # Input a new password or the same password of your account.
            web.send_keys('//*[@id="password"]', self.password)
            web.send_keys('//*[@id="confirm-password"]', self.password)
            # Click on the "I have read and agree to the..." checkbox.
            web.clickable('(//*[@role="checkbox"])[2]')
            # Click on the "Import" button.
            web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            # Wait until the login worked and click on the "All done" button".
            web.visible('//*[contains(@class, "emoji")][position()=1]')
            web.clickable('//*[contains(@class, "btn-primary")][position()=1]')
            print(f'{green}Logged to MetaMask.')

        except Exception:  # Failed - a web element is not accessible.
            print(f'{red}Login to MetaMask failed, retrying...')
            self.metamask_login()

    def sign_contract(self) -> None:
        """Sign a Wallet contract to login to OpenSea."""
        if wallet == 0: self.coinbase_contract()
        else: self.metamask_contract()

    def coinbase_contract(self) -> None:
        """Sign a Coinbase contract to login to OpenSea."""
        # Switch to the Coinbase pop up tab.
        web.window_handles(2)
        # Click on the "Sign" button - Make a contract link.
        web.clickable('//*[@data-testid="sign-message"]')
        try:  # Wait until the Coinbase pop up is closed.
            WDW(web.driver, 10).until(EC.number_of_windows_to_be(2))
        except TE:
            self.coinbase_contract()  # Sign the contract a second time.
        web.window_handles(1)  # Switch back to the OpenSea tab.

    def metamask_contract(self) -> None:
        """Sign a MetaMask contract to login to OpenSea."""
        if structure.blockchain == 'Polygon':
            web.clickable('//div[@data-testid="Panel"][last()]/div/div'
                          '/div/div/button')  # "Sign" button.

        web.window_handles(2)  # Switch to the MetaMask pop up tab.
        # Click on the "Sign" button - Make a contract link.
        web.clickable('//*[contains(@class, "button btn-secondary")]')
        try:  # Wait until the MetaMask pop up is closed.
            WDW(web.driver, 10).until(EC.number_of_windows_to_be(2))
        except TE:
            self.metamask_contract()  # Sign the contract a second time.
        web.window_handles(1)  # Switch back to the OpenSea tab.

    def start_coin_wallet(self) -> None:
        """Start the Coinbase wallet process."""
        try:
            # Click on the "Coinbase wallet" button in list of wallets.
            web.clickable('//*[contains(text(), "Coinbase Wallet")]/../..')
            # Switch to the new pop-up tab
            web.window_handles(2)
            # Click on the "Connect" button.
            web.clickable('//*[@data-testid="allow-authorize-button"]')
            # Switch to the new Wallet pop up tab.
            # WDW(web.driver, 5)
            web.window_handles(3)
            # Cick on the "Sign" button.
            web.clickable('//*[@data-testid="sign-message"]')

        except Exception:  #Could not start the wallet
            print(f'{red}Starting the Coinbase wallet failed. Retrying.')
            web.window_handles(1)  # Switch to the main (data:,) tab.
            web.driver.refresh()  # Reload the page (is the login failed?).
            self.opensea_login()  # Retry everything.

    def start_meta_wallet(self) -> None:
        """Start the MetaMask wallet process."""
        try:
            # Click on the "MetaMask" button in list of wallets.
            web.clickable('//*[contains(text(), "MetaMask")]/../..')
            # Switch to the new pop-up tab
            web.window_handles(2)
            # Click on the "Next" button.
            web.clickable('//*[@class="button btn-primary"]')
            # Click on the "Connect" button.
            web.clickable('//*[contains(@class, "button btn-primary")]')
            web.window_handles(2)  # Switch to the MetaMask pop up tab.
            self.metamask_contract()  # Sign the contract.

        except Exception:
            print(f'{red}Starting the wallet failed. Retrying.')
            web.window_handles(1)  # Switch to the main (data:,) tab.
            web.driver.refresh()  # Reload the page (is the login failed?).
            self.opensea_login()  # Retry everything.

    def opensea_login(self) -> None:
        """Login to OpenSea using the chosen wallet."""
        try:  # Try to login to the OpenSea using MetaMask.
            print('Login to OpenSea.', end=' ')
            web.window_handles(1)  # Switch to the main (data:,) tab.
            web.driver.get(self.login_url)  # Go to the OpenSea login URL.
            # Click on the "Show more options" button.
            web.clickable('//button[contains(@class, "show-more")]')

            # Login to the wallet
            if wallet == 0:
                self.start_coin_wallet()
            else:
                self.start_meta_wallet()

            # Check if the login worked.
            web.window_handles(1)  # Switch back to the OpenSea tab.
            WDW(web.driver, 15).until(EC.url_to_be(self.create_url))
            print(f'{green}Logged to OpenSea.\n')
        except Exception:  # The contract failed.
            try:
                web.window_handles(1)  # Switch back to the OpenSea tab.
                web.window_handles(2)  # Switch to the MetaMask pop up tab.
                self.sign_contract()  # Sign the contract.
                # Check if the login worked.
                WDW(web.driver, 15).until(EC.url_to_be(self.create_url))
                print(f'{green}Logged to OpenSea.\n')
            except Exception:
                print(f'{red}Login to OpenSea failed. Retrying.')
                web.window_handles(1)  # Switch back to the OpenSea tab.
                web.driver.refresh()  # Reload the page (is the login failed?).
                self.opensea_login()  # Retry everything.


    def check_for_captcha(self) -> None:
        # Check to wait for captcha
        if web.visible('//h4[contains(text(), "Almost done")]'):

            # Look for the captcha ifrmae and switch to it
            try:
                time.sleep(2)
                iframes = web.driver.find_elements(by=By.TAG_NAME, value="iframe")
                web.driver.switch_to.frame(iframes[0])
                # print('Found iframe and switched to it')
            except Exception:
                print('| Could not find the captcha iframe')

            # Try to click the anchor
            try:
                web.clickable('//*[@id="recaptcha-anchor"]/div[1]')
                # print('Found anchor and clicked it')
            except Exception:
                print('| Could not find the anchor')

            # Solve the captcha
            print('| Captcha found, solve and press enter', end=' ')
            wait_response = str(input())


    def opensea_upload(self, number: int) -> bool:
        """Upload multiple NFTs automatically on OpenSea."""
        print(f'\nUploading NFT n°{number}/{reader.lenght_file}.')
        try:  # Go to the OpenSea create URL and input all datas of the NFT.
            web.driver.get(self.create_url + '?enable_supply=true')
            if isinstance(structure.file_path, list):
                if len(structure.file_path) == 2:
                    file_path = os.path.abspath(structure.file_path[0])
                    preview = os.path.abspath(structure.file_path[1])
            else:  # No preview file.
                file_path = os.path.abspath(structure.file_path)
            if not os.path.exists(file_path):  # Upload the NFT file.
                raise TE('File doesn\'t exist or path is incorrect.')
            if os.path.getsize(file_path) / (1024 ** 2) > 100:
                raise TE('File size must be less than 100 MegaBytes.')
            if os.path.splitext(file_path)[1][1:].lower() not in \
                ('jpg', 'jpeg', 'png', 'gif', 'svg', 'mp4',  # Check the file
                 'webm', 'mp3', 'wav', 'ogg', 'glb', 'gltf'):  # extensions.
                raise TE('The file extension is not supported on OpenSea.')
            structure.is_empty('//*[@id="media"]', file_path)
            if os.path.splitext(file_path)[1][1:].lower() in \
                    ('mp4', 'webm', 'mp3', 'wav', 'ogg', 'glb', 'gltf'):
                if not os.path.exists(preview):  # Upload the NFT file.
                    raise TE('File doesn\'t exist or path is incorrect.')
                if os.path.getsize(preview) / (1024 ** 2) > 100:
                    raise TE('File size must be less than 100 MegaBytes.')
                structure.is_empty('//input[@name="preview"]', preview)
            # Input NFT name.
            if structure.is_empty('//*[@id="name"]', structure.nft_name):
                raise TE('The NFT name is missing.')
            # Input external link.
            structure.is_empty('//*[@id="external_link"]', structure.link)
            # Input description.
            structure.is_empty('//*[@id="description"]', structure.description)
            if not structure.is_empty(  # Input collection and select it.
                    '//form/div[5]/div/div[2]/input', structure.collection):
                try:  # Try to click on the collection button.
                    collection = ('//span[contains(text(), "'
                                  f'{structure.collection}")]/../..')
                    web.visible(collection)  # Check that the collection span
                    web.clickable(collection)  # is visible and click on it.
                except Exception:  # If collection doesn't exist.
                    raise TE('Collection doesn\'t exist or can\'t be found.')
            datas = [structure.properties, structure.levels, structure.stats]
            for index in range(len(datas)):  # Add properties, levels & stats.
                if not len(datas[index]) > 0:  # Check if data is not empty.
                    continue  # Pass this data because it's empty or null.
                # Change element from a list of strings to a list of lists.
                if not isinstance(datas[index][0], list):
                    datas[index] = [datas[index]]  # Target maybe useless.
                web.clickable(  # Click on "+" button to open the pop up.
                    f'//form/section/div[{index + 1}]/div/div[2]/button')
                number_ = 0
                for data in datas[index]:
                    if number_ > 0:  # If there are more than 1 element.
                        # Click on "Add more" button.
                        web.clickable('//div[@role="dialog"]/section/button')
                    number_ += 1  # Increase number to add more element.
                    web.send_keys(  # Input values in the inputs.
                        f'/html/body/div[{index + 2}]/div/div/div/section/tabl'
                        f'e/tbody/tr[{number_}]/td[1]/div/div/input', data[0])
                    for rank in [3, 2]:  # Input third and second values.
                        if len(data) == 3 or rank == 2:  # 1 or 2 loops.
                            actual_element = f'/html/body/div[{index + 2}]' + \
                                '/div/div/div/section/table/tbody/' + \
                                f'tr[{number_}]/td[{rank}]/div/div/input'
                            web.clear_text(actual_element)  # Default text.
                            web.send_keys(actual_element, data[rank - 1])
                web.clickable('//footer/button')  # Click on the "Save" button.
            # Click on the "Unlockable Content" switch if it's true.
            if isinstance(structure.unlockable_content, list):  # If not False.
                if len(structure.unlockable_content) > 0:  # Not an empty list.
                    if isinstance(structure.unlockable_content[0], bool):
                        if structure.unlockable_content[0]:  # If True.
                            web.send_keys('//*[@id="unlockable-content-toggle'
                                          '"]', Keys.ENTER)  # Toggle button.
                            web.send_keys(  # Input the unlockable content.
                                '//div[contains(@class, "unlockable")]/'
                                'textarea', structure.unlockable_content[1])
            # Click on the "Explicit & Sensitive Content" switch if it's true.
            if structure.explicit_and_sensitive_content != '':  # Not empty.
                if isinstance(structure.explicit_and_sensitive_content, bool):
                    if structure.explicit_and_sensitive_content:  # True.
                        web.send_keys('//*[@id="explicit-content-toggle"]',
                                      Keys.ENTER)  # Toggle button.
            # Set number of supplies if it's not an empty string.
            if structure.supply != '' and 'supply=' in web.driver.current_url:
                if isinstance(structure.supply, int):  # Integer.
                    if structure.supply > 1:  # Set supplies deleting default
                        web.send_keys('//*[@id="supply"]',  # supply (= 1).
                                      f'{Keys.BACKSPACE}{structure.supply}')
            else:  # This is important for the sale part.
                structure.supply = 1
            # Set Blockchain if it's different from "Ethereum".
            if structure.blockchain != '':  # If it's not an empty string.
                if web.visible('//*[@id="chain"]').get_attribute('value') \
                        != structure.blockchain:  # Compare to the span text.
                    try:  # Try to select the Blockchain.
                        web.clickable('//*[@id="chain"]/..')  # Open the sheet.
                        web.clickable('//span[contains(text(), '
                                      f'"{structure.blockchain}")]/../..')
                    except Exception:  # Blockchain is unknown.
                        raise TE('Blockchain is unknown or badly written.')
            else:  # This is important for the sale part.
                structure.blockchain = 'Ethereum'
            web.clickable('(//div[contains(@class, "submit")])'  # Click on the
                          '[position()=1]/div/span/button')  # "Create" button.
            # Check for captchas
            self.check_for_captcha()

            # Verify upload
            WDW(web.driver, 60).until(lambda _: web.driver.current_url != self.create_url + '?enable_supply=true')
            print(f'{green}| Uploaded.{reset}')
            if 2 not in structure.action:  # Save the data for future upload.
                structure.save_nft(web.driver.current_url, structure.nft_name)
            return True  # If it perfectly worked.
        except Exception as error:  # An element is not reachable.
            print(f'{red}An error occured. {error}')
            return False  # If it failed.

    def opensea_sale(self, number: int, date: str = '%d-%m-%Y %H:%M') -> None:
        """Set a price for the NFT and sell it."""
        print(f'\nSale of the NFT n°{number}/{len(structure.file)}.', end=' ')
        try:  # Try to sell the NFT with different types and methods.
            if 2 in structure.action and 1 not in structure.action:
                web.driver.get(structure.nft_url + '/sell')  # NFT sale page.
            else:  # The NFT has just been uploaded.
                web.driver.get(web.driver.current_url + '/sell')  # Sale page.
            if not isinstance(structure.supply, int):
                raise TE('The supply number must be an integer.')
            elif structure.supply == 1 and structure.blockchain == 'Ethereum':
                if not isinstance(structure.price, int) and not \
                        isinstance(structure.price, float):
                    raise TE('The price must be an integer or a float.')
                if 'Timed' in str(structure.type):  # Timed Auction.
                    # Click on the "Timed Auction" button.
                    web.clickable('//i[@value="timelapse"]/../..')
                    if isinstance(structure.method, list):  # If it's a list.
                        if len(structure.method) == 2:  # [method, price]
                            if not isinstance(structure.method[1], int) and \
                                    not isinstance(structure.method[1], float):
                                raise TE('Prices must be integer or float.')
                            if 'declining' in str(structure.method[0]):
                                web.clickable(  # Click on the method button.
                                    '//*[@id="main"]/div/div/div[3]/div/div[2]'
                                    '/div/div[1]/form/div[2]/div/div[2]')
                                # Click on the "Sell with declining price"
                                web.clickable('//*[@role="tooltip"]'  # button.
                                              '/div/div/ul/li/button')
                                if structure.method[1] < structure.price:
                                    web.send_keys(  # Input the ending price.
                                        '//*[@name="endingPrice"]', format(
                                            structure.method[1], '.8f'))
                                else:  # Ending price is higher than the price.
                                    raise TE('The ending price must be higher'
                                             ' than the starting price.')
                            elif 'highest' in str(structure.method[0]):
                                if structure.method[1] > 0:  # Reserve price.
                                    if structure.method[1] <= 1 or structure \
                                            .method[1] < structure.price:
                                        raise TE('Reserve price must be higher'
                                                 'than 1 WETH and the price.')
                                    # Click on the "More option" button.
                                    web.clickable('//button[contains(@class, '
                                                  '"more-options")]')
                                    # Click on the "Include reserve price"
                                    web.send_keys(  # toggle switch button.
                                        '//*[@role="switch"]', Keys.ENTER)
                                    web.send_keys(  # Input the reserve price.
                                        '//*[@name="reservePrice"]',
                                        format(structure.method[1], '.8f'))
                            else:  # Not a Declining price or a Highest bidder.
                                raise TE('Unknown method for Timed Auction.')
            elif structure.supply > 1:  # Set a quantity of supply.
                if isinstance(structure.quantity, int):  # Quantity is int.
                    if structure.quantity <= structure.supply:
                        web.send_keys('//*[@id="quantity"]',  # Supply to sell.
                                      f'{Keys.BACKSPACE}{structure.quantity}')
                    else:  # Quantity number is higher that supply number.
                        raise TE('Quantity must be less or equal to supplies.')
            elif structure.blockchain not in ('Ethereum', 'Polygon'):
                raise TE('Blockchain is unknown or badly written.')
            if 'Timed' not in str(structure.type):  # Set a specific buyer.
                if isinstance(structure.specific_buyer, list):
                    if len(structure.specific_buyer) == 2:
                        if isinstance(structure.specific_buyer[0], bool):
                            if structure.specific_buyer[0]:
                                # Click on the "More option" button.
                                web.clickable('//button[contains(@cla'
                                              'ss, "more-options")]')
                                # Click on "Reserve for specific buyer".
                                web.send_keys('(//*[@role="switch"])[last()]',
                                              Keys.ENTER)
                                web.send_keys(  # Input a specific buyer.
                                    '//*[@id="reservedBuyerAddressOrEns'
                                    'Name"]', structure.specific_buyer[1])
            web.send_keys('//*[@name="price"]', format(structure.price, '.8f'))
            if isinstance(structure.duration, str):  # Transform to a list.
                structure.duration = [structure.duration]
            if isinstance(structure.duration, list):  # List of 1 or 2 values.
                if len(structure.duration) == 2:  # From {date} to {date}.
                    from datetime import datetime as dt  # Default import.
                    # Check if duration is less than 6 months.
                    if (dt.strptime(structure.duration[1], date) -
                            dt.strptime(structure.duration[0], date
                                        )).total_seconds() / 60 > 262146:
                        raise TE('Duration must be less than 6 months.')
                    # Check if starting date has passed.
                    if dt.strptime(dt.strftime(dt.now(), date), date) \
                            > dt.strptime(structure.duration[0], date):
                        raise TE('Starting date has passed.')
                    # Split the date and the time.
                    start_date, start_time = structure.duration[0].split(' ')
                    end_date, end_time = structure.duration[1].split(' ')
                    web.clickable('//*[@id="duration"]')  # Date button.
                    web.visible(  # Scroll to the pop up frame of the date.
                        '//*[@role="dialog"]').location_once_scrolled_into_view
                    web.send_date('//*[@role="dialog"]'  # Ending date.
                                  '/div[2]/div[2]/div/div[2]/input', end_date)
                    web.send_date('//*[@role="dialog"]/'  # Starting date.
                                  'div[2]/div[1]/div/div[2]/input', start_date)
                    web.send_date('//*[@id="end-time"]', end_time)  # End date.
                    web.send_date('//*[@id="start-time"]',  # Starting date +
                                  f'{start_time}{Keys.ENTER}')  # close frame.
                elif len(structure.duration) == 1:  # In {n} days/week/months.
                    if structure.duration[0] == '':  # Duration not specified.
                        raise TE('Duration must be specified.')
                    if web.visible('//*[@id="duration"]/div[2]').text \
                            != structure.duration[0]:  # Not default.
                        web.clickable('//*[@id="duration"]')  # Date button.
                        web.clickable('//*[@role="dialog"]'  # Duration Range
                                      '/div[1]/div/div[2]/input')  # sheet.
                        web.clickable('//span[contains(text(), '   # Date span.
                                      f'"{structure.duration[0]}")]/../..')
                        web.send_keys('//*[@role="dialog"]', Keys.ENTER)
            try:  # Click on the "Complete listing" (submit) button.
                web.clickable('//button[@type="submit"]')
            except Exception:  # An unknown error has occured.
                raise TE('The submit button cannot be clicked.')

            try:  # Polygon blockchain requires a click on a button.
                self.sign_contract() # Sign the contract.
            except Exception:  # No deposit or an unknown error occured.
                raise TE('You need to make a deposit before proceeding'
                         ' to listing of your NFTs.')
            web.window_handles(1)  # Switch back to the OpenSea tab.
            try:  # Wait until the NFT is listed.
                web.visible('//header/h4')  # "Your NFT is listed!".
                print(f'{green}NFT put up for sale.')
            except Exception:  # An error occured while listing the NFT.
                raise TE('The NFT is not listed.')
        except Exception as error:  # Failed, an error has occured.
            print(f'{red}NFT sale cancelled. {error}')

    def opensea_remove(self, number: int) -> None:
        """Remove the NFT"""
        print(f'\nDeleting NFT n°{number}/{len(structure.file)}.')
        
        web.driver.get(structure.nft_url)  # Edit url
        try:  # Try to delete the NFT.
            edit_button = '//a[contains(text(), "Edit")]' # The edit element

            # Check for NFT
            try:
                WDW(web.driver, 2).until(EC.visibility_of_element_located((By.XPATH, edit_button)))
            except Exception:  # An error occured while looking for edit
                raise TE('-NFT does not exist or did not load')

            # web.driver.refresh()  # Reload the page to prevent a blank page.
            web.clickable(edit_button)  # Click Edit.
            web.clickable('//button[contains(text(), "Delete item")]')  # Click Delete Item.
            web.visible('//*[contains(text(), "Are you sure you want to delete this item? ")]')
            web.clickable('//div[@class="Overlayreact__Overlay-sc-1yn7g51-0 ebMEfa"]/div/div/footer/div/button')
            web.visible('//span[contains(text(), "Deleted! Changes will take a minute to reflect.")]')  # Wait for deletion.
            print('| Deleted.')

        except Exception as error: # Faled, an error has occured
            print(f'{red}| Counld not remove the NFT. {error}')


# App Utilities
# ---------------------------------------------

""" Read file
* Reads the content of a file.  It will create and saves input 
* if the files does not exist
@Params:
- file_: The file to reaad/save to
- question: The prompt for input
@Returns: The file or prompt input value.
"""
def read_file(file_: str, question: str) -> str:
    if not os.path.isfile(f'assets/{file_}.txt'):
        open(f'assets/{file_}.txt', 'a')  # Create a file if it doesn't exist.

    with open(f'assets/{file_}.txt', 'r+', encoding='utf-8') as file:
        text = file.read()

        # Check for an empty file
        if text == '':  
            text = input(question)  # Ask the question.
            if input(f'Do you want to save your {file_} in a text file? (y/n) ').lower() != 'y':
                print(f'{yellow}Not saved.')
            else:
                file.write(text)
                print(f'{green}Saved.')

        return text

""" Perform action
* Suggests what actions are available to the user
"""
def perform_action() -> list:
    """Suggest multiple actions to the user."""
    while True:
        [print(string) for string in [
            f'{yellow}\nChoose an action to perform:{reset}',
            '1 - Upload and Sell NFTs',
            '2 - Upload NFTs only', 
            '3 - Sell NFTs only',
            '4 - Delete exsiting NFTs']]
        number = input('Action number: ')

        # Check if answer is a number.
        if number.isdigit():  
            if int(number) > 0 and int(number) < 5:
                return [[1, 2,], [1], [2], [3]][int(number) - 1]

        print(f'{red}You must choose an option from the list.')
        return perform_action()

""" Choose wallet
* Choose the wallet type you want to use
"""
def choose_wallet() -> int:
    while True:
        [print(string) for string in [
            f'{yellow}\nChoose which wallet you want to use:{reset}',
            '1 - Coinbase Wallet',
            '2 - MetaMask Wallet']]
        number = input('Choose a wallet: ')

        # Check if the anser is within range.
        if number.isdigit():  
            if int(number) > 0 and int(number) < 3:
                return int(number) - 1

        print(f'{red}You must choose an option from the list.')
        return choose_wallet()

""" Date file
* Read the data folders and extract JSON, CSV and XLSX files
"""
def data_file() -> str:
    """Read the data folder and extract JSON, CSV and XLSX files."""
    while True:
        file_number = 0
        files_list = []

        print(f'{yellow}\nChoose your file:{reset}\n0 - Browse a file on PC.')

        # Files of the data folder.
        for files in [glob(f'data/{extension}') for extension in ['*.json', '*.csv', '*.xlsx']]:
            for file in files:
                file_number += 1
                files_list.append(file)
                print(f'{file_number} - {os.path.abspath(file)}')

        # Files of the data sub folders
        for files in [glob(f'data/*/{extension}') for extension in ['*.json', '*.csv', '*.xlsx']]:
            for file in files:
                if 'Templates' not in file:
                    file_number += 1
                    files_list.append(file)
                    print(f'{file_number} - {os.path.abspath(file)}')

        answer = input('File number: ')

        cls()  # Clear console.

        # Check if answer is a number.
        if not answer.isdigit():  
            print(f'{red}Answer must be an integer.')

        # Browse a file on PC.
        elif int(answer) == 0:  
            print(f'{yellow}Browsing on your computer...')
            from tkinter import Tk  # Tkinter module: pip install tk
            from tkinter.filedialog import askopenfilename
            Tk().withdraw()  # Hide Tkinter tab.
            return askopenfilename(filetypes=[('', '.json .csv .xlsx')])

        # Return file paths.
        elif int(answer) <= len(files_list):
            return files_list[int(answer) - 1] 

        print(f'{red}File doesn\'t exist.')


""" Clear
* Clears the console
"""
def cls() -> None:
    """Clear console function."""
    # Clear console for Windows using 'cls' and Linux & Mac using 'clear'.
    os.system('cls' if os.name == 'nt' else 'clear')


""" Exit with message
@Params:
- message: The message to display with exiting
"""
def exit(message: str = '') -> None:
    """Stop running the program using the sys module."""
    import sys
    sys.exit(f'\n{red}{message}')


if __name__ == '__main__':

    cls()  # Clear console.

    print(f'{green}Time to upload/sell/delete them NTFs\n')

    input('\nPRESS [ENTER] TO CONTINUE. ')
    cls()  # Clear console.

    print(f'{green}Lets get started!!')

    # Choose what wallet you want to use
    wallet = choose_wallet()  # Which wallet to use

    # Init the OpenSea class and send the password and the recovery phrase.
    login_prefix = ('meta', 'coin')[wallet == 0]
    wallet_name = ("MetaMask", 'Coinbase')[wallet == 0]

    # Setup
    opensea = OpenSea(wallet,
        read_file('{}_password'.format(login_prefix), '\nWhat is your {} password? '.format(wallet_name)), 
        read_file('{}_recovery_phrase'.format(login_prefix), '\nWhat is your {} recovery phrase? '.format(wallet_name)))
    action = perform_action()  # What the user wants to do.
    reader = Reader(data_file())  # Ask for a file and read it.
    structure = Structure(action) 
    web = Webdriver(wallet)  # Start a new webdriver and init its methods.

    # Start Opensea
    opensea.wallet_login()  # Log into wallets.
    opensea.opensea_login()  # Connect to OpenSea.

    for nft_number in range(reader.lenght_file):
        structure.get_data(nft_number)  # Structure the data of the NFT.

        # Move on to the next NFT if it has alraedy been completed
        if 1 in action and structure.nft_name in structure.completed:
            print(f'NFT n°{nft_number} has alraedy been uploaded.')
        else:
            upload = None  # Prevent Undefined value error.
            if 1 in action:  # 1 = Upload. If user wants to upload the NFT.
                upload = opensea.opensea_upload(nft_number + 1)  # Upload the NFT.
            if 2 in action:  # 2 - Sale. If user wants to sell the NFT.
                if 1 in action and not upload:  # Do not upload the NFT because of
                    continue  # a user choice or a failure of the upload.
                elif isinstance(structure.price, int) or \
                        isinstance(structure.price, float):
                    if structure.price > 0:  # If price has been defined.
                        opensea.opensea_sale(nft_number + 1)  # Sell NFT.
            if 3 in action:  # 4 - Delete.  Delete NFTS from Opensea.
                opensea.opensea_remove(nft_number + 1)  # Remove the NFT


    web.driver.quit()  # Stop the webdriver.
    print(f'\n{green}All done! Your NFTs have been taken care of.')
