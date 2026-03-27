# 予約サイト（Django）

## 概要
- 管理画面から予約枠を作成し、ユーザー画面で一覧表示・予約ができるミニ予約サイトです。<br>
- Djangoを使用してDB連携と二重予約防止を実装しています。

## 主な機能
- 予約枠一覧表示（DB連携）
- 満席制御（残り0は予約不可）
- 予約処理（POST）
- 二重予約防止（transaction.atomic + select_for_update）

## 予約の流れ
1. 日付を選択
2. 空き予約枠を表示
3. 予約ボタンで予約実行
4. 予約完了ページを表示

## 技術ポイント
- Django 'transaction.atomic'を使った二重予約防止
- 'select_for_update'による排他制御
- Bootstrapを使ったUI構築

## 使用技術
- Python / Django
- SQLite（開発用）
- HTML / CSS
- Bootstrap
- JavaScript
- Git / GitHub

## ディレクトリ構成

reservation_site/
├ images/              # README用スクリーンショット
├ reservation_site/    # Django設定
│  ├ __init__.py
│  ├ asgi.py
│  ├ settings.py
│  ├ urls.py
│  └ wsgi.py
├ reservations/        # 予約アプリ
│  ├ migrations/
│  ├ static/reservations/
│  │  ├ css/
│  │  └ js/
│  ├ templates/
│  │  ├ manage/
│  │  ├ registration/
│  │  └ reservations/
│  ├ __init__.py
│  ├ admin.py
│  ├ apps.py
│  ├ models.py
│  ├ tests.py
│  ├ urls.py
│  └ views.py
├ manage.py
└ README.md

## 画面

### 予約画面
<img src="images/reservation.png" width="700">

### 管理画面
<img src="images/admin.png" width="700">

### 削除確認
<img src="images/delete_confirm.png" width="700">

## セットアップ
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver
