# python build_dictionary_from_sop.py --from_ym 201601 --to_ym 201812 --start_point 0

import pandas as pd
import os
from datetime import datetime as dt
from datetime import timedelta as td
from dateutil.relativedelta import relativedelta
import argparse
from eunjeon import Mecab
import textlib as tl

SOP_PATH = 'd:\\SOP'
SOP_EXTRACT_COLS = ['요청월','고객사', '사업단위', '서비스유형(중)', '서비스유형(소)', '제목', '처리담당세부그룹', '조치내역']
MERGED_SOP_FILE = 'sop_merged.xlsx'
CORPORA_FILE = 'skt_words_sop.dat'

arg_parser = argparse.ArgumentParser(description='build dictionary from sop')
arg_parser.add_argument("--from_ym", help="from date : YYYYMM", type=str)
arg_parser.add_argument("--to_ym", help="to date : YYYYMM", type=str)    
arg_parser.add_argument("--start_point", help="0(처음부터), 1(merge후부터)", type=int, default=0)    
args = arg_parser.parse_args()    

# from_date 부터 to_date까지 yyyymm 포맷의 날짜 리스트 반환
def enum_date_period(from_date, to_date):
    i = 0
    mths = []
    while(True):
        ym = dt.strptime(from_date, '%Y%m') + relativedelta(months=i)
        mths.append(ym.strftime('%Y%m'))   
        if ym == dt.strptime(to_date, '%Y%m'):
            break
        i += 1         
    return mths


# from_date 부터 to_date까지의 sop 파일(yyyymm.xls)을 pandas dataframe 포맷으로 merge
def merge_sop(from_date, to_date, output_file=None):
    dfs = []

    for ym in enum_date_period(from_date, to_date):    
        df = pd.read_excel(os.path.join(SOP_PATH, f'{ym}.xls'), sheet_name='장애티켓')
        df = df[(df['서비스유형(대)'] == 'Application') & \
            ((df['사업단위'] == 'Swing') | (df['사업단위'] == 'BSwing') | (df['사업단위'] == 'TSwing') | \
            (df['사업단위'] == 'UKey') | (df['사업단위'] == 'TUKey') | (df['사업단위'] == 'BUKey'))]
        df['요청월'] = ym
        df = df[SOP_EXTRACT_COLS]
        dfs.append(df)
        
        print(f'{ym} completed!')
        
    all_df = pd.concat(dfs)      

    if output_file is not None:
        writer = pd.ExcelWriter(MERGED_SOP_FILE)
        all_df.to_excel(writer, 'Sheet1', index=False)
        writer.save()

    return all_df

# dataframe으로부터 문장 추출 (제목 & 조치내역)
def extract_texts(sop_df):
    title = sop_df['제목']
    repair = sop_df[sop_df['조치내역'].isnull() == False]['조치내역']

    return pd.concat([title, repair], ignore_index=True)
        

if __name__ == '__main__':
    from_ym = args.from_ym
    to_ym = args.to_ym
    start_point = args.start_point

    if start_point == 0:
        print('start merging sop list...')
        merged_sop_df = merge_sop(from_ym, to_ym, MERGED_SOP_FILE)
        print('completed merging sop list.')
    else:
        print('start loading sop list...')        
        merged_sop_df = pd.read_excel(MERGED_SOP_FILE, sheet_name='Sheet1')
        print('completed loading sop list.')

    try:
        os.remove(CORPORA_FILE)
    except FileNotFoundError:
        pass

    mecab = Mecab()

    print('start writing corpora...')
    texts = extract_texts(merged_sop_df)    

    with open(CORPORA_FILE, 'w', encoding='utf-8') as f:    
        for i,d in enumerate(texts):
            cleansed = tl.clean_text(d)
            sentences = tl.sentence_segment(cleansed)
        
            tl.write_corpora(sentences, f, mecab)

    print('completed writing corpora...')


