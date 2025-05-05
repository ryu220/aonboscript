# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import json
import time
import requests

# ページ設定を最初に配置
st.set_page_config(
    page_title="あおんぼ台本AI",
    page_icon="📝",
    layout="wide"
)

load_dotenv()

# カスタムCSSの追加
st.markdown("""
    <style>
    /* メインカラー */
    :root {
        --primary-color: #1e88e5;
        --secondary-color: #64b5f6;
        --background-color: #f5f9ff;
        --text-color: #333333;
    }
    
    /* 全体のスタイル */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* ヘッダー */
    h1 {
        color: var(--primary-color);
        border-bottom: 2px solid var(--secondary-color);
        padding-bottom: 10px;
    }
    
    /* サイドバー */
    .css-1d391kg {
        background-color: white;
        border-right: 1px solid var(--secondary-color);
    }
    
    /* フォーム要素 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid var(--secondary-color);
        border-radius: 5px;
        padding: 8px;
    }
    
    /* ボタン */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color);
    }
    
    /* タブ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0px 0px;
        gap: 1rem;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* プログレスバー */
    .stProgress > div > div > div > div {
        background-color: var(--primary-color);
    }
    
    /* アラートメッセージ */
    .stAlert {
        border-radius: 5px;
        padding: 10px;
    }
    
    /* テキストエリア */
    .stTextArea textarea {
        background-color: white;
        border: 1px solid var(--secondary-color);
        border-radius: 5px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'generation_status' not in st.session_state:
    st.session_state.generation_status = "idle"  # idle, generating, editing, completed
if 'final_script' not in st.session_state:
    st.session_state.final_script = ""
if 'error' not in st.session_state:
    st.session_state.error = None

st.title("あおんぼ台本AI")
st.markdown("あおんぼ脳をインストールした高品質な台本生成ツール")

# サイドバー
with st.sidebar:
    st.header("API設定")
    api_key = st.text_input(
        "Claude API Key", 
        type="password", 
        help="Anthropicのウェブサイトで取得したAPIキーを入力してください。APIキーの取得方法は[こちら](https://console.anthropic.com/)を参照してください。"
    )
    
    if not api_key:
        st.warning("APIキーを入力してください。APIキーはAnthropicのウェブサイトで取得できます。")
    else:
        try:
            # APIキーの検証
            client = Anthropic()
            client.api_key = api_key
            # 簡単なテストリクエストを送信
            client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            st.success("APIキーが有効です")
        except Exception as e:
            st.error(f"APIキーが無効です: {str(e)}")
    
    st.markdown("---")
    st.markdown("© 2025 あおんぼ台本AI - あおんぼ脳をインストールしたツール")

# メインコンテンツ
tab1, tab2 = st.tabs(["入力", "結果"])

with tab1:
    st.header("台本情報入力")
    st.markdown("台本生成に必要な情報を入力してください")

with st.form("script_form", clear_on_submit=False):
    reference_script = st.text_area(
        "参考台本", 
        height=300,
        placeholder="参考にしたい既存の台本を入力してください",
        help="参考にしたい既存の台本を入力してください"
    )
    
    video_theme = st.text_input(
        "動画テーマ",
        placeholder="動画のテーマや主題",
        help="動画のテーマや主題を入力してください"
    )
    
    thumbnail_title = st.text_input(
        "サムネタイトル",
        placeholder="動画のサムネイルに表示されるタイトル",
        help="動画のサムネイルに表示されるタイトルを入力してください"
    )
    
    seo_keywords = st.text_input(
        "SEOキーワード",
        placeholder="検索エンジン最適化のためのキーワード（カンマ区切り）",
        help="検索エンジン最適化のためのキーワードをカンマ区切りで入力してください"
    )
    
    character_count = st.number_input(
        "出力する台本の文字数",
        min_value=300,
        max_value=5000,
        value=1000,
        step=100,
        help="300〜5000文字の間で指定してください"
    )
    
    knowledge = st.text_area(
        "台本に反映させるナレッジ（任意）",
        height=200,
        placeholder="台本に含めたい専門用語、事実、データ、特定の情報などを入力してください",
        help="台本に含めたい専門用語、事実、データ、特定の情報などを入力してください"
    )
    
    submit_button = st.form_submit_button(
        "台本を生成",
        type="primary",
        use_container_width=True
    )
    
    if submit_button:
        st.warning("台本の生成を開始します。この処理には数分かかる場合があります。")

def analyze_script(reference_script):
    """台本の特徴を分析するプロンプトを生成"""
    prompt = f""" 以下の台本を分析し、以下の要素を抽出してください：

キャラクターの口調と文末表現
台本の構成パターン
特徴的な表現や言い回し
会話のリズムやテンポ
ト書きの特徴
分析対象の台本：

{reference_script}
分析結果は、以下の形式で出力してください：

ANALYSIS:
1. 口調と文末表現: [分析結果]
2. 構成パターン: [分析結果]
3. 特徴的表現: [分析結果]
4. 会話リズム: [分析結果]
5. ト書き特徴: [分析結果]
"""
    return prompt

def generate_writing_prompt(reference_script, video_theme, thumbnail_title, seo_keywords, character_count, knowledge):
    prompt = f"""
あなたは高度に最適化された文章生成を行うAIアシスタントです。このプロンプトに従って、ユーザーの真の意図を深く理解し、メディア形式に最適化された高品質な文章を生成してください。

@THEME: "{video_theme}"
@THUMBNAIL_TITLE: "{thumbnail_title}"
@SEO_KEYWORDS: "{seo_keywords}"
@TARGET_LENGTH: "{character_count}文字"
@KNOWLEDGE_INTEGRATION: ```
{knowledge}
```

@REFERENCE_SCRIPT: ```
{reference_script}
```

以上の情報を基に、高品質な台本を作成してください。

【重要】以下の点を厳密に守ってください：
1. 与えられたナレッジ（@KNOWLEDGE_INTEGRATION）を必ず台本の中心に据えてください
2. 参考台本（@REFERENCE_SCRIPT）は、あくまで文体や構成の参考としてのみ使用してください
3. 台本は必ず完全な形で生成し、中略や後略は一切使用しないでください
4. 文字数は必ず{character_count}文字にしてください（±3%以内）
5. 文字数が超過する場合は、内容を要約するのではなく、不要な部分を削除してください
6. 文字数が不足する場合は、内容を膨らませて{character_count}文字に近づけてください
7. 台本の最後に「文字数: [実際の文字数]」を必ず記載してください
8. 文字数の計算には、スペースや改行も含めてください
9. 最初から最後まで最初から最後まで最初から最後まで全て全て全て生成して提出すること

文字数の厳守は最も重要な要件です。必ず{character_count}文字±3%以内に収めてください。
"""
    return prompt

def generate_editing_prompt(draft_script, reference_script, analysis, character_count):
    prompt = f"""
以下の台本を、分析結果に基づいて編集してください。

@ANALYSIS_RESULTS:
{analysis}

@DRAFT_SCRIPT: ```
{draft_script}
```

@REFERENCE_SCRIPT: ```
{reference_script}
```

以下の点に注意して編集してください：
1. 口調、文末表現、構成パターンの再現度を最大限に高める
2. 特徴的な表現や言い回しの使用を確認・修正
3. 会話のリズムやテンポを調整
4. ト書きの特徴を完全に一致させる
5. 余計な説明や改善点は削除し、台本本文のみを残す
6. 台本は必ず完全な形で生成し、中略や後略は一切使用しないでください
7. 文字数は必ず{character_count}文字±3%以内に調整してください
8. 文字数の計算には、スペースや改行も含めてください
9. 最初から最後まで最初から最後まで最初から最後まで全て全て全て生成して提出すること

文字数の厳守は最も重要な要件です。必ず{character_count}文字±3%以内に収めてください。
最終的な台本のみを出力し、編集過程や説明は含めないでください。
"""
    return prompt

def generate_content_guidance_prompt(video_theme, thumbnail_title, seo_keywords, knowledge):
    """コンテンツの方向性をガイドするプロンプト"""
    prompt = f""" 以下の情報を基に、台本の方向性をガイドしてください：

@THEME: "{video_theme}" @THUMBNAIL_TITLE: "{thumbnail_title}" @SEO_KEYWORDS: "{seo_keywords}" @KNOWLEDGE_INTEGRATION: ``` {knowledge}


以下の点に注意して、台本の方向性をガイドしてください：
1. 動画テーマに沿った内容を展開
2. ナレッジを効果的に活用し、説得力のある内容を構築
3. サムネタイトルとSEOキーワードを自然に組み込み、視聴者の興味を維持
4. 元台本の特徴を活かしつつ、新しい内容で独自性を確保
"""
    return prompt

def generate_script(api_key, reference_script, video_theme, thumbnail_title, seo_keywords, character_count, knowledge):
    try:
        # APIクライアントの初期化
        client = Anthropic()
        client.api_key = api_key
        
        # 台本分析
        st.session_state.generation_status = "analyzing"
        st.info("台本の分析を開始しました...")
        st.progress(0.2)
        
        max_retries = 3
        retry_delay = 10  # リトライ間隔を10秒に延長
        
        # 分析フェーズ
        for attempt in range(max_retries):
            try:
                analysis_prompt = analyze_script(reference_script)
                analysis_response = client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=4000,
                    temperature=0.3,
                    system="あなたは台本分析の専門家です。与えられた台本の特徴を詳細に分析してください。",
                    messages=[
                        {"role": "user", "content": analysis_prompt.encode('utf-8').decode('utf-8')}
                    ]
                )
                analysis = analysis_response.content[0].text
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    st.warning(f"分析中にエラーが発生しました。{retry_delay}秒後に再試行します...")
                    time.sleep(retry_delay)
                else:
                    raise e
        
        # コンテンツ方向性のガイド
        st.session_state.generation_status = "guiding"
        st.info("コンテンツの方向性を決定しています...")
        st.progress(0.3)
        
        for attempt in range(max_retries):
            try:
                guidance_prompt = generate_content_guidance_prompt(video_theme, thumbnail_title, seo_keywords, knowledge)
                guidance_response = client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=4000,
                    temperature=0.3,
                    system="あなたはコンテンツ戦略の専門家です。与えられた情報を基に、台本の方向性をガイドしてください。",
                    messages=[
                        {"role": "user", "content": guidance_prompt.encode('utf-8').decode('utf-8')}
                    ]
                )
                guidance = guidance_response.content[0].text
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    st.warning(f"ガイド生成中にエラーが発生しました。{retry_delay}秒後に再試行します...")
                    time.sleep(retry_delay)
                else:
                    raise e
        
        # 台本生成
        st.session_state.generation_status = "generating"
        st.info("台本の生成を開始しました...")
        st.progress(0.5)
        
        for attempt in range(max_retries):
            try:
                writing_prompt = generate_writing_prompt(
                    reference_script, 
                    video_theme, 
                    thumbnail_title, 
                    seo_keywords, 
                    character_count, 
                    knowledge
                )
                
                draft_response = client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=8000 if character_count > 5000 else 4000,  # 文字数に応じてトークン数を調整
                    temperature=0.7,
                    system="あなたは台本作成の専門家です。与えられた指示に従って高品質な台本を作成してください。",
                    messages=[
                        {"role": "user", "content": writing_prompt.encode('utf-8').decode('utf-8')}
                    ]
                )
                
                draft_script = draft_response.content[0].text
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    st.warning(f"台本生成中にエラーが発生しました。{retry_delay}秒後に再試行します...")
                    time.sleep(retry_delay)
                else:
                    raise e
        
        # 台本編集
        st.session_state.generation_status = "editing"
        st.info("台本の編集・改善を開始しました...")
        st.progress(0.8)
        
        for attempt in range(max_retries):
            try:
                editing_prompt = generate_editing_prompt(
                    draft_script,
                    reference_script,
                    analysis,
                    character_count
                )
                
                final_response = client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=8000 if character_count > 5000 else 4000,  # 文字数に応じてトークン数を調整
                    temperature=0.3,
                    system="あなたは台本の編集・添削の専門家です。分析結果に基づいて台本を改善してください。",
                    messages=[
                        {"role": "user", "content": editing_prompt.encode('utf-8').decode('utf-8')}
                    ]
                )
                
                final_script = final_response.content[0].text
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    st.warning(f"編集中にエラーが発生しました。{retry_delay}秒後に再試行します...")
                    time.sleep(retry_delay)
                else:
                    raise e
        
        st.session_state.generation_status = "completed"
        st.success("台本の生成が完了しました！")
        st.progress(1.0)
        return final_script, None
        
    except Exception as e:
        st.session_state.generation_status = "idle"
        return None, str(e)

if submit_button:
    if not api_key:
        st.error("Claude APIキーを入力してください")
    elif not reference_script:
        st.error("参考台本を入力してください")
    elif not video_theme:
        st.error("動画テーマを入力してください")
    elif not thumbnail_title:
        st.error("サムネタイトルを入力してください")
    elif not seo_keywords:
        st.error("SEOキーワードを入力してください")
    else:
        final_script, error = generate_script(
            api_key,
            reference_script,
            video_theme,
            thumbnail_title,
            seo_keywords,
            character_count,
            knowledge
        )
        
        if error:
            st.session_state.error = error
        else:
            st.session_state.final_script = final_script

with tab2:
    # ステータス表示用のコンテナ
    status_container = st.empty()
    
    if st.session_state.generation_status == "generating":
        status_container.info("台本を生成中...")
        st.progress(0.3)
    elif st.session_state.generation_status == "editing":
        status_container.info("台本を編集・改善中...")
        st.progress(0.7)
    elif st.session_state.error:
        status_container.error(f"エラーが発生しました: {st.session_state.error}")
    elif st.session_state.final_script:
        status_container.success("台本の生成が完了しました！")
        st.progress(1.0)
        
        # スタイルの適用
        st.markdown("""
        <style>
        .stTextArea textarea {
            background-color: #ffffff !important;
            color: #000000 !important;
            font-family: "Yu Gothic", "Meiryo", sans-serif !important;
            font-size: 16px !important;
            line-height: 1.8 !important;
            padding: 20px !important;
            border: 2px solid #e0e0e0 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
        }
        .stTextArea textarea:disabled {
            opacity: 1 !important;
            cursor: text !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 文字数の表示
        actual_length = len(st.session_state.final_script)
        length_diff = abs(actual_length - character_count)
        length_diff_percent = (length_diff / character_count) * 100
        
        if length_diff_percent <= 3:
            st.success(f"文字数: {actual_length}文字 (目標: {character_count}文字, 差: {length_diff}文字, 誤差: {length_diff_percent:.1f}%)")
        else:
            st.warning(f"文字数: {actual_length}文字 (目標: {character_count}文字, 差: {length_diff}文字, 誤差: {length_diff_percent:.1f}%)")
        
        st.text_area(
            "台本",
            value=st.session_state.final_script,
            height=600,
            disabled=True,
            key="script_output"
        )
        
        # ボタンのスタイルも改善
        st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #45a049;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("コピー", key="copy_button"):
                st.success("クリップボードにコピーしました")
                
        with col2:
            if st.download_button(
                label="ダウンロード",
                data=st.session_state.final_script,
                file_name=f"台本_{video_theme}.txt",
                mime="text/plain"
            ):
                st.success("ダウンロードが開始されました")
        
        if st.button("新規作成", key="new_script_button"):
            st.session_state.final_script = ""
            st.session_state.error = None
            st.session_state.generation_status = "idle"
            st.rerun()
    else:
        st.info("台本が生成されると、ここに表示されます")