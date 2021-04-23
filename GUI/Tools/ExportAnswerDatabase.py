import os
import sqlite3
from xlsxwriter.workbook import Workbook

if __name__=="__main__":
    os.chdir(os.path.split(os.path.realpath(__file__))[0])
    dbaddr=input("请输入数据库 answers.db 的位置：").strip()
    db=sqlite3.connect(dbaddr)
    try:
        res=db.execute("SELECT * FROM ALL_ANSWERS")
    except sqlite3.OperationalError:
        print("数据库中无ALL_ANSWERS表？")
    else:
        with Workbook("answers.xlsx") as workbook:
            sheet=workbook.add_worksheet("题库")
            sheet.write(0,0,"问题")
            sheet.merge_range("B1:E1","答案",workbook.add_format({'align':"center"}))
            i=1
            for res_e in res.fetchall():
                question=str(res_e[0])
                answers=str(res_e[1]).split("#")
                sheet.write(i,0,question)
                for j,answer in enumerate(answers):
                    j=j+1
                    sheet.write(i,j,answer)
                i=i+1
    db.close()    
    print("在文件 answers.xlsx 中导出题库完成")
