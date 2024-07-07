from pypdf import PdfReader
from enum import Enum
from datetime import date
from datetime import timedelta
import tkinter
from tkinter import messagebox
import re
import os

# Constants
INVOICE_DIRECTORY_PATH = '../../tests'
PAYMENT_WINDOW_DAYS = 14
PAID_INVOICE_FILE = 'PaidInvoiceList.txt'

skipWords = { 'Фактура', 'По', 'сметка', 'Служебен', 'потребител', 'потребител\n', 'В', 'брой', '(Анулиран)', '\n(Анулиран)'  }

class InvoiceFields(Enum):
    Total = 0,
    Tax = 1,
    TaxBase = 2,
    InvoiceID = 3,
    DocType = 4,
    Date = 5,
    PartnerName = 6,
    Bulstat = 7,
    PaymentType = 8,
    UserType = 9

class SettingSum(Enum):
    Total = 0,
    Tax = 1,
    TaxBase = 2

def parseWord(word, data, sum):
    bulstat = re.findall(r"\D(\d{9})\D", " "+word+" ")
    if (bulstat):
        data[InvoiceFields.Bulstat] = all

    if (word).isnumeric():
        if len(word) == 10:
            data[InvoiceFields.InvoiceID] = word
        if len(word) < 9:
            match sum:
                case SettingSum.Total:
                    data[InvoiceFields.Total] = word
                case SettingSum.Tax:
                    data[InvoiceFields.Tax] = word
                case SettingSum.TaxBase:
                    data[InvoiceFields.TaxBase] = word
    elif (len(word.split('.')) == 2):
        match sum:
            case SettingSum.Total:
                try:
                    data[InvoiceFields.Total] += word
                except:
                    data[InvoiceFields.Total] = word
                sum = SettingSum.Tax
            case SettingSum.Tax:
                try:
                    data[InvoiceFields.Tax] += word
                except:
                    data[InvoiceFields.Tax] = word
                sum = SettingSum.TaxBase
            case SettingSum.TaxBase:
                try:
                    data[InvoiceFields.TaxBase] += word
                except:
                    data[InvoiceFields.TaxBase] = word
                sum = SettingSum.Total
    elif (len(word.split('.')) == 3):
        data[InvoiceFields.Date] = word
    elif (word not in skipWords):
        cleanWord = word.strip()
        try:
            data[InvoiceFields.PartnerName] += (' ' + cleanWord)
        except:
            data[InvoiceFields.PartnerName] = cleanWord
    return sum
        
def checkDuePayment(invoice):
    dateStr = ''
    try:
        filteredDate = data[InvoiceFields.Date].split(')')
        if len(filteredDate) == 1:
            dateStr = filteredDate[0]
        elif len(filteredDate) == 2:
            dateStr = filteredDate[1]
    except:
        print("No date for invoice")
        return

    dateFields = dateStr.split('.')
    day = dateFields[0].lstrip('0')
    month = dateFields[1].lstrip('0')
    year = dateFields[2]

    today = date.today()
    invoiceDate = date(int(year), int(month), int(day))
    if ((today - invoiceDate) > timedelta(days = PAYMENT_WINDOW_DAYS)):
        if markedAsPaid(invoice[InvoiceFields.InvoiceID]):
            return
        try:
            res = tkinter.messagebox.askquestion("Неплатена фактура от: ", invoice[InvoiceFields.PartnerName] + "\nцъкнете YES, за да маркирате като платена или NO за повторно напомняне")
            if (res == 'yes'):
                markAsPaid(invoiceDate.strftime('%d%m%Y'), invoice[InvoiceFields.InvoiceID])
        except:
            tkinter.messagebox.showwarning("Warning", "Cannot parse invoice data")

def markAsPaid(date, id):
    paidInvoices = open(PAID_INVOICE_FILE, 'a')
    paidInvoices.write(date + ' ' + id + '\n')
    paidInvoices.close()

def markedAsPaid(id):
    try:
        paidInvoices = open(PAID_INVOICE_FILE, 'r')
        for line in paidInvoices.readlines():
            if id in line:
                return True
        return False
    except:
        return False


files = os.listdir(INVOICE_DIRECTORY_PATH)
invoiceFiles = []
for file in files:
    if file.find('pdf') != -1 and file.find('документи') != -1:
        invoiceFiles.insert(1, file)

for invoicePdf in invoiceFiles:
    reader = PdfReader(INVOICE_DIRECTORY_PATH + '/' + invoicePdf)
    pageCounter = 0
    for page in reader.pages:
        text = page.extract_text()
  
        # Parameter setup
        counter = 0
        data = {}
        sum = SettingSum.Total

        # Skip garbage at beginning of page
        garbageThreshhold = 5
        if (pageCounter == 0):
            garbageThreshhold = 16
        pageCounter = pageCounter + 1

        for word in text.split(' '):
            if counter > garbageThreshhold and len(word) > 0:
                sum = parseWord(word, data, sum)
            counter = counter + 1
            if len(data) == 7 and (word == 'По' or word == 'В'):
                checkDuePayment(data)
                print(data)
                data = {}
