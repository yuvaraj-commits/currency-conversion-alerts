#%%
from selenium import webdriver
import telegram_send
import time
import datetime
import os
import pandas as pd
from datetime import datetime
import warnings
import pickle
from variables import os_name,url_value
import urllib.parse
import requests
warnings.filterwarnings("ignore")

def send_go_alert(conversion_rate_today,conversion_rate_yesterday):
    print('Current conversion rate is good at ' + str(conversion_rate_today))
    telegram_send.send(messages=["*"*10 + "sunway" + "*"*10])
    msg = 'Current conversion rate is good at ' + str(conversion_rate_today)
    telegram_send.send(messages=[msg])
    msg_2 = 'Yesterday conversion rate is ' + str(conversion_rate_yesterday)
    telegram_send.send(messages=[msg_2])
    telegram_send.send(messages=["PROCEED WITH TRANSFER!!!"])
    telegram_send.send(messages=["*"*30])


def send_no_go_alert(conversion_rate_today,conversion_rate_yesterday):
    telegram_send.send(messages=["*"*10 + "sunway" + "*"*10])
    telegram_send.send(messages=["NO GO!!"])
    telegram_send.send(messages=["Conversion rate Today and yesterday are : {0} , {1}".format(str(conversion_rate_today),str(conversion_rate_yesterday))])
    telegram_send.send(messages=["*"*30])


def send_both_conversion_rates(row):
    date_st= datetime.strptime(str(row.date.iloc[0]), '%Y%m%d').date().strftime('%B %d,%Y') 
    sunway_msg = 'Sunway : '+ str(row.sunway_conversion_rate.iloc[0])
    instarem_rate = 'Instarem : ' + str(row.instarem_conversion_rate.iloc[0])
    msg = '*'*10 + '\n' + date_st + '\n' + '-'*10 + '\n' + sunway_msg + '\n' + instarem_rate + '\n' + '*'*10
    telegram_send.send(messages = [msg])


def get_hash_key():
    if os.path.exists('support_lib.serialized'):
        with open('support_lib.serialized', 'rb') as handle:
            b = pickle.load(handle)
        return str(b['hash_key'])
    else:
        print('Access token missing.')
        raise

def send_conversion_rate_to_group(url,row):
    hash = get_hash_key()
    url = url.replace('<hash>',hash)
    date_st= datetime.strptime(str(row.date.iloc[0]), '%Y%m%d').date().strftime('%B %d,%Y') 
    sunway_msg = 'Sunway : '+ str(row.sunway_conversion_rate.iloc[0])
    instarem_rate = 'Instarem : ' + str(row.instarem_conversion_rate.iloc[0])
    msg = '*'*10 + '\n' + date_st + '\n' + '-'*10 + '\n' + sunway_msg + '\n' + instarem_rate + '\n' + '*'*10
    #telegram_send.send(messages = [msg])
    encoded = urllib.parse.quote(msg)
    #print(encoded)
    url = url.replace('<text>',encoded)
    #print(url)
    response = requests.get(url)
    if response.status_code!=200:
        print('unable to send message, something failed')
        raise



def fetch_conversion_rate(site = 'sunway'):
    try:
        if site == 'sunway':
            if os_name == 'mac':
                driver = webdriver.Chrome('./chromedrivers/mac/chromedriver')
            elif os_name == 'windows':
                driver = webdriver.Chrome('./chromedrivers/windows/chromedriver.exe')
            elif os_name == 'linux':
                driver = webdriver.Chrome('./chromedrivers/linux/chromedriver')
            driver.get('https://sunwaymoney.com')
            select = driver.find_element_by_xpath('//*[@id="selectCurrencyContainer"]/div[2]')
            time.sleep(2)
            select.click()
            #time.sleep(0.25)
            searchword = driver.find_element_by_id('searchCurrencyListInput')
            #time.sleep(1)
            searchword.send_keys('INR')
            time.sleep(1)
            #inr = driver.find_element_by_xpath('//*[@id="currencyList"]/li[13]/a')
            inr = driver.find_element_by_xpath('//*[@id="currencyList"]/li[12]') #updated site
            time.sleep(2)
            inr.click()
            # Fetch The Rate
            time.sleep(1)
            inr = driver.find_element_by_xpath("//*[@id='currencyRate']")
            #driver.close()
            #inr = driver.find_element_by_class_name('currency__country-code')
            today_rate = str(inr.text)
            print('conversion rate of sunway today is : ' + today_rate)
            driver.quit()
            return today_rate

        if site == 'instarem':
            if os_name == 'mac':
                driver = webdriver.Chrome('./chromedrivers/mac/chromedriver')
            elif os_name == 'windows':
                driver = webdriver.Chrome('./chromedrivers/windows/chromedriver.exe')
            elif os_name == 'linux':
                driver = webdriver.Chrome('./chromedrivers/linux/chromedriver')
            driver.get('https://instarem.com/en-in/')
            source_currency_amount = driver.find_element_by_id('gross_source_amount')
            source_currency_amount.clear()
            #time.sleep(2)
            source_currency_amount.send_keys('1')
            source_currency_name = driver.find_element_by_xpath('//*[@id="dropdownMenuButtonSource"]/span[1]')
            source_currency_name.click()
            time.sleep(1)
            source_currency_name = driver.find_element_by_id('sourch_search')
            #time.sleep(1)
            source_currency_name.send_keys('MYR')
            time.sleep(1)
            source_currency_name = driver.find_element_by_xpath('//*[@id="source-dropdown"]/div/ul/li/a/span[1]')
            #time.sleep(1)
            source_currency_name.click()
            destination_currency_name = driver.find_element_by_xpath('//*[@id="dropdownMenuButtonDestination"]')
            destination_currency_name.click()
            #time.sleep(1)
            destination_currency_name = driver.find_element_by_id('dest_search')
            time.sleep(1)
            destination_currency_name.send_keys('INR')
            #time.sleep(1)
            source_currency_name = driver.find_element_by_xpath('//*[@id="destination-dropdown"]/div/ul/li/a/span[1]')
            time.sleep(1)
            source_currency_name.click()
            time.sleep(1.5)
            conversion_rate = driver.find_element_by_xpath('//*[@id="unit_calculation"]')
            today_rate = conversion_rate.text.split('=')[1].replace('INR','').strip()
            time.sleep(1)
            print('conversion rate of instarem today is : ' + today_rate)
            driver.quit()
            return today_rate

    except Exception as e:
        print(e)
        print('Failed')
        driver.quit()
        #driver.close()




