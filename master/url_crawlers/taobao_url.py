import spider
import requests
import json
import time
import random
import datetime
import pymongo
import hashlib
import redis

class TaoBaoUrlFetcher(spider.Fetcher):
    """
    fetcher module, only rewrite url_fetch()
    """
    def url_fetch(self, priority: int, url: str, keys: dict, deep: int, repeat: int, proxies=None):
        headers = keys['headers'] if 'headers' in keys else {}
        params = keys['params']
        if repeat > 1:
        #     # print(url)
            time.sleep(5)
        #     return -1, False, None
        else:
            time.sleep(random.choice((1,0.5)))
        try:
            proxies = {
                "http": proxies,
                "https": proxies,
            }
            response = requests.get(url,params=params,headers=headers,proxies=proxies,timeout = 5)

            if response.status_code == 200:
                return 1, True, (response.text,response.cookies)

            else:
                # print('状态码：{0}'.format(response.status_code), url)

                return -1, False, None
        except:
            # print('加载超时，重新写入Queue')
                return 0, False, None


class TaoBaoUrlParser(spider.Parser):
    """
    parser module, only rewrite htm_parse()
    """
    def __init__(self, max_deep=0):
        super(TaoBaoUrlParser, self).__init__(max_deep)
        self.category = ['124374002', '50020306', '50004711', '125226012', '50020299', '125060020', '50258012', '50016817', '123920001', '50025676', '50016806', '125256004', '125220009', '125076018', '125244008', '50013095', '126000001', '123188007',  '50015135', '125020022', '50004721', '50008047', '50009879', '50020319', '50050732', '123330001', '125204013', '124488006', '50025690', '50005948', '50009836', '50012190', '123258002', '121382038', '50018598', '50010535', '124466012', '123222004', '124174011', '50050694', '124848002', '125208008', '50012191', '50604012', '50009821', '124230011', '123634001', '50050395', '125226013', '50009858', '50015262', '50018801', '50010420', '125224009', '50013098', '50012991', '122666001', '50166001', '50015700', '124506003', '50138004', '50009557', '50013076', '124250006', '125048026', '125194002', '50013062', '50326001', '50009919', '50280002', '50020316', '50050725', '50023332', '50050687', '125088024', '50013057', '50008910', '50016796', '125060021', '50003923', '50009849', '50016850', '50025674', '125112030', '50050695', '50150002', '50013074', '50026317', '50050643', '50050728', '50004785', '50015198', '125284013', '50166002', '123190007', '50050393', '50009854', '50013000', '50016429', '50012195', '50009984', '125098026', '50009830',  '50015761', '50012990', '50008063', '125088017', '50050579', '50598001', '50013096', '50013092', '50050423', '50776032', '50050416', '50050147', '50016807', '125110023', '50015227', '50009856', '125260008', '50050428', '50008435', '50050372', '50002256', '123224005', '50020318', '124464007', '50020303', '50025683', '50026800', '124332006', '50528001', '50013082', '125216013', '50016091', '50015272', '50020310', '50012590', '50015218', '124484016', '50016818', '121484023', '50008628', '50023364', '124334003', '125226015', '50012988', '50050427', '50009839', '125286002', '50050698', '50025692', '50015214', '50015228', '125076017', '50394001', '125224006', '50015134', '50009843', '50050431', '124390001', '50013089', '50009983', '50018804', '50015211', '50026558', '50020304', '50009828', '50013185',  '50009560', '50012995', '50050382', '50008604', '50016848', '123190006', '50008617', '50018802', '121420038', '126472004', '123918001', '50050151', '50050396', '50009837', '50009857', '121422026', '50144001', '50025700', '124226017', '125268013', '50015704', '50050359', '50013100', '125210011', '50020300', '50013072', '50005945', '50013083', '50008908', '50007215', '124462015', '50016771', '50008432', '50050580', '50008630', '50015221', '50015207', '50016772', '50015197', '50050419', '50013067', '50050702', '50008624', '125200009', '125218010', '125228003', '50013061', '50015380', '50013087', '123922001', '50013085', '50020309', '50012186', '121408030', '50003251', '124500003', '50050425', '50050397', '50004709', '125020020', '50020312', '125044020', '50012989', '50013091', '50025699', '123236003', '50050150', '126412022', '121366039', '50015222', '124246009', '125084029', '50008612', '123218003', '50050420', '50018808', '123252002', '50050727', '50013088', '125098029', '50016422', '50050429', '121418019', '125040033', '125224010', '123248003', '50020311', '125092021', '50013075', '124458005', '50278005', '50050432', '125280010', '50050149', '50004783', '50008467', '121484022', '124174012', '125054019', '123222007', '125202009', '124228006', '50016443', '50026460', '50023334', '125236009', '50008430', '124498005', '50012992', '50026803', '125104027', '50050391', '50010891', '125260002', '50012196', '50008328',  '121448014', '125248005', '50008046',  '217305', '50166003', '124470001', '50013066', '50146001', '50008665', '125076013', '50015292', '50005773', '125242010', '50023066', '50015137', '125284014', '50050143', '125222011', '50552001', '124294001', '50013079', '50148001', '50025222', '50050669', '50050699', '50013103', '50015136', '121456017', '125114020', '121448015', '50026804', '50020320', '50025682', '50016852', '50050390', '125078026', '125042037', '50012998', '125224011', '121454038', '125218009', '50008649', '50026003', '124486012', '50012987', '50050724', '50020307', '50020323', '50009986', '50012999', '121404016', '125228012', '125268012', '50013084', '50015710', '50015715', '123190004', '50009861', '50003253', '124636001', '50015223', '50050731', '50013086', '50009562', '50146002', '50018812', '121470011', '50013090', '123256002', '126104013', '124466007', '125036027', '123238003', '121484024', '50150001', '50016845', '50005949', '50016847', '50020314', '50017138', '124476007', '50008674', '125230009', '50016853', '125060019', '50050415', '50020317', '50003860', '50025684', '50016801', '50023263',  '125258012', '50023331', '50023333', '50050693', '123210006', '125226016', '50018597', '124392005',  '50015717', '217308', '50008616', '50023044', '125284009', '50050672', '50011946', '124494004', '125216006', '50050667', '50008650', '50013064', '50012985', '50154001', '50020275', '50005776', '50015294', '125080007', '50013054', '217313', '210605', '50010550', '50050145', '123190005', '125236010', '50018837', '124488014', '50003404', '50026085', '50015209', '125200008', '125074026', '50009556', '125244010', '123220003', '124508011', '50016851', '50013065', '50152001', '125286001', '50008618', '124392004', '50018803', '126492001', '50008044', '50011943', '50020305', '50016854', '50009866', '50002766', '50012392', '50138003', '125112017', '50050421', '50015703', '124350003', '50050426', '50009860', '50015716', '125052025', '50019055', '124358002', '50023067', '50008613', '50012994', '50011942', '125036029', '50050413', '50050719', '50050394', '50017141', '50013093', '50009824', '123196007', '124456024', '121366028', '124348004', '50016236', '50015194', '50009898', '50005777', '50005946', '50050380', '125098025', '50016428', '125040021', '50020313', '50006762', '124372005', '50050383', '124478008', '50050578', '124240006', '50012993', '50013073', '50009846', '50010421', '124128007', '50020302', '50013078', '50050417', '124204011', '125672021', '50012943', '121416017', '50013101', '50050371', '50011947', '50012982', '50015962', '50013193', '50013152', '50050729', '124494008', '50016819', '50016235', '124388001', '124558013', '123210007', '123378001', '50015956', '124230012', '50002614', '50020298', '50003702', '50050701', '125020021', '50009859', '50023264', '123246002', '50009980', '50025680', '50013097', '125252002', '124216008', '50004784', '50005778', '50009981', '50050422', '123224003', '50013080', '124534019', '125092022', '123206005', '50013069', '50013094', '50050688', '50015711', '50023040', '123250002', '50008919', '125282004', '121408043', '125110019', '50020321', '50025687', '50025689', '50013081', '50013071', '50015196', '125268011', '123202003', '123244002', '124326002', '124432001', '124392002', '123194007', '50050730', '50009558', '124360005', '50016849', '123256001', '121454027', '123232002', '50013099', '50020296', '50050573', '125284012', '124146003', '50009979', '124204010', '50009841', '125226003', '50016427', '50013063', '50004710', '50020322', '50010566', '50012981', '50015219', '50012997', '50026316', '50015725', '50015213', '125084043', '50015755', '50009985', '50008431', '50050733',  '50050379', '50008625', '123196006', '120856009', '50012986', '50008651', '50008045', '50013068', '50012382', '124386002',  '50016846', '50328001', '125046003', '50018809', '123200008', '50050668', '50050434', '125208007', '50020315', '50006825', '125040022', '50016048', '125232009', '50015713', '125216012', '50013070', '50050385', '50050388', '50013102', '50008048', '50017231', '124464006', '50136009', '50015195', '124252006', '125032026', '126334003', '50556001', '50008623', '50020280', '50050424', '124092006', '50008433', '50012983', '50005774', '50050381', '50005947', '50050418', '123240003', '121364031', '50025691', '50009878', '123188001', '50008434', '50050146', '124356006', '125230008', '50015699', '50050414', '125094020', '50009835', '50016820', '124142014', '125022037', '50012996', '124484015', '50016855', '50009559', '50050734', '50013077', '50050430', '125098028', '50004720', '50020308', '50050433']
        pass

    def htm_parse(self, priority: int, url: str, keys: dict, deep: int, content: object):
        url_list = []
        sku_list = []
        text, cookies = content
        if '令牌为空' in text or '非法请求' in text:
            keys['params']['t'] = str(int(time.time() * 1000))
            keys['headers'] = {}
            keys['headers']['cookie'] = '; '.join([i + '=' + cookies.get(i) for i in cookies.keys()])
            src = cookies.get('_m_h5_tk').split('_')[0] + '&' + keys['params']['t'] + '&' + keys['params']['appKey'] + '&' + keys['params']['data']
            m = hashlib.md5()
            m.update(src.encode('utf-8'))
            keys['params']['sign'] = m.hexdigest()

            url_list.append((url, keys, priority - 1))
            return 0, url_list, sku_list
        elif '调用成功' in text:
            data = json.loads(text.replace('mtopjsonp1(', '').replace(')', ''))
            for i in data['data']['listItem']:
                if 'category' not in i:
                    continue
                else:
                    if i['userType'] == '0':#i['category'] in self.category and
                        sku_list.append({
                            '_id': i['item_id'],
                            'keyword' : keys['keyword'],
                            'website': keys['website']
                        })

            params_data = json.loads(keys['params']['data'])
            if params_data['page'] < int(data['data']['totalPage']):
                params_data['page'] = params_data['page'] + 1
                keys['params']['data'] = json.dumps(params_data,ensure_ascii=False)
                url_list.append((url,keys,priority - 1))

            return 1, url_list, sku_list



        # print(save_list)



class TaoBaoUrlSaver(spider.Saver):


    def __init__(self):
        self.count = 0
        client = pymongo.MongoClient('localhost')
        db = client['sku']
        self.collection = db['sku_ids_' + datetime.datetime.now().strftime('%Y%m')]
        self.r = redis.Redis.from_url("redis://202.202.5.140:6379", decode_responses=True)

        return


    def item_save(self, url: str, keys: dict, item: (list, tuple)):
        """
        save the item of a url, you can rewrite this function, parameters and return refer to self.working()
        """
        # item.update(keys)
        # pass
        try:
            self.collection.insert(item)
        except Exception as e:
            return -1

        # if self.count % 1000 == 0:
        #     self.db.commit()
        self.r.sadd('sku:'+keys['website'], item)
        return 1

class TaoBaoUrlProxieser(spider.Proxieser):

    def proxies_get(self):
        url = 'http://127.0.0.1:5010/get_all/?name=TaoBao_proxy'
        wb_data = requests.get(url)
        # print(wb_data.content)
        proxies = []
        for i in eval(wb_data.text):
            proxies.append(i)
        # print(len(proxies))
        return 0,proxies



