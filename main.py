
import pyscript
from pyscript import display, document
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np
import h5py
import os
import io
import math
from datetime import datetime

from pyweb import pydom
import asyncio
from scipy import interpolate
from scipy import fft
from scipy.fft import dst, idst
from pyodide.http import open_url
import ast
from pyodide.ffi.wrappers import add_event_listener
from pyodide.ffi import *

import json

from bokeh.embed import json_item
from bokeh.plotting import figure
from bokeh.models import HoverTool, ResetTool

import zipfile 

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from js import (
    CanvasRenderingContext2D as Context2d,
    ImageData,
    Uint8ClampedArray,
    console,
    document,
    window, 
    Bokeh, 
    JSON,
    Uint8Array,
)
from io import BytesIO
from calc_pdf import Calc_PDF_from_xy
from globalsv import global_vars
tes = Calc_PDF_from_xy()
plt.style.use("seaborn")
display("FFT-PDF Module created", target="load_engine")





## ファイル読み込み
async def handle_file_upload(e, id_selector, output_filename):
    print(f"Handling upload for: {output_filename}")
    filepath = str(pydom[f"#{id_selector}"][0].value)
    ext = os.path.splitext(os.path.basename(filepath))[1]

    file_list = e.target.files.to_py()
    if id_selector =="file-upload":
        select_id="select_upload" 
        id_max = "select_max"   
        id_label = "select_file"
    elif id_selector =="bg-upload": 
        select_id="select_bg" 
        id_max = "select_bg_max"
        id_label = "select_background_file"

    label = document.getElementById(id_label)

    label.innerText = os.path.basename(os.path.basename(filepath).split("\\")[-1])
    if ext == ".h5":
        for f in file_list:
            array_buffer = await f.arrayBuffer()
            uint8 = window.Uint8Array.new(array_buffer)
            data = bytes(uint8.to_py())
            with h5py.File(io.BytesIO(data), 'r') as f:
                data_num = (f["data"].shape[0])
                print(data_num)
                document.getElementById(select_id).max = data_num
                document.getElementById(select_id).min = 1
                document.getElementById(select_id).value = 1
                document.getElementById(id_max).value=  data_num
    elif (os.path.splitext(os.path.basename(filepath))[0]) == "":
        document.getElementById(select_id).max = 0
        document.getElementById(select_id).min = 0
        document.getElementById(select_id).value = 0
        document.getElementById(id_max).value=  0

        label = document.getElementById(id_label)
        label.innerText = "_"
    else:
        document.getElementById(select_id).max = 1
        document.getElementById(select_id).min = 1
        document.getElementById(select_id).value= 1
        document.getElementById(id_max).value= 1 
        for f in file_list:
            data = await f.text()
        with open(output_filename.replace(".h5", ".xy"), 'w') as f:
            f.write(data)


async def upload_file_and_show(e):
    print("upload_file_and_show")
    await handle_file_upload(e, "file-upload", "./data.h5")

async def upload_bg(e):
    await handle_file_upload(e, "bg-upload", "./bg.h5")

add_event_listener(document.getElementById("bg-upload"), "change", upload_bg)

add_event_listener(document.getElementById("file-upload"), "change", upload_file_and_show)

## ファイル読み込み Config
async def upload_config(e):
    print("upload_config")
    fileList = e.target.files.to_py()
    for f in fileList:
        data = await f.text()
        dict = ast.literal_eval(data)
    # 辞書を表示
    document.getElementById('enrgy').value = str(dict["energy_of_X-ray"])
    document.getElementById('atom_no').value = str(dict["atomNo[List]"])
    document.getElementById('atom_conc').value = str(dict["atomConc"])

    document.getElementById('density').value = str(dict["Density"])
    document.getElementById('polarize_f').value = str(dict["Polarization Factor"])
    document.getElementById('recoil_f').value = str(dict["Recoil Factor"])
    document.getElementById('q_range1').value = str(dict["Q range from"])
    document.getElementById('q_range2').value = str(dict["Q range to"])
    document.getElementById('max').value = str(dict["r Max"])
    document.getElementById('d_r').value = str(dict["delta-r"])
    document.getElementById('cut_off').value = str(dict["Cut off Distance"])


add_event_listener(document.getElementById("upload-config"), "change", upload_config)


def read_complete(event):
    text = document.getElementById("content")
    Element("text").write(f"{event.target.result}")

def prepare_canvas(width: int, height: int, canvas: pydom.Element) -> Context2d:
    ctx = canvas._js.getContext("2d")
    canvas.style["width"] = f"{width}px"
    canvas.style["height"] = f"{height}px"
    canvas._js.width = width
    canvas._js.height = height
    ctx.clearRect(0, 0, width, height)

    return ctx

def draw_image(ctx: Context2d, image: np.array) -> None:
    data = Uint8ClampedArray.new(to_js(image.tobytes()))
    width, height, _ = image.shape
    image_data = ImageData.new(data, width, height)
    ctx.putImageData(image_data, 0, 0)



async def clicked_calc_of_s(event):
    width, height = 140*4, 140*3
    try:
        await draw_s(width, height)
    except Exception as e:
        display(e, target="mpl", append=False)

