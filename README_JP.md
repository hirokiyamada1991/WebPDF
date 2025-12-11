
# WebPDF

WebPDF は、ブラウザ上で動作する X 線 PDF（Pair Distribution Function）解析ソフトです。  
PyScript と Pyodide を利用してブラウザ内で Python を実行しており、インストール不要で PDF 解析が可能です。

ライブ版：  
https://yamada-hiroki.com/software/pdf/index.html

---

## 特徴
- インストール不要でブラウザのみで動作  
- 原データは 2θ–強度（twotheta–intensity）形式 の XRD データに対応  
- 背景補正・正規化  
- フーリエ変換による G(r), S(Q), RDF の計算  
- Q 範囲、密度、エネルギー、ウィンドウ関数などを設定可能  
- ハイスループット測定/時分割測定向けの逐次処理  
- 結果をテキスト形式でダウンロード可能  

---

## マニュアル・サンプルデータ
公式マニュアルおよび example data は以下にあります：

https://yamada-hiroki.com/software.html

内容：  
- WebPDF の使い方  
- XRD のサンプルデータ  
- X線PDF解析用ツール  

---

## 使用方法
1. WebPDF を開く：  
   https://yamada-hiroki.com/software/pdf/index.html  
2. 2θ, 強度形式の XRD データ をアップロード  
3. 密度、エネルギー、Q 範囲、ウィンドウ関数などを設定  
4. **Calculate** を押して G(r), S(Q), RDF を計算  
5. 計算結果をテキストとしてダウンロード  

---

## 使用ライブラリ

WebPDF は PyScript + Pyodide によりブラウザ内で Python を実行しています。

実際に使用しているライブラリ：
- **NumPy**（数値計算）  
- **Scipy**（数値計算）  
- Python 標準ライブラリ  
- PyScript / Pyodide ランタイム  


Pyodide の第三者ライセンス一覧：  
https://pyodide.org/en/stable/project/licenses.html

---

## リポジトリ構成
- `index.html` — メイン UI  
- `main.py`, `calc_pdf.py` — PDF 計算ロジック  
- `example_data/` — サンプルデータ  
- `pyscript.toml` — PyScript 設定  
- `LICENSE` — MIT License  

---

## ライセンス
WebPDF は **MIT License** の下で公開されています。

Pyodide には BSD/MIT 系ライブラリが含まれます：
https://pyodide.org/en/stable/project/licenses.html

---

