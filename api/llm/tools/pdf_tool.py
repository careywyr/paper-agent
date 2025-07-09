# -*- coding: utf-8 -*-
"""
@file    : pdf_tool.py
@date    : 2025-06-30
@author  : leafw
@reference: https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/multi_column.py
"""
import fitz

def column_boxes(page, footer_margin=50, header_margin=50, no_image_text=True):
    """Determine bboxes which wrap a column."""
    paths = page.get_drawings()
    bboxes = []

    # path rectangles
    path_rects = []

    # image bboxes
    img_bboxes = []

    # bboxes of non-horizontal text
    # avoid when expanding horizontal text boxes
    vert_bboxes = []

    # compute relevant page area
    clip = +page.rect
    clip.y1 -= footer_margin  # Remove footer area
    clip.y0 += header_margin  # Remove header area

    def can_extend(temp, bb, bboxlist):
        """Determines whether rectangle 'temp' can be extended by 'bb'
        without intersecting any of the rectangles contained in 'bboxlist'.

        Items of bboxlist may be None if they have been removed.

        Returns:
            True if 'temp' has no intersections with items of 'bboxlist'.
        """
        for b in bboxlist:
            if not intersects_bboxes(temp, vert_bboxes) and (
                b == None or b == bb or (temp & b).is_empty
            ):
                continue
            return False

        return True

    def in_bbox(bb, bboxes):
        """Return 1-based number if a bbox contains bb, else return 0."""
        for i, bbox in enumerate(bboxes):
            if bb in bbox:
                return i + 1
        return 0

    def intersects_bboxes(bb, bboxes):
        """Return True if a bbox intersects bb, else return False."""
        for bbox in bboxes:
            if not (bb & bbox).is_empty:
                return True
        return False

    def extend_right(bboxes, width, path_bboxes, vert_bboxes, img_bboxes):
        """Extend a bbox to the right page border.

        Whenever there is no text to the right of a bbox, enlarge it up
        to the right page border.

        Args:
            bboxes: (list[IRect]) bboxes to check
            width: (int) page width
            path_bboxes: (list[IRect]) bboxes with a background color
            vert_bboxes: (list[IRect]) bboxes with vertical text
            img_bboxes: (list[IRect]) bboxes of images
        Returns:
            Potentially modified bboxes.
        """
        for i, bb in enumerate(bboxes):
            # do not extend text with background color
            if in_bbox(bb, path_bboxes):
                continue

            # do not extend text in images
            if in_bbox(bb, img_bboxes):
                continue

            # temp extends bb to the right page border
            temp = +bb
            temp.x1 = width

            # do not cut through colored background or images
            if intersects_bboxes(temp, path_bboxes + vert_bboxes + img_bboxes):
                continue

            # also, do not intersect other text bboxes
            check = can_extend(temp, bb, bboxes)
            if check:
                bboxes[i] = temp  # replace with enlarged bbox

        return [b for b in bboxes if b != None]

    def clean_nblocks(nblocks):
        """Do some elementary cleaning."""

        # 1. remove any duplicate blocks.
        blen = len(nblocks)
        if blen < 2:
            return nblocks
        start = blen - 1
        for i in range(start, -1, -1):
            bb1 = nblocks[i]
            bb0 = nblocks[i - 1]
            if bb0 == bb1:
                del nblocks[i]

        # 2. repair sequence in special cases:
        # consecutive bboxes with almost same bottom value are sorted ascending
        # by x-coordinate.
        y1 = nblocks[0].y1  # first bottom coordinate
        i0 = 0  # its index
        i1 = -1  # index of last bbox with same bottom

        # Iterate over bboxes, identifying segments with approx. same bottom value.
        # Replace every segment by its sorted version.
        for i in range(1, len(nblocks)):
            b1 = nblocks[i]
            if abs(b1.y1 - y1) > 10:  # different bottom
                if i1 > i0:  # segment length > 1? Sort it!
                    nblocks[i0 : i1 + 1] = sorted(
                        nblocks[i0 : i1 + 1], key=lambda b: b.x0
                    )
                y1 = b1.y1  # store new bottom value
                i0 = i  # store its start index
            i1 = i  # store current index
        if i1 > i0:  # segment waiting to be sorted
            nblocks[i0 : i1 + 1] = sorted(nblocks[i0 : i1 + 1], key=lambda b: b.x0)
        return nblocks

    # extract vector graphics
    for p in paths:
        path_rects.append(p["rect"].irect)
    path_bboxes = path_rects

    # sort path bboxes by ascending top, then left coordinates
    path_bboxes.sort(key=lambda b: (b.y0, b.x0))

    # bboxes of images on page, no need to sort them
    for item in page.get_images():
        img_bboxes.extend(page.get_image_rects(item[0]))

    # blocks of text on page
    blocks = page.get_text(
        "dict",
        flags=fitz.TEXTFLAGS_TEXT,
        clip=clip,
    )["blocks"]

    # Make block rectangles, ignoring non-horizontal text
    for b in blocks:
        bbox = fitz.IRect(b["bbox"])  # bbox of the block

        # ignore text written upon images
        if no_image_text and in_bbox(bbox, img_bboxes):
            continue

        # confirm first line to be horizontal
        line0 = b["lines"][0]  # get first line
        if line0["dir"] != (1, 0):  # only accept horizontal text
            vert_bboxes.append(bbox)
            continue

        srect = fitz.EMPTY_IRECT()
        for line in b["lines"]:
            lbbox = fitz.IRect(line["bbox"])
            text = "".join([s["text"].strip() for s in line["spans"]])
            if len(text) > 1:
                srect |= lbbox
        bbox = +srect

        if not bbox.is_empty:
            bboxes.append(bbox)

    # 检测是否为双栏布局
    # 计算页面宽度的中点
    page_middle_x = page.rect.width / 2
    
    # 将文本块分为左栏和右栏
    left_column = []
    right_column = []
    
    for bbox in bboxes:
        # 根据bbox的中心点判断其所在栏
        bbox_center_x = (bbox.x0 + bbox.x1) / 2
        if bbox_center_x < page_middle_x:
            left_column.append(bbox)
        else:
            right_column.append(bbox)
    
    # 分别对左栏和右栏按照从上到下的顺序排序
    left_column.sort(key=lambda k: (in_bbox(k, path_bboxes), k.y0))
    right_column.sort(key=lambda k: (in_bbox(k, path_bboxes), k.y0))
    
    # 先左栏后右栏
    bboxes = left_column + right_column

    # Extend bboxes to the right where possible
    bboxes = extend_right(
        bboxes, int(page.rect.width), path_bboxes, vert_bboxes, img_bboxes
    )

    # immediately return of no text found
    if bboxes == []:
        return []

    # --------------------------------------------------------------------
    # Join bboxes to establish some column structure
    # --------------------------------------------------------------------
    # the final block bboxes on page
    nblocks = [bboxes[0]]  # pre-fill with first bbox
    bboxes = bboxes[1:]  # remaining old bboxes

    for i, bb in enumerate(bboxes):  # iterate old bboxes
        check = False  # indicates unwanted joins

        # check if bb can extend one of the new blocks
        for j in range(len(nblocks)):
            nbb = nblocks[j]  # a new block

            # never join across columns
            if bb == None or nbb.x1 < bb.x0 or bb.x1 < nbb.x0:
                continue

            # never join across different background colors
            if in_bbox(nbb, path_bboxes) != in_bbox(bb, path_bboxes):
                continue

            temp = bb | nbb  # temporary extension of new block
            check = can_extend(temp, nbb, nblocks)
            if check == True:
                break

        if not check:  # bb cannot be used to extend any of the new bboxes
            nblocks.append(bb)  # so add it to the list
            j = len(nblocks) - 1  # index of it
            temp = nblocks[j]  # new bbox added

        # check if some remaining bbox is contained in temp
        check = can_extend(temp, bb, bboxes)
        if check == False:
            nblocks.append(bb)
        else:
            nblocks[j] = temp
        bboxes[i] = None

    # do some elementary cleaning
    nblocks = clean_nblocks(nblocks)

    # return identified text bboxes
    return nblocks

