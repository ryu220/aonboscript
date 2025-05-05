# あおんぼ台本AI

あおんぼ脳をインストールした高品質な台本生成ツールです。

## 機能

- 参考台本に基づいた高品質な台本生成
- 動画テーマに合わせたカスタマイズ
- SEO最適化
- 文字数指定可能
- ナレッジ統合機能

## 使用方法

1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. GitHubアカウントでログイン
3. リポジトリを選択してデプロイ
4. サイドバーに表示される「Claude API Key」欄に、[Anthropic](https://console.anthropic.com/)で取得したAPIキーを入力
5. 必要な情報を入力して台本を生成

## 必要な情報

- Claude API Key（Anthropicのウェブサイトで取得）
- 参考台本
- 動画テーマ
- サムネタイトル
- SEOキーワード
- 出力する台本の文字数（300〜5000文字）
- 台本に反映させるナレッジ（任意）

## 注意事項

- APIキーは安全に管理してください
- 生成された台本は自動的に保存されません
- 大量の台本を生成する場合は、APIの使用制限に注意してください

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