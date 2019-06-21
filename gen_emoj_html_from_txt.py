# -*- coding: utf-8 -*-
import codecs
import os
import sys
import re
import json
emoj_data = {}
def gen_emoj_html():
	fsave = open("emoji_index.html",'w',encoding='gbk')

	with open("emo_config.txt","r",encoding='utf-8') as f:
		lines = f.readlines()
		index = 0
		for line in lines:
			index = index+1
			nfirst = line.find('(\"')
			nfirst_1 = line.find('\")')

			name = line[nfirst+2:nfirst_1]
			print (name)
			nsecond = line.find('(\"',nfirst_1)
			nsecond_2 = line.find('\")',nsecond)
			tip = line[nsecond+2:nsecond_2]
			print(tip)

			line_item = {}
			line_item.update({'value':name})
			line_item.update({'tip':tip})
			line_item.update({"image":"%03d.png"%(index)})

			emoj_data[index] = line_item
		
	with codecs.open('emoj_data.py',"w",'utf-8') as fs:
		json.dump(emoj_data, fs, ensure_ascii=False, indent=4, sort_keys=True)


if __name__ =='__main__':
	gen_emoj_html()