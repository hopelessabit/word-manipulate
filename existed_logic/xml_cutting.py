# -*- coding: utf-8 -*-
"""
xml_cutting.py
--------------
Script xử lý 1 file đề gốc (TOAN-11_C4_B1_TEST-01.docx...) để tách thành:
 - DE_<tên_gốc>.docx  : chỉ còn phần ĐỀ
 - GIAI_<tên_gốc>.docx: chỉ còn phần LỜI GIẢI

Đồng thời:
 - Cắt bỏ khối Shape rác ở đầu (ảnh, watermark...) nhưng
   KHÔNG làm mất thông tin section (sectPr), để tránh lỗi
   khi merge bằng docxcompose.
"""

from docx import Document
import os
import copy
import re
from typing import List


# ================== HÀM HỖ TRỢ CHUNG ================== #

def get_full_text(element) -> str:
    """
    Lấy toàn bộ text (gộp từ các run) bên trong 1 element (paragraph / table...).
    Trả về dạng UPPER để dễ tìm kiếm.
    """
    texts = []
    for node in element.iter():
        if node.text:
            texts.append(node.text)
    return "".join(texts).upper()


# ================== HÀM XỬ LÝ PARAGRAPH ĐẦU ================== #

def clean_first_paragraph_deeply(doc: Document) -> None:
    """
    Xóa paragraph đầu chứa Shape rác.
    
    - Nếu paragraph đầu chứa <w:sectPr> (thông tin section của document)
      thì KHÔNG xóa cả paragraph, chỉ xóa nội dung rác bên trong để
      tránh làm document mất section (gây lỗi cho docxcompose sau này).
    - Nếu không có sectPr -> xóa luôn paragraph đầu như logic cũ.
    """
    body = doc.element.body

    if len(body) == 0:
        return

    first_p = body[0]

    # Chỉ quan tâm khi nó là paragraph <w:p>
    if not first_p.tag.endswith('p'):
        return

    # Trong python-docx, element.xml là chuỗi XML
    xml_str = first_p.xml

    # Nếu paragraph này chứa w:sectPr -> KHÔNG được remove() cả node
    if "w:sectPr" in xml_str:
        print("  [!] Paragraph đầu chứa <w:sectPr>, sẽ GIỮ lại để tránh mất section.")
        # Dù giữ paragraph, ta vẫn có thể dọn nội dung rác (run, drawing...) bên trong
        # nhưng phải giữ lại node sectPr
        children = list(first_p)

        # Tìm và gom các rId để gỡ bỏ relationship
        rids = re.findall(r'(?:r:id|r:embed)="([^"]+)"', xml_str)
        if rids:
            print(f"  [-] Phát hiện {len(rids)} liên kết ngầm (Ảnh/Shape) trong paragraph chứa sectPr. Đang gỡ bỏ...")
            for rid in rids:
                try:
                    if rid in doc.part.rels:
                        doc.part.rels.pop(rid)
                except Exception as e:
                    print(f"  [!] Không thể xóa rId {rid}: {e}")

        # Xóa các child không phải sectPr (giữ lại sectPr để document còn section)
        for child in children:
            if child.tag.endswith("sectPr"):
                continue  # giữ lại
            first_p.remove(child)

        print("  [x] Đã dọn rác trong paragraph đầu (giữ lại sectPr).")
        return

    # Trường hợp bình thường: paragraph đầu không chứa sectPr -> xóa như cũ
    # 1) Tìm các rId liên quan để gỡ bỏ relationships
    rids = re.findall(r'(?:r:id|r:embed)="([^"]+)"', xml_str)
    if rids:
        print(f"  [-] Phát hiện {len(rids)} liên kết ngầm (Ảnh/Shape) trong header. Đang gỡ bỏ...")
        for rid in rids:
            try:
                if rid in doc.part.rels:
                    doc.part.rels.pop(rid)
            except Exception as e:
                print(f"  [!] Cảnh báo: Không thể xóa rId {rid}: {e}")

    # 2) Xóa luôn paragraph đầu
    body.remove(first_p)
    print("  [x] Đã cắt bỏ khối Shape đầu tiên (không chứa sectPr) thành công.")


# ================== HÀM XỬ LÝ FILE ĐỀ ================== #

