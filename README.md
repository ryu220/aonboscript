# あおんぼ台本AI

あおんぼ脳をインストールした高品質な台本生成ツールです。

## 機能

- 参考台本に基づいた高品質な台本生成
- 動画テーマに合わせたカスタマイズ
- SEO最適化
- 文字数指定可能
- ナレッジ統合機能

## 使用方法

1. Claude APIキーを入力
2. 参考台本を入力
3. 動画テーマを設定
4. サムネタイトルを入力
5. SEOキーワードを設定
6. 文字数を指定
7. 必要に応じてナレッジを追加
8. 「台本を生成」ボタンをクリック

## 技術スタック

- Python
- Streamlit
- Anthropic Claude API

## セットアップ

1. リポジトリをクローン
```bash
git clone [リポジトリURL]
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

3. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

4. アプリケーションを起動
```bash
streamlit run streamlit_app.py
```

## ライセンス

MIT License 