async def clicked_calc_of_g(event):
    width, height = 140*4, 140*3
    try:
        await draw_g(width, height)
    except Exception as e:
        display(e, target="mpl", append=False)

async def  clicked_save (event):
    if tes.tt is None:
        document.getElementById("mpl").innerHTML = ""
        document.getElementById("mpl2").innerHTML = ""
        document.getElementById("mpl3").innerHTML = ""
        document.getElementById("mpl4").innerHTML = ""
        display("density は読み込まれていません", target="mpl")
        return 0
    
    params = {}

    filepath = str(pydom[f"#file-upload"][0].value)
    ext = os.path.splitext(os.path.basename(filepath))[1].lower()
    data_name_without_ext = os.path.splitext(os.path.basename(filepath))[0]
    if ext == ".h5":
        tes.intensityRaw, tes.tt = await load_h5_data("file-upload", "select_upload")
    else:
        if not filepath =="" :
            try:
                tes.tt, tes.intensityRaw = load_xy_data("data.xy")
            except:
                tes.bg_filename =""
                document.getElementById("mpl").innerHTML = ""
                document.getElementById("mpl2").innerHTML = ""
                document.getElementById("mpl3").innerHTML = ""
                document.getElementById("mpl4").innerHTML = ""
                display("Failed to load data", target="mpl")
        else:
            document.getElementById("mpl").innerHTML = ""
            document.getElementById("mpl2").innerHTML = ""
            document.getElementById("mpl3").innerHTML = ""
            document.getElementById("mpl4").innerHTML = ""
            display("Failed to load data", target="mpl")
            return -1

    params["filename"]= data_name_without_ext.split("\\")[-1]+"_"+ str(document.getElementById("select_upload").value) + ext
    params["count1"]= 1
    params["data"]={"tt":tes.tt,
    "intensityRaw":tes.intensityRaw}   

    # 背景ファイル処理
    filepath_bg = str(pydom[f"#bg-upload"][0].value)
    ext_bg = os.path.splitext(os.path.basename(filepath_bg))[1].lower()
    basename_without_ext = os.path.splitext(os.path.basename(filepath_bg))[0]
    tes.bg_filename = basename_without_ext.split("\\")[-1] 
    loaded_successfully = False
    if ext_bg == ".h5":
        try:
            tes.intensityBG, tes.tt_bg = await load_h5_data("bg-upload", "select_bg")
            loaded_successfully = True
        except:
            display("Failed to load back-ground data", target="mpl")
            return -1
    else:
        if not tes.bg_filename =="" :
            try:
                tes.tt_bg, tes.intensityBG = load_xy_data("bg.xy")
                basename = os.path.basename(filepath_bg)
                loaded_successfully = True
            except:
                tes.bg_filename =""
                document.getElementById("mpl").innerHTML = ""
                document.getElementById("mpl2").innerHTML = ""
                document.getElementById("mpl3").innerHTML = ""
                document.getElementById("mpl4").innerHTML = ""
                display("Failed to load Background", target="mpl")

    if loaded_successfully:
        params["filename_bg"]= basename_without_ext.split("\\")[-1] +"_"+ str(document.getElementById("select_bg").value)+ ext_bg
        params["count2"]= 1
        params["bg_factor"]=pydom["#bg_factor"][0].value
        params["bg_data"]={"tt":tes.tt_bg,
            "intensityRaw":tes.intensityBG}   # 背景データに置き換えてください
    else:
        params["filename_bg"]= ""
        params["count2"]= 0
        params["bg_factor"]= 1
        params["bg_data"]=None


    params["atomic_number"]= pydom["#atom_no"][0].value
    params["atomic_concentration"]= pydom["#atom_conc"][0].value
    params["energy"]= pydom["#enrgy"][0].value
    params["density"]= pydom["#density"][0].value
    params["polarization_factor"]=pydom["#polarize_f"][0].value
    params["recoil_factor"]= pydom["#recoil_f"][0].value
    params["scattering_factor_upper"]=pydom["#q_range1"][0].value
    params["scattering_factor_lower"]=pydom["#q_range2"][0].value
    params["r_max"]= pydom["#max"][0].value
    params["delta_r"]= pydom["#d_r"][0].value
    params["cutoff_distance"]= pydom["#cut_off"][0].value
            
    data_name = data_name_without_ext.split("\\")[-1]
    data_num = str(document.getElementById("select_upload").value)
    now_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    filename = data_name +"_num-"+ data_num +"_date-"+ now_time +"_" + ".npz"
    np.savez(filename, **params)
    # name = os.path.basename(path)

    # ファイル読み込み（バイナリ）
    with open(filename, "rb") as f:
        data = f.read()

    # JS向けにUint8Arrayとしてデータを変換
    buffer = window.Uint8Array.new(len(data))
    for i, byte in enumerate(data):
        buffer[i] = byte

    # MIMEタイプ：application/octet-streamが無難
    file = window.File.new([buffer], filename, {"type": "application/octet-stream"})

    # ダウンロードリンク作成と自動クリック
    url = window.URL.createObjectURL(file)
    link = document.createElement("a")
    link.href = url
    link.download = filename
    link.click()

