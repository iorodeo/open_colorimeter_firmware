from adafruit_bitmap_font import bitmap_font

fontname = 'Hack-Bold'
#fontname = 'FiraCode-Bold'
font_14pt = bitmap_font.load_font(f'/assets/{fontname}-14.pcf')
font_10pt = bitmap_font.load_font(f'/assets/{fontname}-10.pcf')

#print(f'14pt bbox = {font_14pt.get_bounding_box()}')
#print(f'10pt bbox = {font_10pt.get_bounding_box()}')