def load_pdf(file_path: str) -> list:
    """兼容旧接口，使用新的load_pdf_with_tables实现"""
    return load_pdf_with_tables(file_path)

def load_pdf_with_tables(file_path: str) -> list:
    """
    加载PDF文件并提取所有页面的内容，包括文本和表格
    
    Args:
        file_path: PDF文件路径
        
    Returns:
        所有页面的内容列表，每个页面是一个列表，包含该页面的文本和表格内容
    """
    # 打开文档
    doc = fitz.open(file_path)
    all_content = []
    
    # 处理每一页
    for page_num in range(len(doc)):
        # 获取指定页面
        page = doc[page_num]
        
        # 移除任何几何问题
        page.wrap_contents()
        
        # 获取表格信息
        table_finder = page.find_tables()
        tables = table_finder.tables if hasattr(table_finder, 'tables') else []
        table_bboxes = []
        table_objects = {}
        
        # 将表格的边界框存储起来，并建立边界框到表格对象的映射
        for table in tables:
            table_bbox = fitz.Rect(table.bbox)
            table_bbox_irect = fitz.IRect(table_bbox)
            table_bboxes.append(table_bbox_irect)
            # 将IRect转换为元组(x0, y0, x1, y1)作为字典键
            table_key = (table_bbox_irect.x0, table_bbox_irect.y0, table_bbox_irect.x1, table_bbox_irect.y1)
            table_objects[table_key] = table
        
        # 合并相邻的表格边界框
        merged_table_bboxes = []
        if len(table_bboxes) > 0:
            # 按y坐标排序表格边界框
            sorted_bboxes = sorted(table_bboxes, key=lambda b: b.y0)
            current_merged = sorted_bboxes[0]
            
            for i in range(1, len(sorted_bboxes)):
                current = sorted_bboxes[i]
                # 如果当前表格与合并表格在垂直方向上接近（小于20像素），则合并它们
                if abs(current.y0 - current_merged.y1) < 20:
                    current_merged = fitz.IRect(
                        min(current_merged.x0, current.x0),
                        current_merged.y0,
                        max(current_merged.x1, current.x1),
                        current.y1
                    )
                else:
                    merged_table_bboxes.append(current_merged)
                    current_merged = current
            
            merged_table_bboxes.append(current_merged)
        else:
            merged_table_bboxes = table_bboxes
        
        # 获取文本边界框
        bboxes = column_boxes(page)
        
        # 创建结果列表
        page_content = []
        processed_tables = set()  # 使用集合来存储已经处理过的表格
        
        # 处理每个边界框
        for i, bbox in enumerate(bboxes):
            # 检查是否与任何表格重叠
            is_table = False
            table_content = None
            overlapping_table_bbox = None
            
            # 检查与合并后的表格边界框的重叠
            for table_bbox in merged_table_bboxes:
                # 计算重叠面积比例
                intersection = bbox & table_bbox
                if not intersection.is_empty:
                    overlap_ratio = intersection.get_area() / bbox.get_area()
                    # 如果重叠面积超过边界框面积的30%，则认为是表格
                    if overlap_ratio > 0.3:
                        is_table = True
                        overlapping_table_bbox = table_bbox
                        break
            
            # 如果是表格且这个表格还没有被处理过
            if is_table and overlapping_table_bbox is not None:
                table_key = (overlapping_table_bbox.x0, overlapping_table_bbox.y0, 
                            overlapping_table_bbox.x1, overlapping_table_bbox.y1)
                
                if table_key not in processed_tables:
                    try:
                        # 尝试获取表格对象并转换为pandas DataFrame
                        if table_key in table_objects:
                            table = table_objects[table_key]
                            try:
                                table_content = table.to_pandas()
                            except Exception as e:
                                print(f"表格转换失败: {e}")
                                # 如果转换失败，直接使用文本
                                table_content = page.get_text("text", clip=overlapping_table_bbox)
                        else:
                            # 直接从页面提取表格区域的文本
                            table_content = page.get_text("text", clip=overlapping_table_bbox)
                        
                        processed_tables.add(table_key)
                    except Exception as e:
                        print(f"处理表格时出错: {e}")
                        is_table = False
            
            if is_table and table_content is not None:
                # 添加表格内容
                page_content.append({
                    'type': 'table',
                    'content': table_content,
                    'bbox': bbox,
                    'index': i,
                    'page': page_num
                })
            else:
                # 如果不是表格，添加文本内容
                text_in_bbox = page.get_text("text", clip=bbox)
                page_content.append({
                    'type': 'text',
                    'content': text_in_bbox,
                    'bbox': bbox,
                    'index': i,
                    'page': page_num
                })
        
        all_content.append(page_content)
    
    return all_content

# 示例用法
if __name__ == "__main__":
    filename = "/Users/leafw/Zotero/storage/9978FXRZ/Maragheh 等 - 2025 - ARAG Agentic Retrieval Augmented Generation for Personalized Recommendation.pdf"
    
    # 提取全部内容
    all_contents = load_pdf_with_tables(filename)
    
    # 指定要打印的页码
    page_to_print = 3
    if 0 <= page_to_print < len(all_contents):
        page_contents = all_contents[page_to_print]
        print(f"\n打印第 {page_to_print} 页的内容:")
        
        # 打印提取的内容
        for i, content in enumerate(page_contents):
            print(f"\n内容 #{i} ({content['type']})")
            if content['type'] == 'table':
                print("表格内容:")
                print(content['content'])
            else:
                print("文本内容:")
                print(content['content'])
    else:
        print(f"页码 {page_to_print} 超出范围，文档共有 {len(all_contents)} 页")
