import csv
import json
import glob

files = glob.glob("csv/*.csv")
files.sort()

output = {}

for file in files:
    csvdata = []
    with open(file, encoding='shift-jis', newline='') as f:
        reader = csv.reader(f)
        csvdata = [row for row in reader]

    header_count = 20
    csv_header = csvdata[header_count]

    # 各項目を保持
    title = 0
    for i in range(header_count+1, len(csvdata)):
        if len(csvdata[i]) < 1:
            continue
        受渡日 = csvdata[i][6]
        受渡日_sprit = 受渡日.split('/')
        受渡日_年 = 受渡日_sprit[0]
        受渡日_月 = 受渡日_sprit[1]
        受渡日_日 = 受渡日_sprit[2]

        if not 受渡日_年 in output:
            output[受渡日_年] = {}

        if not 受渡日_月 in output[受渡日_年]:
            output[受渡日_年][受渡日_月] = {}

        if not 受渡日_日 in output[受渡日_年][受渡日_月]:
            output[受渡日_年][受渡日_月][受渡日_日] = []

        output[受渡日_年][受渡日_月][受渡日_日].append({
            '銘柄コード/種別': csvdata[i][0].strip(),
            '銘柄': csvdata[i][1],
            '約定日': csvdata[i][3],
            '取引': csvdata[i][5],
            '損益金額/徴収額': int(csvdata[i][11]),
        })

# 取引年でソートする
output = dict(sorted(output.items()))

with open('sbi_soneki.json', 'w') as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

損益 = 0
for year in output:
    損益_年毎 = 0
    for month in output[year]:
        損益_月毎 = 0
        for day in output[year][month]:
            損益_日毎 = 0

            取引_日 = output[year][month][day]
            for 取引 in 取引_日:
                取引種別 = 取引['銘柄コード/種別']

                # 利益計算
                if 取引種別.isdecimal():
                    損益_日毎 += 取引['損益金額/徴収額']
                elif '還付' in 取引種別:
                    損益_日毎 += 取引['損益金額/徴収額']
                elif '徴収' in 取引種別:
                    損益_日毎 -= 取引['損益金額/徴収額']
                else:
                    if 取引['取引'] == '投信分配金':
                        損益_日毎 += 取引['損益金額/徴収額']
                    elif 取引['取引'] == '国内債券利金':
                        損益_日毎 += 取引['損益金額/徴収額']
                    else:
                        print('[WRNING] なんか 徴収でも還付でもないものがあります')
                        print(取引)
            損益_月毎 += 損益_日毎
            # print(year + '/' + month + '/ ' +day)
            # print(損益_日毎)

        損益_年毎 += 損益_月毎
        # print(year + '年' + month + '月')
        # print(損益_月毎)

    損益 += 損益_年毎
    print(year + '年損益', str(損益_年毎) + '円')

print('= = = = = =')
print('現状損益', 損益, '円')