def build_de_file(master_doc: Document, output_path: str) -> None:
    """
    Tạo file ĐỀ:
      - Copy từ file gốc
      - Xóa Shape đầu
      - Giữ từ đầu -> trước dòng 'HƯỚNG DẪN GIẢI CHI TIẾT'
    """
    print("--- Đang tạo file ĐỀ ---")
    doc_de = copy.deepcopy(master_doc)

    # 1. Cắt Shape đầu và dọn rác
    clean_first_paragraph_deeply(doc_de)

    # 2. Xóa phần lời giải (giữ phần ĐỀ)
    body_de = doc_de.element.body
    found_split = False
    to_delete: List[object] = []

    for element in body_de.iterchildren():
        if found_split:
            to_delete.append(element)
            continue

        if element.tag.endswith('p') or element.tag.endswith('tbl'):
            xml_text = get_full_text(element)
            if "HƯỚNG DẪN GIẢI CHI TIẾT" in xml_text:
                found_split = True
                # Xóa luôn dòng này khỏi file đề
                to_delete.append(element)

    if not found_split:
        print("  [!] Không tìm thấy 'HƯỚNG DẪN GIẢI CHI TIẾT' trong file. File ĐỀ có thể vẫn chứa cả lời giải.")

    for el in to_delete:
        body_de.remove(el)

    doc_de.save(output_path)
    print(f"  => Đã lưu file ĐỀ: {output_path}")


# ================== HÀM XỬ LÝ FILE GIẢI ================== #

def build_giai_file(master_doc: Document, output_path: str) -> None:
    """
    Tạo file GIẢI:
      - Copy từ file gốc
      - Xóa Shape đầu
      - GIỮ: Header (dòng 'BÀI:' hoặc 'ĐỀ TEST')
      - XÓA: Đoạn nội dung ĐỀ ở giữa
      - GIỮ: phần từ 'HƯỚNG DẪN GIẢI CHI TIẾT' trở đi
    """
    print("--- Đang tạo file GIẢI ---")
    doc_giai = copy.deepcopy(master_doc)

    # 1. Cắt Shape đầu và dọn rác
    clean_first_paragraph_deeply(doc_giai)

    # 2. Xác định vùng cần xóa (phần ĐỀ)
    body_giai = doc_giai.element.body
    children = list(body_giai.iterchildren())

    start_delete_idx = -1
    end_delete_idx = -1

    for i, element in enumerate(children):
        xml_text = get_full_text(element)

        # Tìm dòng chứa "BÀI:" hoặc "ĐỀ TEST" để xác định mốc bắt đầu xóa SAU nó
        if "BÀI:" in xml_text or "ĐỀ TEST" in xml_text:
            start_delete_idx = i + 1  # xóa bắt đầu từ sau header

        # Tìm dòng "HƯỚNG DẪN GIẢI CHI TIẾT" để dừng xóa TRƯỚC nó
        if "HƯỚNG DẪN GIẢI CHI TIẾT" in xml_text:
            end_delete_idx = i
            break

    if start_delete_idx > 0 and end_delete_idx > start_delete_idx:
        print(f"  [i] Xóa nội dung đề từ index {start_delete_idx} đến {end_delete_idx - 1}")
        nodes_to_remove = children[start_delete_idx:end_delete_idx]
        for node in nodes_to_remove:
            body_giai.remove(node)
    else:
        print("  [!] Không xác định được vùng cần xóa cho file GIẢI (có thể cấu trúc file khác).")

    doc_giai.save(output_path)
    print(f"  => Đã lưu file GIẢI: {output_path}")


# ================== HÀM CHÍNH XỬ LÝ 1 FILE ================== #

def process_exam_file(input_path: str) -> None:
    """
    Xử lý 1 file đề gốc:
       - Sinh ra DE_<tên_gốc>.docx
       - Sinh ra GIAI_<tên_gốc>.docx
    """
    filename = os.path.basename(input_path)
    base_name = os.path.splitext(filename)[0]
    dir_name = os.path.dirname(input_path) or "."

    path_de = os.path.join(dir_name, f"DE_{base_name}.docx")
    path_giai = os.path.join(dir_name, f"GIAI_{base_name}.docx")

    print(f"\n>>> Đang xử lý file gốc: {filename}")

    # Load file gốc
    try:
        master_doc = Document(input_path)
    except Exception as e:
        print(f"[LỖI] Không mở được file '{input_path}': {e}")
        return

    # Tạo file ĐỀ
    build_de_file(master_doc, path_de)

    # Tạo file GIẢI
    build_giai_file(master_doc, path_giai)


# ================== MAIN ================== #

if __name__ == "__main__":
    # ĐIỀN TÊN FILE CỦA BẠN Ở ĐÂY
    input_file = "TOAN-11_C4_B2_ĐỀ-TEST-01_HAI-DUONG-THANG-SONG-SONG_HDG.docx"

    if os.path.exists(input_file):
        process_exam_file(input_file)
    else:
        print(f"[LỖI] Không tìm thấy file đầu vào: {input_file}")
