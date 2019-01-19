import requests
import json
import re
import json


def get_goods(gjz, page_count, price, sort, sales_filete, pd_filter):
    """
    获取指定关键字的商品
    :param gjz: String 关键字
    :param page_count:  int 需要获取多少也
    :param price: String 价格区间， 默认None代表不筛选， 否则 pricce = 'price,10,100'
    :param sort: String 排序 default综合， _credit评分， _sales销量， price价格从低到高， _price价格从高到低
    :param sales_filete: list sales_filete销量区间 [10,1000]
    :param pd_filter: int 过滤拼团数量
    :return:
    """
    headers = {
        'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
        # 'Host': 'apiv3.yangkeduo.com'
    }
    data = {'goods_list': []}


    # 开始循环获取商品
    for page in range(1, page_count + 1):
        url = 'http://apiv3.yangkeduo.com/search?q=%s&page=%s&size=50&requery=0&list_id=search_UHpDve&sort=%s' % (
            gjz, page, sort)
        if price:
            url += '&filter=%s' % price
        response = requests.get(url=url, headers=headers)
        # 所有商品的列表
        print(response.text)
        good_list = json.loads(response.text)

        # 开始获取商品
        for good in good_list.get('items'):
            # 商品ID
            goods_id = good['goods_id']

            # 标题链接
            link = 'http://mobile.yangkeduo.com/goods.html?goods_id=%s' % goods_id
            # 销量
            sales = good['sales']
            if sales_filete[1]:
                if not sales_filete[0] < sales < sales_filete[1]:
                    continue
            # 价格
            t = list(str(good['normal_price']))
            t.insert(-2, '.')
            normal_price = float(''.join(t))
            # 当前可拼数量, 及名称
            good_data = get_good_info(goods_id)

            mall_id = good_data['mall_id']

            good_group = get_goods_group(goods_id)
            mall_data = get_mall_info(mall_id)
            data['goods_list'].append(good_data)

    return data


# 获取当前商品以拼数量
def get_good_info(good_id):
    """
    获取指定商品的当前拼单人数，以及商品名称
    :param good_id: 商品ID
    :return: （商品名称， 拼单人数）
    """
    headers = {
        'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
    }
    response = requests.get(url='http://apiv4.yangkeduo.com/v5/goods/{}?pdduid='.format(good_id), headers=headers)
    data = json.loads(response.text)
    return data

    # response = requests.get(url='http://mobile.yangkeduo.com/goods.html?goods_id=%s' % good_id, headers=headers)
    # json_find = re.findall('window.rawData=\s+(?P<n>{.+});', response.text)
    # if json_find:
    #     data = json.loads(json_find[0])
    #     return data['initDataObj']['goods']['goodsName'], data['initDataObj']['goods']['localGroupsTotal']
    # else:
    #     return '', 0
def get_goods_group(good_id):
    """
    获取指定商品的当前拼单人数，以及商品名称
    :param good_id: 商品ID
    :return: （商品名称， 拼单人数）
    """
    headers = {
        'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
    }
    response = requests.get(url='http://apiv4.yangkeduo.com/v2/goods/{}/local_group?pdduid='.format(good_id), headers=headers)
    data = json.loads(response.text)
    return data


def get_mall_info(mall_id):
    """
    获取指定商品的当前拼单人数，以及商品名称
    :param good_id: 商品ID
    :return: （商品名称， 拼单人数）
    """
    headers = {
        'User-Agent': 'android Mozilla/5.0 (Linux; Android 4.4.2; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36  phh_android_version/3.23.0 phh_android_build',
    }
    response = requests.get(url='http://apiv4.yangkeduo.com/mall/{}/info?pdduid='.format(mall_id), headers=headers)
    data = json.loads(response.text)
    return data


if __name__ == '__main__':
    gjz, page_count, price, sort, sales_filete = '四川泡菜', 1, None, '_sales', [0, 0]
    print(get_goods(gjz, page_count, price, sort, sales_filete, 0))
    # get_price_qj('羽绒服')