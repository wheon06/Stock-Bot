def addStockList(cur):
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (1, '태혁건설', 100000, 0, 'TCON'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (2, '예찬인력', 100000, 0, 'YHPO'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (3, 'HC중공업', 100000, 0, 'HCHV'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (4, '현섭강화농업', 100000, 0, 'HSGA'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (5, 'GO케미컬', 100000, 0, 'GOCH'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (6, 'SM컴퍼니', 100000, 0, 'SMCO'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (7, '성민항공', 100000, 0, 'SAIR'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (8, '민규푸드', 100000, 0, 'MFOD'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (9, '주엽용역', 100000, 0, 'JSVC'))
    cur.execute("INSERT OR IGNORE INTO Stock VALUES(?, ?, ?, ?, ?)", (10, '현진소프트웨어', 100000, 0, 'HSFT'))
