from pypdf import PdfReader
from enum import Enum
import re

reader = PdfReader('../../tests/Издадени документи 2024.03.pdf')

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
            print(data)
            data = {}