def main(history_retention=10):
    try:
        start_t = time.time()

        history_retention = history_retention
        rate_today_sunway =  fetch_conversion_rate(site = 'sunway')        #17.4656
        rate_today_instarem =  fetch_conversion_rate(site = 'instarem')        #17.4656
        timestamp = datetime.now().strftime('%Y%m%d')

        # Write todays rate to file
        try:
            if os.path.exists('./conversion_hist.csv'):
                with open('conversion_hist.csv', 'w') as write:
                    write.writelines('date,sunway_conversion_rate,instarem_conversion_rate\n')
                    write.writelines(str(timestamp) + ',' + \
                        str(rate_today_sunway) +  ',' +\
                            str(rate_today_instarem) + \
                                '\n')
            else:
                with open('conversion_hist.csv','a+') as append:
                        append.writelines(str(timestamp) + ',' + \
                        str(rate_today_sunway) + ',' +\
                            str(rate_today_instarem) + \
                                '\n')
        except Exception as e:
            print("Couldn't read the file.")
            print(e)
            raise


       # Read from hist file
        try:
            dataframe = pd.read_csv('conversion_hist.csv',dtype=object)
            print(dataframe)
        except Exception as e:
            print("Couldn't read the file.")
            print(e)
            raise


        #Fetch top 2 rates :
        dataframe = dataframe.sort_values(by='date', ascending=False)
        dataframe = dataframe.drop_duplicates()
        total_entries = dataframe.shape[0]
        if total_entries<2:
            print('Enough Data not available to compare')
        else:
            dataframe_top_two = dataframe.head(2)

        #Format conversion_hist file:
        dataframe.head(history_retention).to_csv('conversion_hist.csv',index=False)

        #Send both conversion rates
        #send_both_conversion_rates(dataframe.head(1))  #For sending to an individual
        
        #Uncomment this line
        send_conversion_rate_to_group(url_value,dataframe.head(1))

        # # LOGIC to notify - Not required
        # if len(rates_dict_sorted_desc)>=2:
        #     yesterday_date,today_date = list(rates_dict_sorted_desc.keys())[0:2]
        #     today_rate,yesterday_rate = float(rates_dict_sorted_desc[yesterday_date]),float(rates_dict_sorted_desc[today_date])
        #     print(today_rate,yesterday_rate)
        #     if today_rate>yesterday_rate:
        #         print('GO!!')
        #         send_go_alert(today_rate,yesterday_rate)
        #     else:
        #         print('NO GO!!')
        #         send_no_go_alert(today_rate,yesterday_rate)
        # else:
        #     print('Enough history unavailable to take decision, Decision in next run')
        
        print(" Total time taken to process_data: %s seconds" % (time.time() - start_t))

    except Exception as e:
        print("Issue in code")
        print(e)
        raise



def test():
    try:

        rate_today_sunway =  fetch_conversion_rate(site = 'sunway')        #17.4656
        rate_today_instarem =  fetch_conversion_rate(site = 'instarem')        #17.4656
        timestamp = datetime.now().strftime('%Y%m%d')
        print(rate_today_sunway)
        print(rate_today_instarem)
    except Exception as e:
        print("Issue in code")
        print(e)
        raise



if __name__ == '__main__':
    main()
    #test()