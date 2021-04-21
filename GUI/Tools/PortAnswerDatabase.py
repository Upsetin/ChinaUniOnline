import os
import csv
import sqlite3

if __name__=="__main__":
    os.chdir(os.path.split(os.path.realpath(__file__))[0])
    csvpath=input("请输入原版程序题库（csv文件）的位置：").strip()
    d=list()
    with open(file=csvpath,mode="r",encoding="utf-8") as reader:
        file=csv.reader(reader)
        for row in file:
            d.append(row)
    db=sqlite3.connect("answers.db")
    try:
        db.execute("CREATE TABLE 'ALL_ANSWERS' (QUESTION TEXT NOT NULL UNIQUE,ANSWER TEXT NOT NULL)")
    except sqlite3.OperationalError:
        print("数据库中似乎已存在 ALL_ANSWERS 表？")
    for d_ in d:
        if len(d_)==2:
            question=str(d_[0])
            answer="#".join(str(d_[1]).replace("[","").replace("]","").replace("'","").strip().split(", "))
            db.execute("INSERT OR REPLACE INTO 'ALL_ANSWERS' (QUESTION,ANSWER) VALUES ('%s','%s')" %(question,answer))
    db.commit()
    db.close()
    print("转换完成，脚本文件夹下的 answers.db 即为GUI版本所需题库")
    