async def clicked_load(event):

    document.getElementById("select_upload").value = ""
    document.getElementById("bg-upload").value=""
    
    input_file = document.createElement("input")
    input_file.type = "file"
    input_file.accept = ".npz"

    def handle_file(evt):
        file = evt.target.files.item(0)
        print(file)
        reader = window.FileReader.new()

        def onload(e):
            # ArrayBuffer ⇒ bytes に変換して NumPy に渡す
            buffer = reader.result.to_py()
            byte_io = io.BytesIO(buffer)

            data = np.load(byte_io, allow_pickle=True)

            print("Keys in npz file:")

            for key in data.files:
                print(f" - {key}")

            for key in data.files:
                value = data[key]
                print(f"\n【{key}】の内容:")
                print(value)

            # <input type="file"> の .value を JavaScriptで直接設定すると、
            # ユーザーが知らないうちにローカルファイルをアップロードできてしまうため、
            # これは HTMLのセキュリティ仕様上禁止されています。

            label = document.getElementById("select_file")
            label.innerText = os.path.basename("snap"+"\\" + str(data["filename"]))


            label = document.getElementById("select_background_file")
            label.innerText = os.path.basename("snap"+"\\" + str(data["filename_bg"]))
            tes.bg_filename = str(data["filename_bg"])


            document.getElementById("select_upload").min = 1
            document.getElementById("select_upload").max= 1
            document.getElementById("select_upload").value = 1
            document.getElementById("select_max").value = 1


            document.getElementById("select_bg").min = 1
            document.getElementById("select_bg").max= 1
            document.getElementById("select_bg").value = 1
            document.getElementById("select_bg_max").value = 1
            document.getElementById('bg_factor').value = str(data["bg_factor"])

            
            document.getElementById('enrgy').value = str(data["energy"])
            document.getElementById('atom_no').value = str(data["atomic_number"])
            document.getElementById('atom_conc').value = str(data["atomic_concentration"])
            document.getElementById('density').value = str(data["density"])
            document.getElementById('polarize_f').value = str(data["polarization_factor"])
            document.getElementById('recoil_f').value = str(data["recoil_factor"])
            document.getElementById('q_range1').value = str(data["scattering_factor_upper"])
            document.getElementById('q_range2').value = str(data["scattering_factor_lower"])
            document.getElementById('max').value = str(data["r_max"])
            document.getElementById('d_r').value = str(data["delta_r"])
            document.getElementById('cut_off').value = str(data["cutoff_distance"])


            tes.tt = data["data"].item()["tt"]
            tes.intensityRaw  = data["data"].item()["intensityRaw"]

            print("asdf")
            print(data["bg_data"])
            print(type(data["bg_data"]))
            print(data["bg_data"] == None)
            print(data["bg_data"] is None)

            if data["bg_data"] == None:
                pass
            else :
                tes.tt_bg = data["bg_data"].item()["tt"]
                tes.intensityBG  = data["bg_data"].item()["intensityRaw"]

            print("asdf")

        reader.onload = onload
        reader.readAsArrayBuffer(file)

    input_file.onchange = handle_file
    input_file.click()

def get_valid_index(input_id, dataset):
    try:
        index = int(document.getElementById(input_id).value) - 1  # 1始まり → 0始まり
        display(index)
        if index < 0:
            display("インデックスは1以上で指定してください。")
            raise ValueError("インデックスは1以上で指定してください。")
        if index >= dataset.shape[0]:
            display(f"インデックスが範囲外です（最大: {dataset.shape[0]}）")
            raise IndexError(f"インデックスが範囲外です（最大: {dataset.shape[0]}）")
        return index
    except Exception as e:
        display(f"インデックスエラー: {e}", target="mpl")
        return ValueError


async def load_h5_data(file_input_id, select_id):
    file_list = document.getElementById(file_input_id).files.to_py()

    for f in file_list:
        try:
            array_buffer = await f.arrayBuffer()
            uint8 = window.Uint8Array.new(array_buffer)
            data = bytes(uint8.to_py())
            with h5py.File(io.BytesIO(data), 'r') as h5f:
                dataset = h5f["data"]
                index = get_valid_index(select_id, dataset)
                intensity = np.array(dataset[index])
                tth = np.array(h5f["tth"])
                return intensity, tth
        except Exception as e:
            display(f"Failed to load HDF5: {e}", target="mpl")
            return None, None

def load_xy_data(filename):
    try:

        with open(filename, "r") as f:
            text = f.read()
        # すべての区切りをスペースに統一（例）
        text = text.replace(",", " ").replace("\t", " ")
        return np.loadtxt(io.StringIO(text)).T
    except Exception as e:
        display(f"Failed to load XY: {e}", target="mpl")
        # return None, None


