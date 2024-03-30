import discord
from discord.ext import commands
from discord.ext import tasks
import sqlite3
import random
import time
import datetime
import token_Stocks
import function as f
import stock_list

app = commands.Bot(command_prefix='!', intents=discord.Intents.all())
con = sqlite3.connect('data.db', isolation_level=None)
cur = con.cursor()

cur.execute(
    "CREATE TABLE IF NOT EXISTS UserInfo(user_id INTEGER PRIMARY KEY, user_name TEXT, bank TEXT, account TEXT, money INTEGER, create_date TEXT)")
cur.execute(
    "CREATE TABLE IF NOT EXISTS Stock(stock_id INTEGER PRIMARY KEY, stock_name TEXT, price INTEGER, quote INTEGER, stock_code TEXT)")
cur.execute(
    "CREATE TABLE IF NOT EXISTS StockTrading(user_id INTEGER, stock_name TEXT, quantity INTEGER, price INTEGER, transaction_type TEXT, transaction_date TEXT)")

# 종목 추가
stock_list.addStockList(cur)
con.close()


@app.event
async def on_ready():
    print(f'{app.user.name} 연결 성공')
    updatedQuote.start()
    await app.change_presence(status=discord.Status.online, activity=discord.Game('Developed by 희연'))


@app.command(aliases=['도움말'])
async def helpCommand(ctx):
    embed = discord.Embed(title=':white_check_mark: 도움말', description='\n', color=0x000000)
    embed.add_field(name='!가입하기', value='Stocks에 가입 합니다.', inline='False')
    embed.add_field(name='!탈퇴하기', value='Stocks로부터 탈퇴 합니다.', inline='False')
    embed.add_field(name='!회원목록', value='Stocks에 가입된 사용자를 볼 수 있습니다.\n', inline='False')

    embed.add_field(name='!내지갑', value='나의 은행 및 계좌의 돈을 조회 할 수 있습니다.', inline='False')
    embed.add_field(name='!계좌개설', value='최대 1개의 은행, 최대 1개의 계좌를 개설할 수 있습니다.', inline='False')
    embed.add_field(name='!계좌삭제', value='개설되어있는 계좌를 삭제합니다.', inline='False')
    embed.add_field(name='!주식시장', value='상장된 종목의 주가와 시세를 볼 수 있습니다.\n종목의 주가와 시세는 1시간마다 정각에 변경됩니다.', inline='False')
    embed.add_field(name='!매수 (종목) (수량)', value='(종목)을 (수량) 만큼 매수할 수 있습니다.', inline='False')
    embed.add_field(name='!매도 (종목) (수량)', value='(종목)을 (수량) 만큼 매도할 수 있습니다.\n', inline='False')

    embed.add_field(name='!홀짝 (베팅금)', value='(베팅금) 을 걸고 홀짝 게임을 합니다. 홀짝에 성공하면 두배로 돌려받습니다. 실패한다면 (베팅금) 을 잃습니다.',
                    inline='False')
    embed.add_field(name='\n!송금 (@보낼사람) (보낼금액)', value='(@보낼사람) 에게 (보낼금액) 만큼 송금합니다.\n', inline='False')
    embed.add_field(name='\n!슬롯머신 (베팅금)', value='(베팅금) 을 걸고 슬롯머신을 합니다. 트리플은 10배, 더블은 5배로 베팅금을 돌려받습니다. 이 외에는 (베팅금) 을 잃습니다.\n', inline='False')
    await ctx.send(embed=embed)


@app.command(aliases=['회원목록'])
async def userList(ctx):
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("SELECT COUNT(user_id) FROM UserInfo")
    userLen = cur.fetchall()
    userLenInt = userLen[0][0]
    cur.execute("SELECT user_name from UserInfo")
    userNameList = cur.fetchall()
    embed = discord.Embed(title=':busts_in_silhouette: 회원 목록', description='\n', color=0x00ff00)

    for i in range(userLenInt):
        embed.add_field(name='', value=userNameList[i][0], inline='False')

    await ctx.send(embed=embed)
    con.close()


