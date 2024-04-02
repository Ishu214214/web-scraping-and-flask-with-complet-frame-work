from flask import Flask ,render_template ,flash ,request ,session
import time
import multiprocessing
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
import threading

manager = multiprocessing.Manager()

def hower_image(src_list ,driver):
    actions = ActionChains(driver)

    for i in range (0,len(src_list)):
        element=driver.find_element("xpath",src_list[i])
        driver.execute_script("arguments[0].scrollIntoView(true);", element) # this line extra shoud be added to scroll the list of image value
        actions.move_to_element(element).perform()


def make_data_formate_detail(detail_page_list ,all_image, stock_status_1 ,product_description_list,result_price_list ,result_name ,brand_name_2):
    update_array = {
                   'product_image':all_image , 'stock_status':stock_status_1 ,'description':product_description_list
                   , 'price':result_price_list , 'product_title':result_name,"brand":brand_name_2   }
    detail_page_list.append(update_array)


def make_data_formate(result_price_list ,produck_link_final , result_img , result_name ,status_dict ,results_list ,name):
    for i in range(0,len(produck_link_final)):
        status_dict= {
                    'product_title':result_name[i], 'product_image' :result_img[i] , 'price':result_price_list[i] ,'keyword':name,
                    'amazone_sku':produck_link_final[i]  }
        results_list.append(status_dict)


def detail_page_scrape(amazon_sku_featch_final , images_org  ,detail_page_list, result_price_list, result_name):
    final_link= "https://www.amazon.in/dp/" + amazon_sku_featch_final

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.get(final_link)
    soup= BeautifulSoup(driver.page_source ,'html.parser')

    all_image= manager.list()    # image list of the product
    src_list= manager.list()
    try:
        step_7= soup.find_all('li', class_= "a-spacing-small item imageThumbnail a-declarative")
        for i in range(0, len(step_7)):
            step_7_1 = step_7[i]
            step_7_2 = step_7_1.find('img')
            step_7_3 = step_7_2.attrs['src']
            xpath = f"//img[@src='{step_7_3}']"
            src_list.append(xpath)

        h1 = multiprocessing.Process( target=hower_image, args=(src_list ,driver  ))        # hower image call
        h1.start()
        h1.join()

        soup1= BeautifulSoup(driver.page_source ,'html.parser')
        driver.quit() # quit the browser

        a1=soup1.find('ul' ,class_="a-unordered-list a-nostyle a-horizontal list maintain-height")
        #print(a1)
        a2=a1.find_all('li')
        #print(a2)
        for i in range(0,len(a2)):
            #print("img gether")
            a3=a2[i]
            a4=a3.find('img')
            if a4:
                a4=a4.attrs['src']
                all_image.append(a4)
    except:
        all_image= images_org
        print('error in  try block')
    #print(all_image)

    #  stock status
    try:
        stock_status_1 =0
        step_5 =soup.find('span', class_='a-size-medium a-color-success')
        stock_status =(step_5.get_text()).strip()
        #print(stock_status)
        if stock_status:
            stock_status_1 = "in stock"
    except:
        stock_status_1 ="None"

    # product description
    product_description_list= manager.list()
    try:
        about_product =soup.find('div', id="feature-bullets")
        about_product_1 =about_product.find_all('li', class_ ="a-spacing-mini")
        for i in range(0,len(about_product_1)):
            org_text_product=(about_product_1[i]).get_text()
            product_description_list.append(org_text_product)
        #print(product_description_list)
    except:
        about_product =soup.find('div', id="productFactsDesktopExpander")
        #print(about_product)
        about_product_1 =about_product.find_all('li')#, class_ ="a-list-item a-size-base a-color-base")
        for i in range(0,len(about_product_1)):
            org_text_product=(about_product_1[i]).get_text()
            product_description_list.append(org_text_product)
        #print(product_description_list)

    # brand
    try:
        brand_name=soup.find('table', class_="a-normal a-spacing-micro")
        brand_name_1 =brand_name.find('span', class_="po-break-word")
        brand_name_2 = brand_name_1.get_text()
        brand_name_2 =brand_name_2.strip()
    except:
        brand_name_2= ""

    #  make date into formate
    d1 = multiprocessing.Process( target=make_data_formate_detail, args=(detail_page_list ,all_image, stock_status_1 ,product_description_list,result_price_list ,result_name ,brand_name_2))
    d1.start()
    d1.join()


def keyword_page_scrape(result_price_list, produck_link_final ,result_img , result_name ,name ,limit_value):
    final_link= "https://www.amazon.in/s?k=" + name

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.get(final_link)
    soup= BeautifulSoup(driver.page_source ,'html.parser')
    #time.sleep(1)
    driver.quit()

    """print("featch image link and title of the product ")"""
    product_page_1= soup.find('div', class_='s-main-slot s-result-list s-search-results sg-row')
    product_page_1_1 =product_page_1.find_all('img', class_='s-image' ,limit=limit_value)

    for i in range(1,len(product_page_1_1)):
        img_all_list= product_page_1_1[i]
        if img_all_list :
            result_img.append(img_all_list.attrs['src'])
            name_valadition= (img_all_list.attrs['alt']).replace('Sponsored Ad -', '')
            result_name.append(name_valadition)
    # print(result_img)
    # print(result_name)

    # sku
    try:
        product_sku= soup.find_all('div', class_='sg-col-20-of-24' ,limit= limit_value)
        #print(len(product_sku))
        for k in range(1,len(product_sku)):
            produck_link= product_sku[k]
            valide_sku =produck_link.attrs['data-asin']
            if valide_sku:
                produck_link_final.append( valide_sku )
        #print(produck_link_final)
        print("sku")
        #print(len(produck_link_final))
    except:
        print("not in sku")
        product_sku= soup.find_all('div', class_='sg-col-4-of-24')# limit used nahi ho  raha ha
        #print(len(product_sku))
        for k in range(1,(limit_value)):
            produck_link= product_sku[k]
            valide_sku =produck_link.attrs['data-asin']
            if valide_sku:
                produck_link_final.append( valide_sku )
        #print(produck_link_final)
        #print(len(produck_link_final))

    # price
    """print("scrape the price")"""
    product_page_price= soup.find_all('span', class_='a-price-whole' ,limit=limit_value)
            #print(len(product_page_price))
    for i in range(1 ,len(product_page_price)):
        product_page_price_1 =product_page_price[i]
        product_price_1 = product_page_price_1.get_text()
        product_price_1 = product_price_1.strip()
        product_price_1= (product_price_1.replace(',', ''))
        product_price_1= (product_price_1.replace(' ', ''))
        product_price_1= (product_price_1.replace('\n', ''))
        product_price_final= float(product_price_1)
        result_price_list.append(product_price_final)

app = Flask(_name_)

app.secret_key = 'the random string'

@app.get('/<menu>')
def single_converter(menu):
    try:
        valu_to_pass = int(menu)
        session["email_cheak"] = valu_to_pass + 1
        print("value pass")
    except:
        pass
    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            status_dict = manager.dict()
            result_price_list= manager.list()
            produck_link_final = manager.list()
            result_img = manager.list()
            result_name= manager.list()
            results_list =manager.list()
            detail_page_list =manager.list()

            time_start= time.time()

            limit_value=6             # get the value of limit from session
            user_email=session.get("email_cheak",None)
            if user_email:
                limit_value=user_email
                print("limit pass")
            else:
                print("value not pass default 6")

            m1 = multiprocessing.Process( target=keyword_page_scrape, args=(result_price_list ,produck_link_final , result_img , result_name ,name ,limit_value))
            m1.start()
            m1.join()
            m2 = multiprocessing.Process( target=make_data_formate, args=(result_price_list ,produck_link_final , result_img , result_name ,status_dict ,results_list ,name))
            m2.start()
            m2.join()

            scrape_time=(f'Time taken to scrap the product in second: {round(time.time() - time_start)}')

            time_scrape_data= time.time()
            t_list = []
            for k in range(0,len(produck_link_final)):
                m3 = threading.Thread( target=detail_page_scrape, args=(produck_link_final[k] ,result_img[k] ,detail_page_list ,result_price_list[k],result_name[k]))
                t_list.append(m3)
                m3.start()

                if len(t_list) == len(produck_link_final):
                    time.sleep(8)
                    for t_ in t_list:
                        t_.join()
                    t_list = []

            detail_time = (f'Time taken to scrap the detail in second: {round( time.time() - time_scrape_data)}')
            print(detail_time)

            return render_template('index.html'  ,all_data=list(results_list)  , all_data_detail=detail_page_list,scrape_time=scrape_time , detail_time=detail_time )
        else:
            flash('Plese re-enter the search')
            return render_template('index.html')

    return render_template('index.html')


if _name_ == '_main_':
    app.run(host='0.0.0.0' ,debug=True)