async def draw_s(width, height):

    document.getElementById("mpl").innerHTML = ""
    document.getElementById("mpl2").innerHTML = ""
    document.getElementById("mpl3").innerHTML = ""
    document.getElementById("mpl4").innerHTML = ""
    # snap 判定
    filelabel = document.getElementById("select_file").innerText

    if filelabel == "_":
        display("ファイルが未選択または初期状態です", target="mpl")
        return 0
    elif "snap\\" in filelabel or "snap/" in filelabel:
        pass
    else:
        # 読み込み処理
        # Dataファイル処理
        filepath = str(pydom[f"#file-upload"][0].value)
        ext = os.path.splitext(os.path.basename(filepath))[1].lower()
        tes.tt, tes.intensityRaw = None, None

        if ext == ".h5":
            tes.intensityRaw, tes.tt = await load_h5_data("file-upload", "select_upload")
        else:
            if not filepath =="" :
                try:
                    tes.tt, tes.intensityRaw = load_xy_data("data.xy")
                except:
                    tes.bg_filename =""
                    display("Failed to load data", target="mpl")
            else:
                display("Failed to load data", target="mpl")
                return -1

        # 背景ファイル処理
        filepath_bg = str(pydom[f"#bg-upload"][0].value)
        ext_bg = os.path.splitext(os.path.basename(filepath_bg))[1].lower()
        basename_without_ext = os.path.splitext(os.path.basename(filepath_bg))[0]
        tes.bg_filename = basename_without_ext.split("\\")[-1] 

        if ext_bg == ".h5":
            try:
                tes.intensityBG, tes.tt_bg = await load_h5_data("bg-upload", "select_bg")
            except:
                display("Failed to load data", target="mpl")
                return -1
        else:
            if not tes.bg_filename =="" :

                print(tes.bg_filename)
                try:
                    tes.tt_bg, tes.intensityBG = load_xy_data("bg.xy")
                    basename = os.path.basename(filepath_bg)
                except:
                    tes.bg_filename =""
                    display("Failed to load Background", target="mpl")


    bg_factor= pydom["#bg_factor"][0].value
    atomList= pydom["#atom_no"][0].value
    atomConc= pydom["#atom_conc"][0].value
    
    enrgyX= pydom["#enrgy"][0].value

    density = pydom["#density"][0].value
    polarize_f= pydom["#polarize_f"][0].value
    recoil_f= pydom["#recoil_f"][0].value
    q_range1= pydom["#q_range1"][0].value
    q_range2= pydom["#q_range2"][0].value
    max     = pydom["#max"][0].value
    d_r     = pydom["#d_r"][0].value
    cut_off = pydom["#cut_off"][0].value

    tes.bg_factor = (float(bg_factor))
    tes.energyX = (float(enrgyX)*1000)
    tes.atomList = (list(map(int, atomList.split(",")))) 
    tes.atomConc = (list(map(float, atomConc.split(",")))) 
    tes.density  = (float(density))
    tes.pol  = (float(polarize_f))
    tes.recoil  = (float(recoil_f))
    tes.norm_min  = (float(q_range1))
    tes.norm_max  = (float(q_range2))
    tes.dr= (float(d_r))
    tes.r_max  = (float(max))
    tes.r_cut = (float(cut_off))
    
    #tes.SQ_run()
    tes.All_run()
    tes.BFT_smooth()
    
    console.log("Computing set ...")

    # raw intesity
    xr = tes.tt
    yr_org = tes.intensityRaw
    yr = tes.subtract_bg()

    

    hover_tool = HoverTool()
    hover_tool.tooltips=None
    TOOLTIPS = [("index", "$index"),("(x,y)", "($x, $y)")]    
    hover_tool.tooltips = TOOLTIPS


    p1 = figure(title="Raw",  x_axis_label='2θ/degree',y_axis_label='Intensity', background_fill_color="#fafafa")
    p1.add_tools(hover_tool)

    if not (tes.bg_filename == ""):
        p1.line(tes.tt_bg, tes.intensityBG*tes.bg_factor, legend_label="Background", line_color="olivedrab")
        p1.line(xr, yr_org, legend_label="Intensity", line_color="tomato")
    else:
        p1.line(xr, yr_org,line_color="tomato")
    

    hover_tool2 = HoverTool()
    hover_tool2.tooltips=None
    TOOLTIPS = [("index", "$index"),("(x,y)", "($x, $y)")]    
    hover_tool2.tooltips = TOOLTIPS
    # S(Q), bFTS(Q)
    p2 = figure(title="S(Q), bFTS(Q)", x_range=[0, tes.norm_max],  x_axis_label='Q/Å**-1',y_axis_label='S(Q)', background_fill_color="#fafafa")
    p2.add_tools(hover_tool2)
    p2.line(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_raw[tes.nn_min:]+1, line_color="tomato")
    #p2.line(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_bFT[tes.nn_min:]+1, legend_label="bFT",line_color="tomato" )
    #p2.line(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_raw[tes.nn_min:]+1, legend_label="raw",line_color="olivedrab")
    #p2.line(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_bFT-tes.iq_interpolate_raw[tes.nn_min:]-2, legend_label="residual",line_color="coral")



    # Gr

    hover_tool3 = HoverTool()
    # p3 = figure(title="qq, (y1 y2)", x_range=[0,tes.r_max],  x_axis_label='r/Å',y_axis_label='G(r)', background_fill_color="#fafafa",width=width, height=height)
    p3 = figure(x_range=[0, tes.norm_max] ,  x_axis_label='Q/Å**-1' ,y_axis_label='Intensity',background_fill_color="#fafafa",width=width, height=height)
    p3.add_tools(hover_tool3)
    p3.line(tes.qq,  tes.intensityCorr_norm_value,  legend_label="X-ray total scattering" ,  line_color="tomato" )
    p3.line(tes.qq,  tes.sum_comp_total,            legend_label="Form foctor + Compton" ,     line_color="olivedrab" )


    hover_tool4 = HoverTool()
    p4 = figure(x_range=[0, tes.norm_max] ,x_axis_label='Q/Å**-1' ,y_axis_label='Intensity',background_fill_color="#fafafa",width=width, height=height)
    p4.add_tools(hover_tool4)
    p4.line(tes.qq, tes.intensityCorr_norm_value, legend_label="X-ray total scattering" ,                         line_color="tomato" )
    p4.line(tes.qq, tes.f2sum,                    legend_label="<f2>",                         line_color="olivedrab" )
    p4.line(tes.qq, tes.comp_total,               legend_label="Compton" ,                           line_color="black" )



    document.getElementById("mpl").innerHTML = ""
    document.getElementById("mpl2").innerHTML = ""
    document.getElementById("mpl3").innerHTML = ""
    document.getElementById("mpl4").innerHTML = ""
    

    filepath =  (str(pydom["#file-upload"][0].value))
    basename_without_ext = os.path.splitext(os.path.basename(filepath))[0]
    if "snap\\" in filelabel or "snap/" in filelabel:
        tes.dl_filename   = filelabel.split("\\")[-1]
    else:
        tes.dl_filename = basename_without_ext.split("\\")[-1]


    p1.width = width
    p2.width = width
    p3.width = width
    p4.width = width
    
    p1.height = height
    p2.height = height
    p3.height = height
    p4.height = height


    p_json = json.dumps(json_item(p1, "mpl"))
    Bokeh.embed.embed_item(JSON.parse(p_json))

    p_json = json.dumps(json_item(p2, "mpl2"))
    Bokeh.embed.embed_item(JSON.parse(p_json))

    p_json = json.dumps(json_item(p3, "mpl3"))
    Bokeh.embed.embed_item(JSON.parse(p_json))

    p_json = json.dumps(json_item(p4, "mpl4"))
    Bokeh.embed.embed_item(JSON.parse(p_json))