@app.command(aliases=['가입하기'])
async def signUp(ctx):
    user_id = ctx.author.id
    name = ctx.author.name
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
    check = f.checkUser(user_id)

    if check == 0:
        null = 'NULL'
        cur.execute("INSERT INTO UserInfo VALUES(?, ?, ?, ?, ?, ?)", (user_id, name, null, null, null, nowDatetime,))
        embed = discord.Embed(title=':wave: 회원가입', description='**성공적으로 가입 되었습니다. {}**'.format(ctx.author.mention),
                              color=0x2cc558)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check == 1:
        embed = discord.Embed(title=':x: 회원가입', description='**이미 가입되어 있습니다. {}**'.format(ctx.author.mention),
                              color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    con.close()


@app.command(aliases=['탈퇴하기'])
async def secession(ctx):
    user_id = ctx.author.id
    name = ctx.author.name
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    cur.execute("UPDATE UserInfo SET user_name = ? WHERE user_id = ?", (name, user_id,))
    check = f.checkUser(user_id)

    if check == 0:
        embed = discord.Embed(title=':x: 회원탈퇴',
                              description='회원이 아닙니다. {}\n먼저 회원가입을 해주세요.\n\n!가입하기'.format(ctx.author.mention),
                              color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check == 1:
        cur.execute("DELETE FROM UserInfo WHERE user_id = ?", (user_id,))
        cur.execute("UPDATE UserInfo SET money = 'NULL' WHERE user_id = ?", (user_id,))
        cur.execute("UPDATE UserInfo SET account = 'NULL' WHERE user_id = ?", (user_id,))
        cur.execute("UPDATE UserInfo SET bank = 'NULL' WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM StockTrading WHERE user_id = ?", (user_id,))
        embed = discord.Embed(title=':sob: 회원탈퇴', description='**성공적으로 탈퇴되었습니다. {}**'.format(ctx.author.mention),
                              color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    con.close()


@app.command(aliases=['내지갑'])
async def myInfo(ctx):
    user_id = ctx.author.id
    con = sqlite3.connect('data.db', isolation_level=None)
    cur = con.cursor()
    check = f.checkUser(user_id)
    con.close()

    if check == 0:
        embed = discord.Embed(title=':x: 내 지갑', description='회원이 아닙니다. {}\n먼저 회원가입을 해주세요.\n\n!가입하기'.format(ctx.author.mention), color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check == 1:
        isBank = f.checkBank(user_id)

        if isBank == 0:
            embed = discord.Embed(title=':x: 내 지갑', description='**계좌가 하나도 없습니다. {}\n먼저 계좌를 개설해주세요.\n\n!계좌개설**'.format(
                ctx.author.mention),
                                  color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

        elif isBank == 1:
            user_bank = f.getValueOnDB(user_id, 'bank', 'UserInfo')
            user_account = f.getValueOnDB(user_id, 'account', 'UserInfo')
            user_money = f.getValueOnDB(user_id, 'money', 'UserInfo')
            embed = discord.Embed(title=':purse: 내 지갑', description='{}'.format(ctx.author.mention), color=0xffD400)
            embed.add_field(name='**은행 : **' + user_bank + ' Bank', value='**계좌번호 : **' + user_account + '**\n잔액 : ' + str(user_money) + '\n,**', inline='False')
            con = sqlite3.connect('data.db', isolation_level=None)
            cur = con.cursor()
            cur.execute("SELECT COUNT(DISTINCT stock_name) AS matching_count FROM StockTrading WHERE user_id IN (" + str(user_id) + ")")
            typeCount = cur.fetchall()
            typeCountList = list(typeCount[0])
            typeCountInt = typeCountList[0]
            cur.execute("SELECT DISTINCT stock_name FROM StockTrading WHERE user_id IN (" + str(user_id) + ")")
            stockNames = cur.fetchall()
            stockNameList = [item[0] for item in stockNames]

            for i in range(typeCountInt):
                cur.execute("SELECT quantity FROM StockTrading WHERE user_id = ? AND stock_name = ?",
                            (user_id, stockNameList[i]))
                stockQuantites = cur.fetchall()
                stockQuantitesList = [item[0] for item in stockQuantites]

                cur.execute("SELECT price FROM StockTrading WHERE user_id = ? AND stock_name = ?",
                            (user_id, stockNameList[i]))
                stockPrices = cur.fetchall()
                stockPricesList = [item[0] for item in stockPrices]
                priceSum = 0

                for j in range(len(stockQuantites)):
                    priceSum += stockQuantitesList[j] * stockPricesList[j]

                if (sum(stockQuantitesList) != 0):
                    stockPriceAvg = priceSum / sum(stockQuantitesList)
                elif (sum(stockQuantitesList) == 0):
                    stockPriceAvg = priceSum

                cur.execute("SELECT price FROM Stock WHERE stock_name = ?", (stockNameList[i],))
                stockPriceOriginals = cur.fetchall()
                stockPricesOriginalList = [item[0] for item in stockPriceOriginals]
                if (stockPriceAvg != 0):
                    quoteChange = (stockPricesOriginalList[0] - stockPriceAvg) / stockPriceAvg * 100
                else:
                    quoteChange = (stockPricesOriginalList[0] - stockPriceAvg)

                embed.add_field(name='**' + str(stockNameList[i]) + '**',
                                value='**시장 주가 : ' + str(round(stockPricesOriginalList[0])) + '원 ' + str(
                                    round(quoteChange, 1)) + '%\n보유 주가 : ' + str(
                                    round(stockPriceAvg)) + '원\n보유 개수 : ' + str(sum(stockQuantitesList)) + '**',
                                inline='False')

            con.close()
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)


@app.command(aliases=['계좌개설'])
async def creatAccount(ctx):
    user_id = ctx.author.id
    check_user = f.checkUser(user_id)

    if check_user == 0:
        embed = discord.Embed(title=':x: 계좌개설', description='회원이 아닙니다.\n먼저 회원가입을 해주세요.\n\n!가입하기', color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check_user == 1:
        check_bank = f.checkBank(user_id)

        if check_bank == 0:
            embed = discord.Embed(title=':bank: 계좌 개설',
                                  description='**계좌를 개설할 은행을 선택해주세요. {}\n\n최대 1개 은행에서 최대 1개의 계좌를 개설할 수 있습니다!\n\n<:kb:1183447867642355712> - 국민은행\n<:hana:1183447864496636056> - 하나은행\n<:woori:1183447869592703056> - 우리은행**'.format(
                                      ctx.author.mention),
                                  color=0xffD400)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            msg = await ctx.send(embed=embed)
            emoji1 = discord.utils.get(ctx.guild.emojis, name="kb")
            await msg.add_reaction(emoji1)
            emoji2 = discord.utils.get(ctx.guild.emojis, name="hana")
            await msg.add_reaction(emoji2)
            emoji3 = discord.utils.get(ctx.guild.emojis, name="woori")
            await msg.add_reaction(emoji3)

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction)

            reaction, user = await app.wait_for('reaction_add', check=check)

            user_bank = 'bank'

            # 누른 이모지 아이디 매치
            if (str(reaction) == '<:hana:1183456523578507294>' or str(reaction) == '<:hana:1183447864496636056>' or str(
                    reaction) == '<:hana:1190979220835410020>' or str(reaction) == '<:hana:1196591569160122378>'):
                user_bank = 'Hana'
            elif (str(reaction) == '<:kb:1183456525327548486>' or str(reaction) == '<:kb:1183447867642355712>' or str(
                    reaction) == '<:kb:1190979246873661450>' or str(reaction) == '<:kb:1196591583848566894>'):
                user_bank = 'KB Kookmin'
            elif (str(reaction) == '<:woori:1183456527718289449>' or str(
                    reaction) == '<:woori:1183447869592703056>' or str(
                    reaction) == '<:woori:1190979265785761792>' or str(reaction) == '<:woori:1196591550059261962>'):
                user_bank = 'Woori'

            # 누른 이모지 아이디 매치 실패
            if user_bank != 'bank':
                con = sqlite3.connect('data.db', isolation_level=None)
                cur = con.cursor()

                cur.execute("SELECT user_name FROM UserInfo WHERE user_id = ?", (user_id,))
                user_name = cur.fetchall

                cur.execute("UPDATE UserInfo SET bank = ? WHERE user_id = ?", (user_bank, user_id,))

                acListRepeat = 0

                while True:
                    user_account = random.randint(10000000000, 99999999999)

                    cur.execute("SELECT account FROM UserInfo")
                    account3 = cur.fetchall()
                    account2 = account3[acListRepeat]
                    account1 = account2[0]

                    if str(user_account) == account1:
                        acListRepeat += 1
                        continue

                    if str(user_account) != account1:
                        break

                cur.execute("UPDATE UserInfo SET account = ? WHERE user_id = ?", (str(user_account), user_id,))
                user_money = 1000000
                cur.execute("UPDATE UserInfo SET money = ? WHERE user_id = ?", (user_money, user_id,))
                con.close()
                embed = discord.Embed(title=':bank: 계좌 개설',
                                      description='**' + user_bank + ' Bank에 계좌를 개설했습니다.\n\n은행 : **' + user_bank + '** Bank\n계좌번호 : **' + str(
                                          user_account) + '**\n잔액 : **' + str(user_money), color=0xFFD400)

            elif user_bank == 'bank':
                embed = discord.Embed(title=':x: 계좌 개설', description='**계좌를 개설할 수 없습니다.**', color=0xFF0000)

            await msg.clear_reaction(emoji3)
            await msg.clear_reaction(emoji2)
            await msg.clear_reaction(emoji1)
            await msg.edit(embed=embed)

        elif check_bank == 1:
            embed = discord.Embed(title=':x: 계좌 개설', description='**계좌가 이미 개설되어있습니다.**\n\n!내지갑', color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)


@app.command(aliases=['계좌삭제'])
async def deleteAccount(ctx):
    user_id = ctx.author.id
    check_user = f.checkUser(user_id)

    if check_user == 0:
        embed = discord.Embed(title=':x: 계좌 삭제', description='회원이 아닙니다.\n먼저 회원가입을 해주세요.\n\n!가입하기', color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check_user == 1:
        check_bank = f.checkBank(user_id)

        if check_bank == 0:
            embed = discord.Embed(title=':x: 계좌 삭제', description='**계좌가 하나도 없습니다.\n먼저 계좌를 개설해주세요.\n\n!계좌개설**',
                                  color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

        elif check_bank == 1:
            name1 = f.getValueOnDB(ctx, 'user_name', 'UserInfo')
            bank1 = f.getValueOnDB(ctx, 'bank', 'UserInfo')
            account1 = f.getValueOnDB(ctx, 'account', 'UserInfo')
            con = sqlite3.connect('data.db', isolation_level=None)
            cur = con.cursor()
            cur.execute("UPDATE UserInfo SET money = 'NULL' WHERE user_id = ?", (user_id,))
            cur.execute("UPDATE UserInfo SET account = 'NULL' WHERE user_id = ?", (user_id,))
            cur.execute("UPDATE UserInfo SET bank = 'NULL' WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM StockTrading WHERE user_id = ?", (user_id,))

            con.close()
            embed = discord.Embed(title=':money_with_wings: 계좌 삭제',
                                  description=name1 + '**의 계좌가 성공적으로 삭제되었습니다.\n\n삭제된 계좌\n**' + bank1 + '** Bank의 **' + account1,
                                  color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)


@app.command(aliases=['주식시장'])
async def securitiesMarket(ctx):
    name = []
    price = []
    quote = []
    code = []

    for i in range(1, f.getStockCount() + 1): name.append(f.getStockOnDB(i, 'stock_name', 'Stock'))
    for i in range(1, f.getStockCount() + 1): price.append(f.getStockOnDB(i, 'price', 'Stock'))
    for i in range(1, f.getStockCount() + 1): quote.append(f.getStockOnDB(i, 'quote', 'Stock'))
    for i in range(1, f.getStockCount() + 1): code.append(f.getStockOnDB(i, 'stock_code', 'Stock'))

    embed = discord.Embed(title=':chart_with_upwards_trend: 주식 시장', description='\n', color=0xFFD400)

    for i in range(0, f.getStockCount()): embed.add_field(name=name[i] + '(' + code[i] + ')', value=format(price[i], ',') + ' **' + str(quote[i]) + '%**',inline='False')

    await ctx.send(embed=embed)


async def buyStock(ctx, name, quantity):
    dt = datetime.datetime.now()
    dateNow = dt.strftime('%Y-%m-%d %H:%M:%S')
    user_id = ctx.author.id
    check_user = f.checkUser(user_id)
    stock_price = f.getStockPriceOnDB(name, 'price', 'Stock')

    if check_user == 0:
        embed = discord.Embed(title=':x: 주식 매수', description='회원이 아닙니다.\n먼저 회원가입을 해주세요.\n\n!가입하기', color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check_user == 1:
        check_bank = f.checkBank(user_id)

        if check_bank == 0:
            embed = discord.Embed(title=':x: 주식 매수', description='**계좌가 하나도 없습니다.\n먼저 계좌를 개설해주세요.\n\n!계좌개설**',
                                  color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

        elif check_bank == 1:
            if (quantity == 'all'):
                quantity = int(int(f.getValueOnDB(user_id, 'money', 'UserInfo')) / int(stock_price))

            if f.stockNameCheck(name) == 0 or int(quantity) <= 0:
                embed = discord.Embed(title=':x: 주식 매수', description='**매수를 할 수 없습니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)

            elif f.stockNameCheck(name) == 1 and int(quantity) > 0:
                if int(int(stock_price) * int(quantity)) <= int(f.getValueOnDB(user_id, 'money', 'UserInfo')):
                    con = sqlite3.connect('data.db', isolation_level=None)
                    cur = con.cursor()
                    balance = int(f.getValueOnDB(user_id, 'money', 'UserInfo')) - int(stock_price) * int(quantity)
                    cur.execute("UPDATE UserInfo SET money = ? WHERE user_id = ?", (balance, user_id,))
                    cur.execute("INSERT INTO StockTrading VALUES(?, ?, ?, ?, ?, ?)",
                                (user_id, name, quantity, stock_price, 'BUY', dateNow,))
                    con.close()
                    embed = discord.Embed(title=':bar_chart: 주식 매수',
                                          description='**' + str(name) + ' ' + str(quantity) + '주를 주당 ' + str(
                                              stock_price) + '원에 매수하였습니다.\n잔액 : **' + str(
                                              f.getValueOnDB(user_id, 'money', 'UserInfo')), color=0xffD400)
                    embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                     icon_url=ctx.message.author.avatar_url)
                    await ctx.send(embed=embed)

                elif int(int(stock_price) * int(quantity)) > int(f.getValueOnDB(user_id, 'money', 'UserInfo')):
                    user_money = f.getValueOnDB(user_id, 'money', 'UserInfo')
                    embed = discord.Embed(title=':x: 주식 매수',
                                          description='**주식을 매수할 수 없습니다. 잔액이 부족합니다.\n\n잔액 : ' + str(user_money) + '원**',
                                          color=0xff0000)
                    embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                     icon_url=ctx.message.author.avatar_url)
                    await ctx.send(embed=embed)


@app.command(aliases=['매도'])
async def sellStock(ctx, name, quantity):
    user_id = ctx.author.id
    check_user = f.checkUser(user_id)

    if check_user == 0:
        embed = discord.Embed(title=':x: 주식 매도', description='회원이 아닙니다.\n먼저 회원가입을 해주세요.\n\n!가입하기', color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check_user == 1:
        check_bank = f.checkBank(user_id)

        if check_bank == 0:
            embed = discord.Embed(title=':x: 주식 매도', description='**계좌가 하나도 없습니다.\n먼저 계좌를 개설해주세요.\n\n!계좌개설**',
                                  color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

        elif check_bank == 1:
            con = sqlite3.connect('data.db', isolation_level=None)
            cur = con.cursor()
            cur.execute("SELECT quantity FROM StockTrading WHERE user_id = ? AND stock_name = ?", (user_id, name))
            stockQuantites = cur.fetchall()
            stockQuantitesList = [item[0] for item in stockQuantites]

            if (quantity == 'all'):
                quantity = int(sum(stockQuantitesList))

            if f.stockNameCheck(name) == 0 or int(quantity) <= 0:
                embed = discord.Embed(title=':x: 주식 매도', description='**매도를 할 수 없습니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)

            elif f.stockNameCheck(name) == 1 and int(quantity) > 0:
                user_money = f.getValueOnDB(user_id, 'money', 'UserInfo')
                cur.execute("SELECT price FROM Stock WHERE stock_name = ?", (name,))
                stockPriceOriginals = cur.fetchall()
                stockPricesOriginalList = [item[0] for item in stockPriceOriginals]

                if (sum(stockQuantitesList) < int(quantity)):
                    embed = discord.Embed(title=':x: 주식 매도', description='**매도하려는 주식이 부족합니다.**', color=0xff0000)
                    embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                     icon_url=ctx.message.author.avatar_url)
                    await ctx.send(embed=embed)
                    return

                cur.execute("SELECT price FROM StockTrading WHERE user_id = ? AND stock_name = ?",
                            (user_id, name))
                stockPrices = cur.fetchall()
                stockPricesList = [item[0] for item in stockPrices]
                priceSum = 0

                for j in range(len(stockQuantites)):
                    priceSum += stockQuantitesList[j] * stockPricesList[j]

                stockPriceAvg = priceSum / sum(stockQuantitesList)

                profit = (stockPricesOriginalList[0] - stockPriceAvg) * int(quantity)

                balanceQuantity = sum(stockQuantitesList) - int(quantity)

                if (balanceQuantity != 0):
                    balancePrice = (priceSum - stockPriceAvg * int(quantity)) / balanceQuantity
                    cur.execute("DELETE FROM StockTrading WHERE user_id = ? AND stock_name = ?", (user_id, name))
                    cur.execute("INSERT INTO StockTrading VALUES(?, ?, ?, ?, ?, ?)",
                                (user_id, name, int(balanceQuantity), int(balancePrice), 'BUY', 'UPDATED'))
                elif (balanceQuantity == 0):
                    balancePrice = (priceSum - stockPriceAvg * int(quantity))
                    cur.execute("DELETE FROM StockTrading WHERE user_id = ? AND stock_name = ?", (user_id, name))

                cur.execute("UPDATE UserInfo SET money = ? WHERE user_id = ?",
                            (int(user_money) + int(stockPricesOriginalList[0] * int(quantity)), user_id,))

                con.close();

                user_money = f.getValueOnDB(user_id, 'money', 'UserInfo')
                embed = discord.Embed(title=':bar_chart: 주식 매도',
                                      description=str(name) + ' ' + str(quantity) + '**주를 주당 ' + str(
                                          round(stockPricesOriginalList[0])) + '원에 판매하였습니다.\n\n손익 : ' + str(
                                          round(profit)) + '원\n\n잔액 : ' + str(user_money) + '원**', color=0xffD400)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)


@app.command(aliases=['송금'])
async def sendMoney(ctx, user: discord.User, money):
    user_id = ctx.author.id
    check_user = f.checkUser(user_id)
    money = int(float(money))

    if check_user == 0:
        embed = discord.Embed(title=':x: 송금', description='회원이 아닙니다.\n먼저 회원가입을 해주세요.\n\n!가입하기', color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check_user == 1:
        check_bank = f.checkBank(user_id)

        if check_bank == 0:
            embed = discord.Embed(title=':x: 송금', description='**계좌가 하나도 없습니다.\n먼저 계좌를 개설해주세요.\n\n!계좌개설**',
                                  color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

        elif check_bank == 1:
            user_money = f.getValueOnDB(user_id, 'money', 'UserInfo')

            if money > int(user_money):
                embed = discord.Embed(title=':x: 송금', description='**송금할 금액이 부족합니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            if money <= 0 or money % 1 > 0:
                embed = discord.Embed(title=':x: 송금', description='**송금할 금액이 잘못되었습니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            if f.checkUser(user.id) == 0:
                embed = discord.Embed(title=':x: 송금', description='**가입된 회원에게만 송금할 수 있습니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            if user.id == ctx.author.id:
                embed = discord.Embed(title=':x: 송금', description='**자신에게 송금할 수 없습니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            if money > 0 and money % 1 == 0 and f.checkUser(user.id):
                toPersonId = user.id
                toPersonName = user.name
                embed = discord.Embed(title=':money_with_wings: 송금', description='**' + toPersonName + ' 님에게 ' + str(
                    money) + '원을 송금하시겠습니까?\n\n송금액 : ' + str(money) + '\n\n송금 후 잔액 : ' + str(
                    int(user_money) - money) + '**', color=0xffD400)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                msg = await ctx.send(embed=embed)
                push = '✅'
                cancle = '❌'

                await msg.add_reaction(push)
                await msg.add_reaction(cancle)

                def check(reaction, user):
                    return user == ctx.author and reaction.message.id == msg.id and str(reaction)

                reaction, user = await app.wait_for('reaction_add', check=check)

                userAnswer = 'None'

                if (str(reaction) == push):
                    userAnswer = 'pushed'

                if (str(reaction) == cancle):
                    userAnswer = 'cancled'

                if userAnswer == 'None':
                    embed = discord.Embed(title=':x: 송금', description='**처리할 수 없습니다.**', color=0xFFFFFF)
                    embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                     icon_url=ctx.message.author.avatar_url)

                elif userAnswer != 'None':
                    if userAnswer == 'pushed':
                        con = sqlite3.connect('data.db', isolation_level=None)
                        cur = con.cursor()

                        balance = int(user_money) - money
                        cur.execute("UPDATE UserInfo SET money = ? WHERE user_id = ?", (balance, user_id,))
                        balance = int(f.getValueOnDB(toPersonId, 'money', 'UserInfo')) + money
                        cur.execute("UPDATE UserInfo SET money = ? WHERE user_id = ?", (balance, toPersonId,))

                        con.close()

                        embed = discord.Embed(title=':money_with_wings: 송금',
                                              description='**' + toPersonName + ' 님에게 ' + str(
                                                  money) + '원을 성공적으로 송금하였습니다.\n\n남은 잔액 : ' + str(
                                                  int(user_money) - money) + '**', color=0xFFD400)
                        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                         icon_url=ctx.message.author.avatar_url)

                    if userAnswer == 'cancled':
                        embed = discord.Embed(title=':x: 송금', description='**송금을 취소했습니다.**', color=0xFFFFFF)
                        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                         icon_url=ctx.message.author.avatar_url)

            await msg.clear_reaction(cancle)
            await msg.clear_reaction(push)
            await msg.edit(embed=embed)


@app.command(aliases=['홀짝'])
async def snifflingGame(ctx, amount):
    user_id = ctx.author.id
    check_user = f.checkUser(user_id)

    if check_user == 0:
        embed = discord.Embed(title=':x: 홀짝 게임', description='회원이 아닙니다.\n먼저 회원가입을 해주세요.\n\n!가입하기', color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check_user == 1:
        check_bank = f.checkBank(user_id)

        if check_bank == 0:
            embed = discord.Embed(title=':x: 홀짝 게임', description='**계좌가 하나도 없습니다.\n먼저 계좌를 개설해주세요.\n\n!계좌개설**',
                                  color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

        elif check_bank == 1:
            user_money = f.getValueOnDB(user_id, 'money', 'UserInfo')

            if int(amount) > int(user_money):
                embed = discord.Embed(title=':x: 홀짝 게임', description='**베팅할 금액이 부족합니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            if int(amount) <= 0:
                embed = discord.Embed(title=':x: 홀짝 게임', description='**베팅할 금액이 잘못되었습니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            systemAnswer = random.randint(1, 4)
            addMoney = int(amount)
            con = sqlite3.connect('data.db', isolation_level=None)
            cur = con.cursor()

            embed = discord.Embed(title=':game_die: 홀짝 게임', description='**베팅금 : ' + str(
                amount) + '\n\n:blue_square: 홀수\n:orange_square: 짝수\n\n성공시 : 베팅금 x 2\n실패시 : 베팅금 x 0**', color=0xffD400)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            msg = await ctx.send(embed=embed)
            even = '🟦'
            odd = '🟧'
            await msg.add_reaction(even)
            await msg.add_reaction(odd)

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and str(reaction)

            reaction, user = await app.wait_for('reaction_add', check=check)

            userAnswer = 'None'

            if (str(reaction) == even):
                userAnswer = '홀'
            elif (str(reaction) == odd):
                userAnswer = '짝'

            if userAnswer == 'None':
                embed = discord.Embed(title=':x: 홀짝 게임', description='**처리할 수 없습니다.**', color=0xFFD400)

            elif userAnswer != 'None':
                if systemAnswer == 1:
                    cur.execute("UPDATE UserInfo SET money = ? WHERE user_id = ?",
                                (int(user_money) + addMoney, user_id,))
                    if userAnswer == '홀':
                        embed = discord.Embed(title=':game_die: 홀짝 게임',
                                              description='**축하합니다!\n\n정답 -> 홀수 :blue_square:\n\n수익 : ' + str(
                                                  addMoney * 2) + '\n잔고 : ' + str(
                                                  f.getValueOnDB(user_id, 'money', 'UserInfo')) + '**', color=0xFFD400)
                    elif userAnswer == '짝':
                        embed = discord.Embed(title=':game_die: 홀짝 게임',
                                              description='**축하합니다!\n\n정답 -> 짝수 :orange_square:\n\n수익 : ' + str(
                                                  addMoney * 2) + '\n잔고 : ' + str(
                                                  f.getValueOnDB(user_id, 'money', 'UserInfo')) + '**', color=0xFFD400)
                else:
                    cur.execute("UPDATE UserInfo SET money = ? WHERE user_id = ?",
                                (int(user_money) - addMoney, user_id,))
                    if userAnswer == '홀':
                        embed = discord.Embed(title=':game_die: 홀짝 게임',
                                              description='**아쉽습니다!\n\n정답 -> 짝수 :orange_square:\n\n수익 : ' + str(
                                                  addMoney * -1) + '\n잔고 : ' + str(
                                                  f.getValueOnDB(user_id, 'money', 'UserInfo')) + '**', color=0xFF0000)
                    elif userAnswer == '짝':
                        embed = discord.Embed(title=':game_die: 홀짝 게임',
                                              description='**아쉽습니다!\n\n정답 -> 홀수 :blue_square:\n\n수익 : ' + str(
                                                  addMoney * -1) + '\n잔고 : ' + str(
                                                  f.getValueOnDB(user_id, 'money', 'UserInfo')) + '**', color=0xFF0000)
            con.close()
            await msg.clear_reaction(even)
            await msg.clear_reaction(odd)
            await msg.edit(embed=embed)


@app.command(aliases=['슬롯머신'])
async def slotMachineGame(ctx, amount):
    user_id = ctx.author.id
    check_user = f.checkUser(user_id)
    user_money = f.getValueOnDB(user_id, 'money', 'UserInfo')

    if amount == 'all':
        amount = user_money

    if check_user == 0:
        embed = discord.Embed(title=':x: 슬롯머신', description='회원이 아닙니다.\n먼저 회원가입을 해주세요.\n\n!가입하기', color=0xff0000)
        embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

    elif check_user == 1:
        check_bank = f.checkBank(user_id)

        if check_bank == 0:
            embed = discord.Embed(title=':x: 슬롯머신', description='**계좌가 하나도 없습니다.\n먼저 계좌를 개설해주세요.\n\n!계좌개설**',
                                  color=0xff0000)
            embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472", icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

        elif check_bank == 1:

            if int(amount) > int(user_money):
                embed = discord.Embed(title=':x: 슬롯머신', description='**베팅할 금액이 부족합니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            if int(amount) <= 0:
                embed = discord.Embed(title=':x: 슬롯머신', description='**베팅할 금액이 잘못되었습니다.**', color=0xff0000)
                embed.set_footer(text=f"{ctx.message.author.name} | Stocks#1472",
                                 icon_url=ctx.message.author.avatar_url)
                await ctx.send(embed=embed)
                return

            inslot = []
            icon = ['🍎', '💵', '🔪', '🍔', '💖', '💎']

            for j in range(3):
                inslot.append(random.choice(icon))
            embed = discord.Embed(title=':slot_machine: 슬롯머신',
                                  description='**' + str(inslot) + '\n\n베팅금 : ' + str(amount) + '**', color=0xFFD400)

            msg = await ctx.send(embed=embed)

            for i in range(5):
                inslot.clear()
                for j in range(3):
                    inslot.append(random.choice(icon))
                embed = discord.Embed(title=':slot_machine: 슬롯머신',
                                      description='**' + str(inslot) + '\n\n베팅금 : ' + str(amount) + '**',
                                      color=0xFFD400)
                await msg.edit(embed=embed)

            if len(list(set(inslot))) == 1:
                result = '트리플! x10'
                outMoney = int(amount) * 10

            elif len(list(set(inslot))) == 2:
                result = '더블! x5'
                outMoney = int(amount) * 5

            else:
                result = '돈을 잃었습니다...'
                outMoney = int(amount) * 0

            balance = user_money + outMoney - int(amount)
            con = sqlite3.connect('data.db', isolation_level=None)
            cur = con.cursor()
            cur.execute("UPDATE UserInfo SET money = ? WHERE user_id = ?", (balance, user_id,))
            con.close()
            embed = discord.Embed(title=':slot_machine: 슬롯머신', description='**' + str(inslot) + '\n\n베팅금 : ' + str(
                amount) + '\n\n' + result + '\n\n수익 : ' + str(outMoney) + '\n잔액 : ' + str(balance) + '**',
                                  color=0xFFD400)
            await msg.edit(embed=embed)


@tasks.loop(seconds=1)
async def updatedQuote():
    dt = datetime.datetime.now()
    if dt.minute == 0 and dt.second == 0:
        con = sqlite3.connect('data.db', isolation_level=None)
        cur = con.cursor()

        for i in range(1, f.getStockCount() + 1):
            price = f.getStockOnDB(i, 'price', 'Stock')
            quoteUpdate = random.randint(-11, 11)

            if price < 20000 and quoteUpdate < 0:
                quoteUpdate *= -1

            if price > 200000 and quoteUpdate > 0:
                quoteUpdate *= -1

            quoteUpdate += round(random.random(), 1)
            price = round(price + (price * quoteUpdate / 100), 0)
            cur.execute("UPDATE Stock SET quote = ? WHERE stock_id = ?", (quoteUpdate, i,))
            cur.execute("UPDATE Stock SET price = ? WHERE stock_id = ?", (price, i,))

        sendMsg = "주식시장이 갱신되었습니다!"

        await app.get_guild(1183299705082490930).get_channel(1183299705610977383).send(sendMsg)

        await app.get_guild(1153857606822154371).get_channel(1183408915887706124).send(sendMsg)
        await app.get_guild(1174964692054192188).get_channel(1174964692054192190).send(sendMsg)
        con.close()
        time.sleep(1)


app.run(token_Stocks.token)
