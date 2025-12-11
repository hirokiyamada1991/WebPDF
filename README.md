For the Japanese version of this document, see:  
[README_JP.md](README_JP.md)

# WebPDF

WebPDF is a browser-based software for X-ray Pair Distribution Function (PDF) analysis.  
It runs Python directly inside modern web browsers using PyScript and Pyodide, enabling PDF calculations without any installation.

Live version:  
https://yamada-hiroki.com/software/pdf/index.html

---

## Features
- Runs entirely in the browser — no installation required  
- Accepts raw XRD data in twotheta–intensity format  
- Background subtraction and normalization  
- Fourier transformation to obtain G(r), S(Q), RDF, and related functions  
- Adjustable parameters such as Q-range, density, X-ray energy, and window functions  
- Sequential processing for high-throughput or time-resolved PDF datasets  
- Export of processed results as text files  
- Interactive plotting using Bokeh for browser-based visualization  

---

## Documentation & Example Data

The official user manual and example datasets are available at:

https://yamada-hiroki.com/software.html

Includes:  
- WebPDF usage guide  
- Example XRD datasets  
- Tools for X-ray PDF analysis  

---

## How to Use
1. Open WebPDF:  
   https://yamada-hiroki.com/software/pdf/index.html  
2. Upload your raw XRD dataset in twotheta–intensity format  
3. Set analysis parameters such as Q-range, density, X-ray energy, and window functions  
4. Click "calculation ..." to compute G(r), S(Q), RDF, and related profiles  
5. Download the calculation results as text files  

---

## Libraries Used

WebPDF executes Python code through PyScript and Pyodide, providing a full Python environment inside the browser.

Libraries actually used:
- NumPy — numerical computations  
- SciPy — numerical routines and Fourier transform  
- Bokeh — interactive plotting in the browser  
- Python standard library  
- PyScript / Pyodide runtime  

Pyodide includes many third-party libraries under BSD/MIT family licenses.  
The full license list is available at:  
https://pyodide.org/en/stable/project/licenses.html

---

## Repository Structure
- `index.html` — Main user interface  
- `main.py`, `calc_pdf.py` — Core PDF calculation logic  
- `example_data/` — Example datasets  
- `pyscript.toml` — PyScript configuration  
- `LICENSE` — MIT License  

---

## License
WebPDF is distributed under the MIT License.

Pyodide and its bundled libraries are distributed under BSD/MIT-compatible licenses:  
https://pyodide.org/en/stable/project/licenses.html