async def draw_g(width, height):

    document.getElementById("mpl").innerHTML = ""
    document.getElementById("mpl2").innerHTML = ""
    document.getElementById("mpl3").innerHTML = ""
    document.getElementById("mpl4").innerHTML = ""

    # snap 判定
    filelabel = document.getElementById("select_file").innerText

    if filelabel == "_":
        display("ファイルが未選択または初期状態です", target="mpl")
        return 0
    elif "snap\\" in filelabel or "snap/" in filelabel:
        pass
    else:
        # 読み込み処理
        # Dataファイル処理
        filepath = str(pydom[f"#file-upload"][0].value)
        ext = os.path.splitext(os.path.basename(filepath))[1].lower()
        tes.tt, tes.intensityRaw = None, None

        if ext == ".h5":
            tes.intensityRaw, tes.tt = await load_h5_data("file-upload", "select_upload")
        else:
            if not filepath =="" :
                try:
                    tes.tt, tes.intensityRaw = load_xy_data("data.xy")
                except:
                    tes.bg_filename =""
                    display("Failed to load data", target="mpl")
            else:
                display("Failed to load data", target="mpl")
                return -1

        # 背景ファイル処理
        filepath_bg = str(pydom[f"#bg-upload"][0].value)
        ext_bg = os.path.splitext(os.path.basename(filepath_bg))[1].lower()
        basename_without_ext = os.path.splitext(os.path.basename(filepath_bg))[0]
        tes.bg_filename = basename_without_ext.split("\\")[-1] 

        if ext_bg == ".h5":
            try:
                tes.intensityBG, tes.tt_bg = await load_h5_data("bg-upload", "select_bg")
            except:
                display("Failed to load data", target="mpl")
                return -1
        else:
            if not tes.bg_filename =="" :

                print(tes.bg_filename)
                try:
                    tes.tt_bg, tes.intensityBG = load_xy_data("bg.xy")
                    basename = os.path.basename(filepath_bg)
                except:
                    tes.bg_filename =""
                    display("Failed to load Background", target="mpl")


    bg_factor= pydom["#bg_factor"][0].value
    atomList= pydom["#atom_no"][0].value
    atomConc= pydom["#atom_conc"][0].value
    
    enrgyX= pydom["#enrgy"][0].value

    
    density = pydom["#density"][0].value
    polarize_f= pydom["#polarize_f"][0].value
    recoil_f= pydom["#recoil_f"][0].value
    q_range1= pydom["#q_range1"][0].value
    q_range2= pydom["#q_range2"][0].value
    max     = pydom["#max"][0].value
    d_r     = pydom["#d_r"][0].value
    cut_off = pydom["#cut_off"][0].value

    tes.bg_factor= (float(bg_factor))
    tes.energyX= (float(enrgyX)*1000)
    tes.atomList= (list(map(int, atomList.split(",")))) 
    tes.atomConc= (list(map(float, atomConc.split(",")))) 
    tes.density  = (float(density))
    tes.pol  = (float(polarize_f))
    tes.recoil  = (float(recoil_f))
    tes.norm_min  = (float(q_range1))
    tes.norm_max  = (float(q_range2))
    tes.dr= (float(d_r))
    tes.r_max  = (float(max))
    tes.r_cut = (float(cut_off))
    
    tes.All_run()
    tes.BFT_smooth()
    
    # spinner = pydom["#pdf .loading"]
    # canvas = pydom["#pdf canvas"][0]
  

    # ctx = prepare_canvas(width, height, canvas)

    console.log("Computing set ...")
    
    
    # figrr, axrr = plt.subplots(2, 2)
    # plt.subplots_adjust(wspace=0.5, hspace=0.5)

    # raw intesity
    xr = tes.tt
    yr_org = tes.intensityRaw
    yr = tes.subtract_bg()


    hover_tool = HoverTool()
    hover_tool.tooltips=None
    TOOLTIPS = [("index", "$index"),("(x,y)", "($x, $y)")]    
    hover_tool.tooltips = TOOLTIPS
    

    p1 = figure(title="Raw",  x_axis_label='2θ/degree',y_axis_label='Intensity', background_fill_color="#fafafa",width=width, height=height)
    p1.add_tools(hover_tool)


    if not (tes.bg_filename == ""):
        p1.line(tes.tt_bg, tes.intensityBG*tes.bg_factor, legend_label="Background", line_color="olivedrab")
        p1.line(xr, yr_org, legend_label="Intensity", line_color="tomato")
    else:
        p1.line(xr, yr_org,line_color="tomato")
    
    
    # raw intesity
    # axrr[0][0].plot(xr, yr)
    # axrr[0][0].set_title('Raw')
    # axrr[0][0].set_xlabel('2θ/degree')   # 1番目にxラベルを追加 ＃単位系帰還と遺憾
    # axrr[0][0].set_ylabel('Intensity')
    
    
    hover_tool2 = HoverTool()
    hover_tool2.tooltips=None
    TOOLTIPS = [("index", "$index"),("(x,y)", "($x, $y)")]    
    hover_tool2.tooltips = TOOLTIPS
    # S(Q), bFTS(Q)
    p2 = figure(title="S(Q), bFTS(Q)", x_range=[0, tes.norm_max],   x_axis_label='Q/Å**-1',y_axis_label='S(Q)', background_fill_color="#fafafa",width=width, height=height)
    p2.add_tools(hover_tool2)
    p2.line(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_bFT[tes.nn_min:]+1, legend_label="bFT",line_color="tomato" )
    p2.line(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_raw[tes.nn_min:]+1, legend_label="raw",line_color="olivedrab")
    p2.line(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_bFT[tes.nn_min:] - tes.iq_interpolate_raw[tes.nn_min:]-2, legend_label="residual",line_color="coral")
    p2.legend.location ="bottom_right" 

    # S(Q), bFTS(Q)
    #  axrr[0][1].set_title('S(Q), bFTS(Q)')
    #  axrr[0][1].plot(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_bFT[tes.nn_min:]+1) # label="bFT-tes raw-2
    #  axrr[0][1].plot(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_raw[tes.nn_min:]+1) # label="raw"
    #  axrr[0][1].plot(tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_bFT-tes.iq_interpolate_raw[tes.nn_min:]-2)  # label=# 残差(residual)　　　"bFT-tes raw-2"
    # labael の付け方が通常と異なる(こちらしか反映されない)
    #  axrr[0][1].legend(["bFT" , "raw", "residual"])
    #  axrr[0][1].set_xlabel('$Q/Å^{{-1}}$')   # 1番目にxラベルを追加 ＃単位系帰還と遺憾
    #  axrr[0][1].set_ylabel('S(Q)')

    hover_tool3 = HoverTool()
    hover_tool3.tooltips=None
    TOOLTIPS = [("index", "$index"),("(x,y)", "($x, $y)")]    
    hover_tool3.tooltips = TOOLTIPS

    # Gr
    p3 = figure(title="Gr", x_range=[0,tes.r_max],  x_axis_label='r/Å',y_axis_label='G(r)', background_fill_color="#fafafa",width=width, height=height)
    #p3 = figure(title="gr",   x_axis_label='r/å',y_axis_label='g(r)', background_fill_color="#fafafa",width=width, height=height)
    p3.add_tools(hover_tool3)
    

    # データ生成
    # xが0〜10の範囲にあるインデックスを抽出
    mask = (tes.rr>= 0) & (tes.rr<= tes.r_max)

    # p3.line(tes.rr[:tes.rmax_pos()], tes._Gr[:tes.rmax_pos()], line_color="tomato" )
    p3.line(tes.rr[mask], tes._Gr[mask], line_color="tomato" )
    
    
    

    # Gr
    #   axrr[1][0].set_title('Gr')
    #   axrr[1][0].plot(tes.rr[:tes.rmax_pos], tes._Gr[:tes.rmax_pos])
    #   axrr[1][0].set_xlabel('$r/Å$')   # 1番目にxラベルを追加 ＃単位系帰還と遺憾
    #   axrr[1][0].set_ylabel('G(r)')

    hover_tool4 = HoverTool()
    hover_tool4.tooltips=None
    TOOLTIPS = [("index", "$index"),("(x,y)", "($x, $y)")]    
    hover_tool4.tooltips = TOOLTIPS

    # Gr(Lorch)
    p4 = figure(title="Gr(Lorch)", x_range=[0,tes.r_max],   x_axis_label='r/Å',y_axis_label='G(r)', background_fill_color="#fafafa",width=width, height=height)
    #p4 = figure(title="Gr(Lorch)",   x_axis_label='r/Å',y_axis_label='G(r)', background_fill_color="#fafafa",width=width, height=height)
    p4.add_tools(hover_tool4)
    p4.line(tes.rr_show_cal()[:tes.rmax_pos()], tes._Gr_Lorch[:tes.rmax_pos()], line_color="tomato" )

    # Gr(Lorch)
    #   axrr[1][1].set_title('Gr(Lorch)')
    #   axrr[1][1].plot(tes.rr_show, tes._Gr_Lorch)
    #   axrr[1][1].set_xlabel('$r/Å$')   # 1番目にxラベルを追加 ＃単位系帰還と遺憾
    #   axrr[1][1].set_ylabel('G(r)')
    document.getElementById("mpl").innerHTML = ""
    document.getElementById("mpl2").innerHTML = ""
    document.getElementById("mpl3").innerHTML = ""
    document.getElementById("mpl4").innerHTML = ""

    
    filepath =  (str(pydom["#file-upload"][0].value))
    basename_without_ext = os.path.splitext(os.path.basename(filepath))[0]
    if "snap\\" in filelabel or "snap/" in filelabel:
        tes.dl_filename   = filelabel.split("\\")[-1]
    else:
        tes.dl_filename = basename_without_ext.split("\\")[-1]


    p1.width = width
    p2.width = width
    p3.width = width
    p4.width = width
    
    p1.height = height
    p2.height = height
    p3.height = height
    p4.height = height

    p_json = json.dumps(json_item(p1, "mpl"))
    Bokeh.embed.embed_item(JSON.parse(p_json))

    p_json = json.dumps(json_item(p2, "mpl2"))
    Bokeh.embed.embed_item(JSON.parse(p_json))
    
    p_json = json.dumps(json_item(p3, "mpl3"))
    Bokeh.embed.embed_item(JSON.parse(p_json))

    p_json = json.dumps(json_item(p4, "mpl4"))
    Bokeh.embed.embed_item(JSON.parse(p_json))


