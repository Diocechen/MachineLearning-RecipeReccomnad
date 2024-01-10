import pandas
import pyodbc as odbc
from ultralytics import YOLO
import AdjustImageSize as AIS

conn_str = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=DESKTOP-SMMSPV3;'
    r'DATABASE=RecipeDatabase;'
    r'Trusted_Connection=yes;'
)

#真正意義上的字典~~
ENtoCHDic = { 'Potato' : '馬鈴薯',
             'Carrot' : '紅蘿蔔',
             'Cabbage':'高麗菜',
             'Pumpkin':'南瓜',
             'Broccoli':'花椰菜'}

conn = odbc.connect(conn_str)
cursor = conn.cursor()

def predict_begin(image_path):
    model = YOLO('C:/Python/yoloTrained/best.pt')
    results = model.predict(source=image_path, save=True, device = 0)
    names = model.names

    # 建立一個空的字典來儲存結果
    result_dict = {}
    
    # 計算每個類別的數量
    for result in results:
        # 如果該類別已經在字典中，則增加數量
        for c in result.boxes.cls:
            if names[int(c)] in result_dict:
                result_dict[names[int(c)]] += 1
            else:
                result_dict[names[int(c)]] = 1
    #print(result_dict)
    return result_dict

if __name__ == '__main__':
    #AIS.resize_image('C:/Python/input/beef-stew-potatoes-carrots-3-l.jpg','C:/Python/inputAdjusted/beef-stew-potatoes-carrots-3-l.jpg',640)
    
    results = predict_begin('C:/Python/input/beef-stew-potatoes-carrots-3-l.jpg')
    #results containing a dictionary, which stores the ingredients found in input image.

    #But here's a big problem, the class names are English but the ingredient names are Chinese!
    #How can we fix that??? see top

    #Reccord scanned ingredients
    currentIng = []
    for result, amount in results.items():
        print(ENtoCHDic[result], amount)
        currentIng.append(ENtoCHDic[result])

    currentResultDict = {}
    searchID = 0
    for ing in currentIng:
        sql = """SELECT R.Recipe_Name, R.Recipe_ID
                FROM Ingredients AS I, Recipes AS R, Recipe_Ingredients AS IR
                WHERE I.Ingredient_Name LIKE ?
                AND IR.Ingredient_ID = I.Ingredient_ID
                AND IR.Recipe_ID = R.Recipe_ID"""
        s = '%'+ing+'%'
        val = (s)
        cursor.execute(sql, val)

        # 進入Dictionary 去除重複查詢到的食譜
        for row in cursor.fetchall():
            currentResultDict[str(row[0]),str(row[1])] = searchID
            searchID += 1

    #輸出推薦食譜
    for recipe, id in currentResultDict.items():
        print(recipe[0].rstrip(),recipe[1])

    searchInput = ''
    while(searchInput != '0'):
        print('--------------------------------------------------')
        searchInput = input('進入查詢，輸入上述食譜查詢或輸入數字0離開查詢:')
        
        if searchInput != '0':
            try:
                sql = """SELECT R.Recipe_Name, I.Ingredient_Name, RI.Amount
                        FROM Recipes AS R, Recipe_Ingredients AS RI, Ingredients AS I
                        WHERE RI.Recipe_ID = ?
                        AND RI.Recipe_ID = R.Recipe_ID
                        AND RI.Ingredient_ID = I.Ingredient_ID"""

                cursor.execute(sql, searchInput)
                searchResult = cursor.fetchall()

                print(str(searchResult[0][0]).rstrip())
                for row in searchResult:
                    print(row[1], row[2])
            except:
                continue

    # 關閉連線
    cursor.close()
    conn.close()
        

    
    
     





