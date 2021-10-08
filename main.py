import requests
import json
import re
import time

import logging
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

TG_TOKEN = "TG TOKEN"
FIXERIO_TOKEN = "TOKEN fixer.io"
uri = "http://data.fixer.io/api/latest?access_key={}&symbols=EUR,USD,RUB,CZK"
answer_template ="{} {} equals {} {}"

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

last_update_time = 0

rates = []

def convert(req, rates):
    if(re.match("\d*[a-z]{2}", req)):
        amount = float(re.match("\d*", req)[0])
        print(req)
        cur_from, cur_to = re.findall("[ucer]", req)
        #print(req, " from: ", cur_from, " to: ", cur_to, sep="")

        if(cur_from == "c"):
            if(cur_to == "e"): #from czk to eur
                eur = float(amount) / float(rates["rates"]["CZK"])
                #rub = eur * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                result = answer_template.format(amount, "czk", round(eur, 2), "eur")

            elif(cur_to == "u"): #from czk to usd
                eur = float(amount) / float(rates["rates"]["CZK"])
                #rub = eur * float(rates["rates"]["RUB"])
                usd = eur * float(rates["rates"]["USD"])
                result = answer_template.format(amount, "czk", round(usd, 2), "usd")

            elif(cur_to == "r"): #from czk to rub
                eur = float(amount) / float(rates["rates"]["CZK"])
                rub = eur * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                result = answer_template.format(amount, "czk", round(rub, 2), "rub")
        
        elif(cur_from == "u"):
            if(cur_to == "e"): #from usd to eur
                eur = float(amount) * float(rates["rates"]["USD"])
                #rub = eur * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                result = answer_template.format(amount, "usd", round(eur, 2), "eur")
            
            if(cur_to == "c"): #from usd to czk
                eur = float(amount) * float(rates["rates"]["USD"])
                #rub = eur * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                czk = eur * float(rates["rates"]["CZK"])
                result = answer_template.format(amount, "usd", round(czk, 2), "czk")

            if(cur_to == "r"): #from usd to rub
                eur = float(amount) * float(rates["rates"]["USD"])
                rub = eur * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                #czk = eur * float(rates["rates"]["CZK"])
                result = answer_template.format(amount, "czk", round(rub, 2), "rub")
    
        elif(cur_from == "e"):
            if(cur_to == "c"): #from eur to czk
                #eur = float(rates["rates"]["EUR"])
                #rub = eur * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                czk = amount * float(rates["rates"]["CZK"])
                result = answer_template.format(amount, "eur", round(czk, 2), "czk")

            if(cur_to == "u"): #from eur to usd
                #eur = float(rates["rates"]["EUR"])
                #rub = eur * float(rates["rates"]["RUB"])
                usd = amount * float(rates["rates"]["USD"])
                #czk = eur * float(rates["rates"]["CZK"])
                result = answer_template.format(amount, "eur", round(usd, 2), "usd")

            if(cur_to == "r"): #from eur to rub
                #eur = float(rates["rates"]["EUR"])
                rub = amount * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                #czk = eur * float(rates["rates"]["CZK"])
                result = answer_template.format(amount, "eur", round(rub, 2), "rub")

        elif(cur_from == "r"):
            if(cur_to == "e"): #from rub to eur
                eur = (float(amount) / float(rates["rates"]["RUB"]))
                #rub = eur * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                #czk = eur * float(rates["rates"]["CZK"])
                result = answer_template.format(amount, "rub", round(eur, 2), "eur")
    
            if(cur_to == "u"): #from rub to eur
                eur = (float(amount) / float(rates["rates"]["RUB"]))
                #rub = eur * float(rates["rates"]["RUB"])
                usd = eur * float(rates["rates"]["USD"])
                #czk = eur * float(rates["rates"]["CZK"])
                result = answer_template.format(amount, "rub", round(usd, 2), "usd")

            if(cur_to == "c"): #from rub to eur
                eur = (float(amount) / float(rates["rates"]["RUB"]))
                #rub = eur * float(rates["rates"]["RUB"])
                #usd = eur * float(rates["rates"]["USD"])
                czk = eur * float(rates["rates"]["CZK"])
                result = answer_template.format(amount, "rub", round(czk, 2), "czk")
    return result

def rate_update():
    global uri
    global rates
    uri = uri.format(FIXERIO_TOKEN)
    r = requests.get(uri)
    #print(r.text)
    rates = json.loads(r.text)
    answer = """
*Exchange rate sync*:
*1 eur equals:*
```
{} czk
{} rub
{} usd
```
    """.format(float(rates["rates"]["CZK"]), float(rates["rates"]["RUB"]), float(rates["rates"]["USD"]))
    print(answer)
    return answer


@dp.message_handler()
async def echo(message: types.Message):
    global last_update_time
    if(round(time.time() - last_update_time, 2) > 14400):
        rate_update()
        last_update_time = time.time()


    if(bool(re.match("\d{1,}[a-z]{2}", message.text))):
        await message.answer(convert(message.text, rates))
    elif(message.text == "sync"):
        await message.answer(rate_update(), parse_mode='Markdown')
    else:
        await message.answer("Example use: \"330cr\" to convert 330 czk to rub. Supported currencies: EUR(e), CZK(c), RUB(r), USD(u)")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