# Because retreiving of a file's ArrayBuffer is an asynchronous process,
# we need to make our function async


def get_bytes_from_file(file):
    # Get the File object's arrayBuffer - just an ordered iterable of the bytes of the file
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer
    array_buf = file.arrayBuffer()

    # Use pyodide's ability to quickly copy the array buffer to a Python 'bytes' object
    # https://pyodide.org/en/stable/usage/api/python-api/ffi.html#pyodide.ffi.JsBuffer.to_bytes
    # https://docs.python.org/3/library/stdtypes.html#bytes-objects
    return array_buf.to_bytes()




async def clicked_dl(event):
    print("clicked_dl")

    checkbox1 = document.getElementById('checkbox1').checked
    checkbox2 = document.getElementById('checkbox2').checked
    checkbox3 = document.getElementById('checkbox3').checked
    checkbox4 = document.getElementById('checkbox4').checked
    checkbox5 = document.getElementById('checkbox5').checked
    checkbox6 = document.getElementById('checkbox6').checked
    checkbox7 = document.getElementById('checkbox7').checked
    checkbox8 = document.getElementById('checkbox8').checked
    checkbox9 = document.getElementById('checkbox9').checked

    checkbox10 = document.getElementById('checkbox10').checked
    checkbox11 = document.getElementById('checkbox11').checked
    checkbox12 = document.getElementById('checkbox12').checked
    checkbox13 = document.getElementById('checkbox13').checked
    checkbox14 = document.getElementById('checkbox14').checked
    checkbox15 = document.getElementById('checkbox15').checked
    checkbox16 = document.getElementById('checkbox16').checked


    


    with zipfile.ZipFile((tes.dl_filename + ".zip"), 'w') as zipf:
        # Gr 
        if checkbox1:

            # データ生成
            # xが0〜r_maxの範囲にあるインデックスを抽出
            mask = (tes.rr>= 0) & (tes.rr<= tes.r_max)

            result = (tes.rr[mask], tes._Gr[mask])
            np.savetxt('G_r.dat',        np.column_stack(result), fmt="%.4f") 
            zipf.write("./G_r.dat", arcname="G_r.dat")
        if checkbox2:
            if type(tes._Gr_bFT[:tes.rmax_pos()]) == np.ndarray:
                np.savetxt('G_r_bft.dat',    np.column_stack((tes.rr[:tes.rmax_pos()], tes._Gr_bFT[:tes.rmax_pos()])), fmt="%.4f") 
                zipf.write("./G_r_bft.dat", arcname="G_r_bft.dat")
        if checkbox3:
            print(checkbox3)
            print(type(tes._Gr_Lorch))    
            if type(tes._Gr_Lorch) == list:
                np.savetxt('G_r_lorch.dat',  np.column_stack((tes.rr_show_cal(), tes._Gr_Lorch)) , fmt="%.4f")
                zipf.write("./G_r_lorch.dat", arcname="G_r_lorch.dat")

        # ggr
        if checkbox4:
            if type(tes._ggr[:tes.rmax_pos()]) == np.ndarray:
                np.savetxt('gg_r.dat',       np.column_stack((tes.rr[:tes.rmax_pos()], tes._ggr[:tes.rmax_pos()])) , fmt="%.4f")
                zipf.write("./gg_r.dat", arcname="gg_r.dat")
        if checkbox5:
            if type(tes._ggr_bFT[:tes.rmax_pos()]) == np.ndarray:
                np.savetxt('gg_r_bft.dat',   np.column_stack((tes.rr[:tes.rmax_pos()] ,tes._ggr_bFT[:tes.rmax_pos()])), fmt="%.4f") 
                zipf.write("./gg_r_bft.dat", arcname="gg_r_bft.dat")
        if checkbox6:
            if type(tes._ggr_Lorch) == np.ndarray:
                np.savetxt('gg_r_lorch.dat', np.column_stack((tes.rr_show_cal(), tes._ggr_Lorch)) , fmt="%.4f")
                zipf.write("./gg_r_lorch.dat", arcname="gg_r_lorch.dat")

        # Tr
        if checkbox7:
            if type(tes._Tr[:tes.rmax_pos()]) == np.ndarray:
                np.savetxt('t_r.dat',        np.column_stack((tes.rr[:tes.rmax_pos()], tes._Tr[:tes.rmax_pos()])) , fmt="%.4f")
                zipf.write("./t_r.dat", arcname="t_r.dat")
        if checkbox8:
            if type(tes.Tr_bFT())    == np.ndarray:
                np.savetxt('t_r_bft.dat',    np.column_stack((tes.rr[:tes.rmax_pos()], tes.Tr_bFT()[:tes.rmax_pos()])), fmt="%.4f") 
                zipf.write("./t_r_bft.dat", arcname="t_r_bft.dat")
        if checkbox9:
            if type(tes._Tr_Lorch) == np.ndarray:
                np.savetxt('t_r_lorch.dat',  np.column_stack((tes.rr_show_cal(), tes._Tr_Lorch)) , fmt="%.4f")
                zipf.write("./t_r_lorch.dat", arcname="t_r_lorch.dat")

        # RDF
        if checkbox10:
            if type(tes._RDF[:tes.rmax_pos()]) == np.ndarray:
                np.savetxt('rdf.dat',  np.column_stack((tes.rr[:tes.rmax_pos()], tes._RDF[:tes.rmax_pos()])), fmt="%.4f") 
                zipf.write("./rdf.dat", arcname="rdf.dat")
        if checkbox11:
            if type(tes.RDF_bFT()) == np.ndarray:
                np.savetxt('rdf_bft.dat',    np.column_stack((tes.rr[:tes.rmax_pos()] ,tes.RDF_bFT()[:tes.rmax_pos()])), fmt="%.4f") 
                zipf.write("./rdf_bft.dat", arcname="rdf_bft.dat")
        if checkbox12:
            if type(tes._RDF_Lorch) == np.ndarray:
                np.savetxt('rdf_lorch.dat',  np.column_stack((tes.rr_show_cal(), tes._RDF_Lorch)) , fmt="%.4f")
                zipf.write("./rdf_lorch.dat", arcname="rdf_lorch.dat")

        # iQ
        if checkbox13:
            if type(tes.iq_interpolate_raw) == np.ndarray:
                np.savetxt('iq.dat', np.column_stack((tes.qq_interpolate[tes.nn_min:],tes.iq_interpolate_raw[tes.nn_min:])), fmt="%.4f")
                zipf.write("./iq.dat", arcname="iq.dat")
        if checkbox14:
            if type(tes.iq_interpolate_bFT) == np.ndarray:
                np.savetxt('iq_bft.dat', np.column_stack((tes.qq_interpolate[tes.nn_min:],tes.iq_interpolate_bFT[tes.nn_min:])), fmt="%.4f")      
                zipf.write("./iq_bft.dat", arcname="iq_bft.dat")
        
        # SQ
        if checkbox15:
            if type(tes.sq[:tes.num_norm_max]) == np.ndarray:
                np.savetxt('sq.dat', np.column_stack((tes.qq[:tes.num_norm_max], tes.sq[:tes.num_norm_max]+1)), fmt="%.4f")
                zipf.write("./sq.dat", arcname="sq.dat")
        if checkbox16:
            if type(tes.iq_interpolate_bFT[tes.nn_min:]) == np.ndarray:
                np.savetxt('./sq_bft.dat', np.column_stack((tes.qq_interpolate[tes.nn_min:], tes.iq_interpolate_bFT[tes.nn_min:]+1)), fmt="%.4f")      
                zipf.write("./sq_bft.dat", arcname="sq_bft.dat")
     
    
    download_file(path= (tes.dl_filename + ".zip"), mime_type="binary")
    



def download_file(path, mime_type):
    name = os.path.basename(path)
    with open(path, "rb") as source:
        data = source.read()

        # Populate the buffer.
        buffer = window.Uint8Array.new(len(data))
        for pos, b in enumerate(data):
            buffer[pos] = b
        details = to_js({"type": mime_type})

        # This is JS specific
        file = window.File.new([buffer], name, details)
        tmp = window.URL.createObjectURL(file)
        dest = document.createElement("a")
        dest.setAttribute("download", name)
        dest.setAttribute("href", tmp)
        dest.click()

