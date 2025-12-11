# WebPDF

WebPDF is a browser-based software for X-ray Pair Distribution Function (PDF) calculation.  
It runs entirely in modern web browsers using PyScript and Pyodide, requiring no installation.

Live version:  
https://yamada-hiroki.com/software/pdf/index.html

---

## Features
- PDF calculation in the browser (no installation required)
- Supports X-ray total scattering data (Q–I(Q))
- Background subtraction, normalization, and Fourier transformation
- Outputs S(Q), G(r), RDF, and related quantities
- Adjustable Q-range, window functions, and analysis parameters
- Download of processed results for further analysis

---

## How to Use
1. Open: https://yamada-hiroki.com/software/pdf/index.html  
2. Upload your scattering data (and optional background)  
3. Set analysis parameters (Q-range, energy, density, Lorch window, etc.)  
4. Click **Calculate**  
5. Download S(Q), G(r), RDF, and other results as text files

---

## Libraries Used

WebPDF runs on **PyScript** and **Pyodide**, which provide a Python environment compiled to WebAssembly.

主要ライブラリ（Pyodide に含まれるもの）:

- **NumPy** – numerical operations  
- **SciPy** – Fourier transform, filtering  
- **Matplotlib** – plotting (used internally by Pyodide if needed)  
- **Pyodide standard packages** – file I/O, array operations  
- **PyScript runtime** – browser integration and event handling  

これらのライブラリは **BSD / MIT 系ライセンス**の下で配布されています。

Pyodide に含まれるすべての第三者ライセンスは以下で公開されています：  
https://pyodide.org/en/stable/project/licenses.html

WebPDF の利用における MIT/BSD ライブラリの再配布要件は、  
上記リンクを明記することで満たされます。

---

## Files in This Repository
- `index.html` — main UI  
- `main.py`, `calc_pdf.py` — core PDF calculation routines  
- `example_data/` — sample input  
- `pyscript.toml` — PyScript configuration  
- `LICENSE` — MIT License  

---

## License
WebPDF is distributed under the **MIT License**.

This project uses Pyodide, which includes third-party libraries under BSD/MIT licenses:  
https://pyodide.org/en/stable/project/licenses.html

---
