#!/bin/bash
# 获取当前日期，格式为 YYYYMMDD
current_date=$(date +%Y%m%d)

git add .
git commit -m "updated${current_date}_xk"
git remote set-url origin https://github.com/ksayus/PCSMT-2.git
git branch -M main
git push -u origin main -f
