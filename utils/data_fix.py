import pymysql
import xlrd
import decimal

table_wait_fix = 'data_201804'
store_base = 'store_baseinfo'
product_base = 'product_baseinfo'

# basic util
def mysql_connect(ip,username,password,database):
    # 打开数据库连接
    db = pymysql.connect(ip, username, password, database ,use_unicode=True, charset="utf8")

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    return db,cursor

def excel_read(path):
    workbook = xlrd.open_workbook(path)
    return workbook

def sheet_read(workbook,sheet_name):
    sheet = workbook.sheet_by_name(sheet_name)
    return sheet
# basic util test
def sheet_read_test():
    path = '/Users/lvyufeng/PycharmProjects/eb_crawler/utils/2018年04月度报表批注.xlsx'
    workbook = excel_read(path)
    print(workbook.sheet_names())
    sheet = sheet_read(workbook,'3.1')
    print(sheet)
    pass

# sheet_read_test()

# query_util
def query_store_id(cursor,store_name,website):
    sql = 'SELECT storeActualId FROM ' + store_base + ' WHERE storeName = %s AND platform = %s'
    try:
        # 执行SQL语句
        cursor.execute(sql,(store_name,website))
        # 获取所有记录列表
        results = cursor.fetchall()
        if len(results) == 1:
            return results[0][0]
        else:
            return [i[0] for i in results]
    except Exception as e:
        print("Error: unable to fetch data",e)
        return None
    pass

def query_product_id(cursor,store_id,product_name):
    sql = 'SELECT productActualID FROM ' + product_base + ' WHERE storeActualID = %s AND productName = %s'
    try:
        # 执行SQL语句
        cursor.execute(sql,(store_id,product_name))
        # 获取所有记录列表
        results = cursor.fetchall()
        return results[0][0]
    except Exception as e:
        # print("Error: unable to fetch data", e)
        return None
    pass

def query_store_product_ids(cursor,store_id):
    sql = 'SELECT productActualID,std_stdPrice,monthSaleCount,isValid FROM ' + table_wait_fix + ' WHERE storeActualID = %s'
    try:
        # 执行SQL语句
        cursor.execute(sql,store_id)
        # 获取所有记录列表
        results = cursor.fetchall()
        return [list(i) for i in results]
    except Exception as e:
        # print("Error: unable to fetch data", e)
        return None
    pass

def query_all_ids(platform,sheet_name):
    path = '/Users/lvyufeng/PycharmProjects/eb_crawler/utils/2018年04月度报表批注.xlsx'
    db, cursor = mysql_connect('139.224.112.239', 'root', '1701sky', 'ebmis_db')
    workbook = excel_read(path)
    sheet = sheet_read(workbook, sheet_name)
    product_id = None
    datas = []
    for i in range(3,sheet.nrows):
        # print(sheet.cell_value(i,6))
        store_id = query_store_id(cursor, sheet.cell_value(i,6),platform)
        if type(store_id) == list:
            for id in store_id:
                product_id = query_product_id(cursor, id, sheet.cell_value(i, 1))
                if product_id:
                    break
            print(sheet.cell_value(i, 0), store_id, product_id)
        else:
            product_id = query_product_id(cursor, store_id, sheet.cell_value(i,1))
            print(sheet.cell_value(i,0),store_id,product_id)
        datas.append({
            'productActualID':product_id,
            'monthSaleCount':int(sheet.cell_value(i,3)),
            'productPromPrice':sheet.cell_value(i,4),
            'std_stdPrice':sheet.cell_value(i,4),
            'isValid':0,
        })
    db.close()

    return datas
    pass

# query_util test
def query_util_test():
    db,cursor = mysql_connect('139.224.112.239','root','1701sky','ebmis_db')
    store_id = query_store_id(cursor,'天猫超市')
    print(store_id)
    # product_id = query_product_id(cursor,store_id,'陈吉旺福 重庆小麻花512g 袋装独立小包装糕点心零食特产手工制作')
    # print(product_id)
    db.close()
    pass
# query_util_test()

# update_utils
def update_single_product(db,cursor,data):
    # SQL 更新语句
    update_sql = "UPDATE " + table_wait_fix + " SET "
    where_condition = " WHERE productActualID = '%s'" % (data['productActualID'])
    data.pop('productActualID')
    mid = ','.join([key + "=" + "'%s'" % (str(data[key])) for key in data.keys()])
    try:
        # 执行SQL语句
        cursor.execute(update_sql + mid + where_condition)
        # 提交到数据库执行
        db.commit()
    except Exception as e:
        # 发生错误时回滚
        print(e)
        db.rollback()
    pass

# compute util
def compute_store_price(store_id,actual_total):
    db, cursor = mysql_connect('localhost', 'root', '19960704', 'ebmis_db')
    product_ids = query_store_product_ids(cursor,store_id)
    result = []
    product_valid_totals = [i[1]*decimal.Decimal(i[2]) if i[3]==1 else 0 for i in product_ids]
    product_invalid_totals = [i[1]*decimal.Decimal(i[2]) if i[3]==0 else 0 for i in product_ids]
    product_prices = [i[1] for i in product_ids]
    # print(product_ids)
    valid_total = sum(product_valid_totals)
    invalid_total = sum(product_invalid_totals)

    sub = actual_total - invalid_total
    nums = [int(i/valid_total*sub/product_prices[product_valid_totals.index(i)]) if product_ids[product_valid_totals.index(i)][3]==1 else 0 for i in product_valid_totals]

    for index,item in enumerate(product_ids):
        if item[3] == 0:
            result.append(item)
        elif nums[index] != 0:
            item[2] = nums[index]
            result.append(item)
    # print(result)
    # return product_ids
    total = sum([i[1]*decimal.Decimal(i[2]) for i in result])
    if product_ids[product_prices.index(min(product_prices))] in result:
        product_ids[product_prices.index(min(product_prices))][2] += int((actual_total - total) / min(product_prices))
    else:
        item = product_ids[product_prices.index(min(product_prices))]
        item[2] = int((actual_total - total) / min(product_prices))
        result.append(item)

    # print(min(product_prices))
    total = sum([i[1] * decimal.Decimal(i[2]) for i in result])



    return result
    pass
def compute_top20_store(platform,sheet_name):
    path = '/Users/lvyufeng/PycharmProjects/eb_crawler/utils/2018年04月度报表批注.xlsx'
    db, cursor = mysql_connect('139.224.112.239', 'root', '1701sky', 'ebmis_db')
    workbook = excel_read(path)
    sheet = sheet_read(workbook, sheet_name)
    datas = []
    for i in range(2,sheet.nrows):
        # print(sheet.cell_value(i,6))
        store_id = query_store_id(cursor, sheet.cell_value(i,1),platform)
        result = compute_store_price(store_id,decimal.Decimal(sheet.cell_value(i,3) * 10000))
        print(i,store_id,result)
        # datas.append(store_id)
    db.close()
    # print(datas)
    return datas


# compute_top20_store('Tmall','2.1')
compute_top20_store('TaoBao','2.2')

# for different sheet fix
def top20_sku_fix():
    datas = []
    db,cursor = mysql_connect('localhost','root','19960704','ebmis_db')
    datas.extend(query_all_ids('Tmall', '3.1'))
    datas.extend(query_all_ids('TaoBao', '3.2'))

    # print(datas)
    for i in datas:
        update_single_product(db,cursor,i)
    # datas = query_all_ids('TaoBao', '3.2')
    # print(datas)
    pass

def top20_store_fix():
    pass

def sanPinYiBiao_fix():
    pass

def category_fix():
    pass

# top20_sku_fix()
