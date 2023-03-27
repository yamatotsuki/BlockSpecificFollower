
# ==============================
# 指定したTwitterアカウントと、そのアカウントがフォロー中のアカウントをブロックするプログラムです
# 同階層のBlock.csvにブロックしたいアカウントのIDを指定して実行すると、最終ブロック結果が出力されます
# 2023/03/27時点では事前にTwitterAPIで利用申請したアカウントのみ実行可能です
# ==============================

import csv
import tweepy
import datetime

# キーの指定（事前にTwitterAPIで利用申請したアカウントのキー）
BEARER_TOKEN        = "AAAAAAAAAAAAAAAAAAAAADbudgEAAAAAYLp%2BC3HPKgw4ZvkzCBVypqscXTA%3DdJJEDRJ2APdBJNxt60fgSd6OlqLjoedBdw42UX7jozsb3QoUmR"
API_KEY             = "Y89QKRcYAuRZkpZQ40elUSVAG"
API_SECRET          = "vpcVg70stkpY3ckLt71D2TSkgKPZTrGNa2Kf8jjmd1Mf3LYC0K"
ACCESS_TOKEN        = "1012156962618814464-zfSanWLQESslj47Byx8ghRdiEHA7Ka"
ACCESS_TOKEN_SECRET = "Rkzqx1Zo5u4mfi1ZAIJkAbmpaai6q3wEAHAxmum8GSE6k"

# ブロック済みリスト
blocked_list = []

# ==============================
# 指定したアカウントのフォロー者を取得
# num_id [i/ ] フォロー者を取得したいアカウントの数値id
# ==============================
def GetFollowingUserIDs(num_id):
    # 返却用に取得したデータを保管
    results = []

    # フォロー者を全取得
    for followers_date in  tweepy.Cursor(api.get_friends, user_id=num_id).items():
        # tweet検索結果取得
        if followers_date != None:
            obj = {}
            obj["num_id"]  = followers_date.id      # 数値のuser_ID
            obj["name"]    = followers_date.name    # アカウントの表示名
            results.append(obj)
        else:
            results.append('')

        dt_now = datetime.datetime.now()
        print(dt_now.strftime('%Y/%m/%d %H:%M:%S'), 'フォロー者',obj["name"],'を取得')

    print('フォロー数', len(results))

    # 結果出力
    return results

# ==============================
# ブロック用関数
# num_id [i/ ] フォロー者を取得したいアカウントの数値id
# ==============================
def BlockWithID(num_id):
    try:
        # すでにブロック済みか確認(リストに含まれていたらスキップ)
        if int(num_id) in blocked_list:
            return False
        else:
            # ブロック
            api.create_block(user_id=num_id)
            blocked_list.append(num_id)
            return True
    except tweepy.errors.TweepyException as e:
        print('何らかのエラー。処理は継続させます。',e)
        return False


# ==========================
# Twitterオブジェクトの生成
# ==========================
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit = True) # API制限がかかったら自動で待つモード

# =======================
# 処理開始
# =======================
# 自身のブロック済みリストを取得
blocked_list = api.get_blocked_ids()
print('ブロック済み人数:', len(blocked_list))

# =======================
# CSVファイル読み込み
# =======================
with open('./Block.csv', 'r', encoding='shift-jis', newline='') as f:
    csvreader = csv.reader(f)
    rows = [row for row in csvreader]

# CSVに書かれたユーザーIDを読み込む
for user in rows:
    block_cnt = 0   # ブロックした人数

    try:
        # CSVのユーザーIDから内部固有のユーザーIDを取得
        # [0]→ユーザーID
        # [1]→ユーザー名(任意：確認用)
        user_context = api.get_user(screen_name=user[0])
        print('CSVから取得したB対象者:',user[0])

        # フォロー一覧取得
        follower_ids = GetFollowingUserIDs(user_context.id)
        
        # =======================
        # フォロー者を回す
        # =======================
        print('フォロー数（空白なら失敗）:', len(follower_ids))
        for follower_id in follower_ids:
            # ユーザーIDが取得できなければ失敗
            if ('' == follower_id):
                print('idが取得できませんでした。',user[0],'の処理をスキップします。')
                break
            # ブロック
            if (True == BlockWithID(follower_id["num_id"])):
                block_cnt+=1
                dt_now = datetime.datetime.now()
                print(dt_now.strftime('%Y/%m/%d %H:%M:%S'), follower_id["name"],'をブロックしました')
                continue
            else:
                print(follower_id["name"], 'はブロック済みです') 
                continue

        # CSVで指定したアカウントもブロック
        if (True == BlockWithID(user_context.id)):
            block_cnt+=1
            dt_now = datetime.datetime.now()
            print(dt_now.strftime('%Y/%m/%d %H:%M:%S'), user_context.name,'をブロックしました')

    except tweepy.errors.TweepyException as e:
        print('何らかのエラー。処理は継続させます。',e)
        continue

    print('====================================')
    print(user_context.name, 'がフォローしているアカウントを新たに', block_cnt, '個ブロックしました')
    print('====================================\n')
