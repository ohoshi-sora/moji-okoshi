#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d venv ]; then
    echo "初回セットアップ: 仮想環境を作成します"
    if ! python3 -m venv venv; then
        echo "仮想環境を作れませんでした。Python 3 をインストールしてください。"
        read -n 1 -s -r -p "何かキーを押すと閉じます"
        exit 1
    fi
fi

source venv/bin/activate

# requirements.txt が前回インストール時から変わっていたら入れ直す
if ! cmp -s requirements.txt venv/.requirements-installed; then
    echo "初回セットアップ: 依存ライブラリをインストールします(数分かかります)"
    if ! pip install -r requirements.txt; then
        echo "インストールに失敗しました。上のエラーを確認してください。"
        read -n 1 -s -r -p "何かキーを押すと閉じます"
        exit 1
    fi
    cp requirements.txt venv/.requirements-installed
fi

python main.py || read -n 1 -s -r -p "異常終了しました。何かキーを押すと閉じます"
