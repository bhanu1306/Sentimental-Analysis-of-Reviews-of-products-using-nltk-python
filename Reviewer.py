from lxml import html
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tkinter as tk
from tkinter import ttk
import time
import re
import sys
from reportlab.lib.units import cm
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import *
from reportlab.graphics import renderPDF

root = tk.Tk()
gasin = tk.StringVar()
class MainClass:
    def __init__(self):
        global root
        topf = ttk.Frame(root, width=260, height=65, padding=(5,5,5,5))
        bottomf = ttk.Frame(root, width=260, height=65, padding=(5,5,5,5))
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        topf.grid(row=0, sticky="n")
        bottomf.grid(row=1, sticky="n")
        label = tk.Label(topf, text="Enter Product ID: ")
        label.grid(row=0, column=0, pady=15)
        entry = tk.Entry(topf, textvariable=gasin)
        entry.grid(row=0, column=1)
        root.winfo_toplevel().title("Reviewer")
        root.geometry("270x130")
        root.resizable(0, 0)
        btn = tk.Button(bottomf, text="Analyze", command=self.startAnalyze, bd=4)
        btn.grid(row=0, columnspan=110, pady=20)
        
        root.mainloop()

    def startAnalyze(self):
        global gasin
        asin  = str(gasin.get())
        root.destroy()
        start_time = time.time()
        u1 = 'https://www.amazon.in/product-reviews/'
        u2 = u1+asin

        para = '?sortBy=recent&reviewerType=all_reviews'
        u3 = u2+para
        amazon_url = u3

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        headers = {'User-Agent': user_agent}

        try:
            page = requests.get(amazon_url, headers = headers)
        except:
            print("Some error has occured!")
        try:
            parser = html.fromstring(page.content)
        except:
            parser = html.fromstring(page.content)

        xpath_but = '//*[@id="cm_cr-pagination_bar"]/ul/li[7]/a/text()'

        xpath_reviews = '//div[@data-hook="review"]'

        xpath_title   = './/a[@data-hook="review-title"]//text()'

        xpath_prod_name = '//*[@id="cm_cr-product_info"]/div/div[2]/div/div/div[2]/div[1]/h1/a/text()'

        xpath_body    = './/span[@data-hook="review-body"]//text()'
        but = parser.xpath(xpath_but)
        reviews = parser.xpath(xpath_reviews)
        if len(but) is not 0:
            r = int(but[0].replace(',', '')) + 1
        else:
            if len(reviews) is not 0:
                r = 2
            else:
                print("No review available for this product!")
                sys.exit()

        name = parser.xpath(xpath_prod_name)
        try:
            tt = name[0]
        except IndexError:
            raise Exception("Invalid Product Id")
        print(name[0])
        tt = re.sub('[\\/:"*?<>|$]+', '', name[0])
        print("Total no of pages.")
        print(r - 1)
        print("Now we can estimate the required time! It depends on your network...")
        print("The counting will go upto the total number of pages...")
        temp = amazon_url + '&pageNumber='

        pos = 0
        neg = 0
        sid = SentimentIntensityAnalyzer()
        ind = "compound"
        rc = 0
       
        
        for i in range(1, r):
            a_url = temp + str(i)
            print(i)
            try:
                page = requests.get(a_url, headers=headers, timeout=60)
            except:
                page = requests.get(a_url, headers=headers, timeout=120)
            parser = html.fromstring(page.content)
            reviews = parser.xpath(xpath_reviews)
            for review in reviews:
                title = review.xpath(xpath_title)
                body = review.xpath(xpath_body)
                rc += 1
                if len(body) is not 0:
                    d = title[0] + ' '
                    ss = sid.polarity_scores(d + body[0])
                    k = ss[ind]
                    if (k > 0):
                        pos += 1
                    

        pr = str(format((pos / rc) * 100, '.3f')) + "%"
        print("Positive: ")
        print(pr)
        print("Total reviews:  ")
        print(rc)
        print("%s time in seconds" % (time.time() - start_time))

        neg = rc - pos

        if len(tt) > 255:
            tt = tt[:255]

        d = Drawing(21*cm, 29.7*cm)
        pc = Pie()
        pc.x = 200
        pc.y = 150
        pc.width = 220
        pc.height = 220
        pc.data = [pos, neg]
        pc.labels = ['Positive', 'Negative'] 
        pc.slices.strokeWidth = 0.5
        pc.slices[1].popout=6
        
        d.add(pc)
        fon=22
        d.add(String(14,670,'Product Name: '+tt[:42], fontSize=fon))
        count = int(len(tt)/41)-1
        if(len(tt)%41!=0):
            count+=1
        for i in range(1, count+1):
            d.add(String(14,670-i*30, '                        '+tt[(42*i):(42*i+42)], fontSize=fon))
        
        d.add(String(14,640-count*30,'Product Id: '+asin, fontSize=fon, ))
        d.add(String(14,610-count*30,'Total number of reviews: '+str(rc), fontSize=fon))
        d.add(String(14,580-count*30,'Number of Positive Reviews: '+str(pos), fontSize=fon))
        d.add(String(14,550-count*30,'Number of Negative Reviews: '+str(neg), fontSize=fon))
        d.add(String(14,520-count*30,'Rating: '+pr, fontSize=fon))
        renderPDF.drawToFile(d, tt+'.pdf','           Review Report')
 
       
if __name__ == '__main__':

    MainClass()
