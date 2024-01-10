import pyodbc as odbc
import requests
from bs4 import BeautifulSoup

def get_ingredients_from_html():
    ingredients = []
    for group in soup.find_all('div', class_='group'):
        for ingredient in group.find_all('li', class_='ingredient'):
            #print(ingredient)
            ingredient_name = ingredient.find('div', class_='ingredient-name').text.replace("\n", "")
            ingredient_unit = ingredient.find('div', class_='ingredient-unit').text.replace("\n", "")
            try:
                group_name = group.find('div', class_='group-name').text
                ingredients.append({
                        'group_name': group_name,
                        'ingredient_name': ingredient_name,
                        'ingredient_unit': ingredient_unit
                    })
            except:
                ingredients.append({
                    'group_name': "食材",
                    'ingredient_name': ingredient_name,
                    'ingredient_unit': ingredient_unit
                })   
    return ingredients

conn_str = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=DESKTOP-SMMSPV3;'
    r'DATABASE=RecipeDatabase;'
    r'Trusted_Connection=yes;'
)

conn = odbc.connect(conn_str)
cursor = conn.cursor()

ingredientCurrentRecipe = {} # store all ingredient, each data store recipe that use this ingredient. Will be update.
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
recipeID = 100000
ingredientID = 0

while(recipeID < 100800):
    url = "https://icook.tw/recipes/" + str(recipeID)

    response = requests.get(url, headers = headers)

    soup = BeautifulSoup(response.text, "html.parser")

    recipeTitle = soup.find("h1", class_ = "title")
    
    #跳過失效網頁
    if recipeTitle == None: 
        recipeID += 1
        continue   
    
    CurrentRecipeIngredients = [] 

    #Recipe Table
    sql = "INSERT INTO Recipes (Recipe_ID, Recipe_Name) VALUES (?, ?)"
    val = (str(recipeID), recipeTitle.text)
    cursor.execute(sql, val)
    cursor.commit()

    ingredients = get_ingredients_from_html()

    #Ingredient Table
    #Prevent duplicate ingredients name in SQL, using unique.
    for ingredient in ingredients:
        try:
            sql = "INSERT INTO Ingredients (Ingredient_ID, Ingredient_Name) VALUES (?, ?)"
            val = (str(ingredientID), ingredient["ingredient_name"])
            cursor.execute(sql, val)
            cursor.commit()
            ingredientCurrentRecipe[ingredient["ingredient_name"]] =(str(recipeID), str(ingredientID), ingredient['ingredient_unit'])
        except:
            print("INSERT FAILED (FOUND DUPLICATED NAME)")
            print(str(ingredientID), ingredient["ingredient_name"])

        ingredientID += 1

    #Recipe_Ingredients Table
    for n, data in ingredientCurrentRecipe.items():
        if data[0] == str(recipeID):
            try:
                sql = "INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Amount) VALUES (?, ?, ?)"
                val = (recipeID, data[1], data[2])
                cursor.execute(sql, val)
                cursor.commit()
            except:
                print(recipeID, data[1], data[2])

    recipeID += 1

#if response.status_code == 200:
#    with open('outPut.html', 'w', encoding = 'utf-8') as f:
#        f.write(response.text)
#else:
#    print("讀取失敗")
    
#allIngredients = soup.find_all("li", class_ = "ingredient")
#for line in allIngredients:
#    ing = line.find("div", class_ = "ingredient-name")
#    ingAmount = line.find("div", class_ = "ingredient-unit")
#    print(ing.a.text,ingAmount.text)
    
#sql = "INSERT INTO Recipe_Ingredients (Recipe_ID, Ingredient_ID, Amount) VALUES (?, ?, ?)"
#val = (str(i), str(ingredientID), ingredient["ingredient_unit"])
#cursor.execute(sql, val)
#cursor.commit()